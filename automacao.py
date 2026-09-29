import threading
import time

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
CAMPO_CNS        = (By.XPATH, "//mat-form-field[contains(., 'CNS')]//input")
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
# ETAPAS 3 a 8: buscar a gestante pelo CNS e abrir
# ============================================================
def buscar_paciente(cns):
    # Etapa 3: clicar em Pacientes
    botao = WebDriverWait(driver, TEMPO_TELA).until(
        EC.element_to_be_clickable(MENU_PACIENTES)
    )
    clicar(botao)
    esperar_tela_carregar()

    # Etapa 4: garantir "Buscar em todas as unidades" marcado
    opcao = WebDriverWait(driver, TEMPO_TELA).until(
        EC.presence_of_element_located(OPCAO_TODAS_UNIDADES_INPUT)
    )
    if not opcao.is_selected():
        clicar(driver.find_element(*OPCAO_TODAS_UNIDADES))
        esperar_tela_carregar()

    # Etapas 5 e 6: rolar até o campo e colar o CNS
    campo_cns = WebDriverWait(driver, TEMPO_TELA).until(
        EC.element_to_be_clickable(CAMPO_CNS)
    )
    clicar(campo_cns)
    campo_cns.send_keys(Keys.CONTROL, "a")
    campo_cns.send_keys(cns)
    time.sleep(PAUSA)

    # Etapa 7: clicar em Filtrar (com a "foto" do cartão antes)
    filtrar = WebDriverWait(driver, TEMPO_TELA).until(
        EC.element_to_be_clickable(BOTAO_FILTRAR)
    )
    cartoes_antes = cartoes_visiveis()
    texto_antigo  = cartoes_antes[0].text if cartoes_antes else None
    clicar(filtrar)
    momento_filtro = time.time()

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

    WebDriverWait(driver, TEMPO_TELA).until(resultado_pronto)
    esperar_tela_carregar()
    paciente = WebDriverWait(driver, TEMPO_TELA).until(resultado_pronto)
    rolar_ate(paciente)

    # Etapa 8: clicar no elemento certo do cartão (o que tem a "mãozinha")
    aba_principal  = driver.current_window_handle
    endereco_antes = driver.current_url

    def tela_mudou():
        return driver.current_url != endereco_antes or len(cartoes_visiveis()) == 0

    for el in driver.execute_script(JS_CLICAVEIS, paciente):
        try:
            rolar_ate(el)
            ActionChains(driver).move_to_element(el).click().perform()
            esperar_tela_carregar()
            fechar_abas_extras(aba_principal)
        except StaleElementReferenceException:
            pass
        if tela_mudou():
            break


# ============================================================
# EXECUÇÃO (roda em segundo plano)
# ============================================================
def executar(cns):
    global status
    with trava:
        try:
            if not navegador_aberto():
                abrir_e_esperar_login()
            status = "Buscando a gestante no e-Saúde..."
            buscar_paciente(cns)
            status = "Gestante aberta no e-Saúde."
        except Exception as erro:
            # só o tipo do erro: nunca mostra CNS ou nome da paciente
            status = f"Erro na automação: {type(erro).__name__}. Clique na gestante de novo."


# ============================================================
# PORTA DE ENTRADA: chamada pelo principal.py no clique da gestante
# ============================================================
def iniciar(cns):
    """Devolve False se ainda estiver buscando a gestante anterior; True nos outros casos."""
    cns = str(cns or "").strip()
    if not cns or cns in ("—", "None"):
        return True                  # gestante sem CNS: nada a buscar
    if trava.locked():
        return False                 # ainda buscando a anterior
    threading.Thread(target=executar, args=(cns,), daemon=True).start()
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
