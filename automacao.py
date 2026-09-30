import threading
import time
import traceback
from datetime import datetime
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    StaleElementReferenceException,
    ElementClickInterceptedException,
    TimeoutException,
    WebDriverException,
)

# ============================================================
# CONFIGURAÇÕES
# ============================================================
URL_LOGIN      = "https://e-saudesp-telemedicina.prefeitura.sp.gov.br/e-saudesp"
SINAL_LOGIN    = (By.XPATH, "//app-nav//button[contains(., 'Início')]")
MENU_PACIENTES = (By.XPATH, "//app-nav//button[contains(., 'Pacientes')]")
OPCAO_TODAS_UNIDADES       = (By.XPATH, "//mat-radio-button[contains(., 'Buscar em todas as unidades')]")
OPCAO_TODAS_UNIDADES_INPUT = (By.XPATH, "//mat-radio-button[contains(., 'Buscar em todas as unidades')]//input")


def campo_por_texto(texto):
    """Localizador do campo que tem esse texto: escrito na tela (rótulo, ex.: 'PROCURAR POR CPF')
    ou dentro do campo (placeholder). Não usa o id (mat-input-0...), que muda a cada tela."""
    return (By.XPATH,
            f"(//mat-form-field[contains(., '{texto}')]//input"
            f" | //input[contains(@placeholder, '{texto}') or contains(@aria-label, '{texto}')])[1]")


# Painel de filtros da tela PESSOAS: "Procurar por CPF", "Procurar por CNS", "Procurar por tags"
CAMPO_CNS        = campo_por_texto("CNS")
CAMPO_CPF        = campo_por_texto("CPF")
# A tela Pessoas NÃO tem campo de nome; se um dia tiver, ele é preenchido também (sem esperar por ele)
CAMPO_NOME       = campo_por_texto("Nome do paciente")

# Registro dos passos (para descobrir onde travou). NUNCA grava CNS, CPF ou nome.
ARQUIVO_LOG = Path(__file__).parent / "automacao_log.txt"
BOTAO_FILTRAR    = (By.XPATH, "//button[contains(., 'Filtrar')]")
CARTOES_PACIENTE = (By.XPATH, "//app-person//app-infinite-scroll//mk-card")
CARREGANDO       = (By.CSS_SELECTOR, "mat-spinner, mat-progress-spinner, mat-progress-bar")

TEMPO_LOGIN      = 300   # até 5 minutos para a pessoa fazer o login
TEMPO_TELA       = 30    # até 30 segundos para cada tela carregar
TEMPO_CARREGANDO = 3     # até 3 segundos esperando rodinhas/barras sumirem
PAUSA            = 1.0   # margem de segurança depois de cada tela
ESTABILIDADE     = 2     # o cartão precisa ficar 2 s sem mudar
ESPERA_MESMO_RESULTADO = 5   # se o cartão não mudar em 5 s, já era a gestante certa

JS_CLICAVEIS = """
const cartao = arguments[0];
const encontrados = [];
for (const el of [cartao, ...cartao.querySelectorAll('*')]) {
    const estilo = getComputedStyle(el);
    if (estilo.cursor !== 'pointer') continue;
    if (el.offsetWidth === 0 || el.offsetHeight === 0) continue;
    if (el.closest('button, a')) continue;
    encontrados.push(el);
}
return encontrados;
"""

# ============================================================
# ESTADO (fica guardado entre um clique e outro da janela)
# ============================================================
driver = None                 # o Chrome já logado
trava  = threading.Lock()     # impede duas buscas ao mesmo tempo
status = ""                   # o que a automação está fazendo (a janela principal mostra)


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================
def navegador_aberto():
    if driver is None:
        return False
    try:
        driver.title
        return True
    except WebDriverException:
        return False


def esperar_tela_carregar():
    WebDriverWait(driver, TEMPO_TELA).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )

    def indicadores_visiveis(d):
        visiveis = []
        for elemento in d.find_elements(*CARREGANDO):
            try:
                if elemento.is_displayed():
                    visiveis.append(elemento)
            except StaleElementReferenceException:
                pass
        return visiveis

    try:
        WebDriverWait(driver, TEMPO_CARREGANDO).until(
            lambda d: len(indicadores_visiveis(d)) == 0
        )
    except TimeoutException:
        pass

    time.sleep(PAUSA)


def rolar_ate(elemento):
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elemento)
    time.sleep(0.3)


def clicar(elemento):
    rolar_ate(elemento)
    try:
        elemento.click()
    except ElementClickInterceptedException:
        driver.execute_script("arguments[0].click();", elemento)


def cartoes_visiveis():
    visiveis = []
    for c in driver.find_elements(*CARTOES_PACIENTE):
        try:
            if c.is_displayed():
                visiveis.append(c)
        except StaleElementReferenceException:
            pass
    return visiveis


def registrar(passo):
    """Acrescenta uma linha no automacao_log.txt com a hora. Nunca coloque dados da paciente aqui."""
    try:
        with open(ARQUIVO_LOG, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now():%Y-%m-%d %H:%M:%S}  {passo}\n")
    except OSError:
        pass                         # o log nunca pode derrubar a automação


def descrever(campo):
    """id e placeholder do campo: ajuda a ver no log SE a automação achou o campo certo."""
    try:
        return f"id={campo.get_attribute('id')} placeholder={campo.get_attribute('placeholder')!r}"
    except WebDriverException:
        return "?"


def preencher(nome_campo, localizador, texto, obrigatorio=True):
    """Clica no campo, apaga o que tinha e digita o texto (vazio = só apaga).
    Apagar é importante: senão sobra o CPF/CNS da busca anterior e o filtro erra.
    obrigatorio=True : espera o campo aparecer (até 30 s); se não aparecer, é erro.
    obrigatorio=False: NÃO espera; se o campo não existe nesta tela, segue sem ele."""
    if obrigatorio:
        try:
            campo = WebDriverWait(driver, TEMPO_TELA).until(EC.element_to_be_clickable(localizador))
        except TimeoutException:
            registrar(f"ERRO: campo {nome_campo} não encontrado em {TEMPO_TELA} s")
            raise
    else:
        visiveis = [c for c in driver.find_elements(*localizador) if c.is_displayed()]
        if not visiveis:
            registrar(f"campo {nome_campo} não existe nesta tela (seguindo sem ele)")
            return
        campo = visiveis[0]
    registrar(f"campo {nome_campo} encontrado: {descrever(campo)}")

    if not texto and not (campo.get_attribute("value") or "").strip():
        registrar(f"campo {nome_campo} já estava vazio")
        return                       # nada para limpar: nem clica
    clicar(campo)
    campo.send_keys(Keys.CONTROL, "a")
    if texto:
        campo.send_keys(texto)
        registrar(f"campo {nome_campo} preenchido")
    else:
        campo.send_keys(Keys.DELETE)
        registrar(f"campo {nome_campo} limpo")


def fechar_abas_extras(aba_principal):
    for aba in driver.window_handles:
        if aba != aba_principal:
            driver.switch_to.window(aba)
            driver.close()
    driver.switch_to.window(aba_principal)


# ============================================================
# ETAPAS 1 e 2: abrir o Chrome e esperar o login
# ============================================================
def abrir_e_esperar_login():
    global driver, status
    status = "Abrindo o e-Saúde no Chrome..."
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get(URL_LOGIN)
    esperar_tela_carregar()

    status = "Faça o login no Chrome (até 5 minutos)..."
    WebDriverWait(driver, TEMPO_LOGIN).until(
        EC.visibility_of_element_located(SINAL_LOGIN)
    )
    esperar_tela_carregar()


# ============================================================
# ETAPAS 3 a 8: buscar a gestante e abrir
#   - com CNS: busca só pelo CNS (o CPF fica vazio)
#   - sem CNS: busca pelo CPF (a tela Pessoas só tem CPF, CNS e tags)
# ============================================================
def buscar_paciente(cns="", cpf="", nome=""):
    # Etapa 3: clicar em Pacientes
    botao = WebDriverWait(driver, TEMPO_TELA).until(
        EC.element_to_be_clickable(MENU_PACIENTES)
    )
    clicar(botao)
    esperar_tela_carregar()
    registrar("etapa 3: menu Pacientes clicado")

    # Etapa 4: garantir "Buscar em todas as unidades" marcado
    opcao = WebDriverWait(driver, TEMPO_TELA).until(
        EC.presence_of_element_located(OPCAO_TODAS_UNIDADES_INPUT)
    )
    if not opcao.is_selected():
        clicar(driver.find_element(*OPCAO_TODAS_UNIDADES))
        esperar_tela_carregar()
        registrar("etapa 4: 'Buscar em todas as unidades' marcado agora")
    else:
        registrar("etapa 4: 'Buscar em todas as unidades' já estava marcado")

    # Etapas 5 e 6: primeiro LIMPA os campos que não serão usados, e por último
    # digita a busca (como antes: o que foi digitado por último vai direto para o Filtrar)
    #   com CNS -> busca pelo CNS | sem CNS -> busca pelo CPF (e pelo nome, se a tela tiver esse campo)
    if cns:
        registrar("busca pelo CNS")
        preencher("Nome", CAMPO_NOME, "", obrigatorio=False)
        preencher("CPF", CAMPO_CPF, "", obrigatorio=False)
        preencher("CNS", CAMPO_CNS, cns)
    else:
        registrar("busca pelo CPF")
        preencher("CNS", CAMPO_CNS, "", obrigatorio=False)
        preencher("Nome", CAMPO_NOME, nome, obrigatorio=False)
        preencher("CPF", CAMPO_CPF, cpf)
    time.sleep(PAUSA)

    # Etapa 7: clicar em Filtrar (com a "foto" do cartão antes)
    filtrar = WebDriverWait(driver, TEMPO_TELA).until(
        EC.element_to_be_clickable(BOTAO_FILTRAR)
    )
    cartoes_antes = cartoes_visiveis()
    texto_antigo  = cartoes_antes[0].text if cartoes_antes else None
    clicar(filtrar)
    momento_filtro = time.time()
    registrar(f"etapa 7: Filtrar clicado ({len(cartoes_antes)} cartão(ões) na tela antes)")

    # Etapa 8: esperar o resultado ficar estável
    estado = {"texto": None, "desde": None}

    def resultado_pronto(d):
        cartoes = cartoes_visiveis()
        if not cartoes:
            estado["texto"], estado["desde"] = None, None
            return False
        primeiro = cartoes[0]
        try:
            texto = primeiro.text
        except StaleElementReferenceException:
            return False
        agora = time.time()
        if texto != estado["texto"]:
            estado["texto"], estado["desde"] = texto, agora
            return False
        if agora - estado["desde"] < ESTABILIDADE:
            return False
        if texto_antigo is None or texto != texto_antigo:
            return primeiro
        if agora - momento_filtro >= ESPERA_MESMO_RESULTADO:
            return primeiro
        return False

    try:
        WebDriverWait(driver, TEMPO_TELA).until(resultado_pronto)
    except TimeoutException:
        registrar(f"ERRO etapa 8: nenhum resultado estável em {TEMPO_TELA} s "
                  f"({len(cartoes_visiveis())} cartão(ões) na tela)")
        raise
    esperar_tela_carregar()
    paciente = WebDriverWait(driver, TEMPO_TELA).until(resultado_pronto)
    rolar_ate(paciente)
    registrar(f"etapa 8: resultado estável ({len(cartoes_visiveis())} cartão(ões) na tela)")

    # Etapa 8: clicar no elemento certo do cartão (o que tem a "mãozinha")
    aba_principal  = driver.current_window_handle
    endereco_antes = driver.current_url

    def tela_mudou():
        return driver.current_url != endereco_antes or len(cartoes_visiveis()) == 0

    clicaveis = driver.execute_script(JS_CLICAVEIS, paciente)
    registrar(f"etapa 8: {len(clicaveis)} elemento(s) com a 'mãozinha' no cartão")
    for numero, el in enumerate(clicaveis, start=1):
        try:
            rolar_ate(el)
            ActionChains(driver).move_to_element(el).click().perform()
            esperar_tela_carregar()
            fechar_abas_extras(aba_principal)
        except StaleElementReferenceException:
            registrar(f"  clique {numero}: elemento sumiu antes do clique")
        mudou = tela_mudou()
        registrar(f"  clique {numero}: abriu a paciente? {'SIM' if mudou else 'não'}")
        if mudou:
            return True

    # nenhum elemento com "mãozinha" abriu: tenta clicar no próprio cartão
    try:
        rolar_ate(paciente)
        ActionChains(driver).move_to_element(paciente).click().perform()
        esperar_tela_carregar()
        fechar_abas_extras(aba_principal)
    except (StaleElementReferenceException, WebDriverException):
        pass
    mudou = tela_mudou()
    registrar(f"  clique no próprio cartão: abriu a paciente? {'SIM' if mudou else 'não'}")
    return mudou


# ============================================================
# EXECUÇÃO (roda em segundo plano)
# ============================================================
def executar(cns, cpf="", nome=""):
    global status
    with trava:
        try:
            if not navegador_aberto():
                abrir_e_esperar_login()
            registrar("===== nova busca =====")
            if cns:
                status = "Buscando a gestante no e-Saúde (pelo CNS)..."
            else:
                status = "Buscando a gestante no e-Saúde (pelo CPF)..."
            if buscar_paciente(cns, cpf, nome):
                status = "Gestante aberta no e-Saúde."
            else:
                status = "Gestante encontrada, mas não consegui abrir: clique no cartão dela no Chrome."
        except Exception as erro:
            # só o tipo do erro: nunca mostra CNS ou nome da paciente
            status = f"Erro na automação: {type(erro).__name__}. Clique na gestante de novo."
            registrar("ERRO:\n" + traceback.format_exc())


# ============================================================
# PORTA DE ENTRADA: chamada pelo principal.py no clique da gestante
# ============================================================
def limpar(valor):
    """Tira espaços e trata '—' / 'None' como vazio."""
    valor = str(valor or "").strip()
    return "" if valor in ("—", "None") else valor


def iniciar(cns, cpf="", nome=""):
    """Com CNS: busca pelo CNS. Sem CNS: busca pelo CPF.
    Devolve False se ainda estiver buscando a gestante anterior; True nos outros casos."""
    cns, cpf, nome = limpar(cns), limpar(cpf), limpar(nome)
    if not cns and not cpf:
        return True                  # sem CNS e sem CPF: nada a buscar
    if trava.locked():
        return False                 # ainda buscando a anterior
    threading.Thread(target=executar, args=(cns, cpf, nome), daemon=True).start()
    return True


# ============================================================
# FECHAR: chamada quando a janela principal é fechada
# ============================================================
def fechar():
    global driver
    if driver is not None:
        try:
            driver.quit()            # fecha o Chrome aberto pela automação
        except Exception:
            pass
        driver = None
