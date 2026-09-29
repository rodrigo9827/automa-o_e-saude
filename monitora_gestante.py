import csv
from datetime import datetime, timedelta
from pathlib import Path

# ============================================================
# ONDE OS CSVs FICAM
# Se a pasta C:\dados existir, os arquivos vão para lá (junto dos outros dados).
# Se não existir, ficam na mesma pasta deste .py.
# ============================================================
PASTA_DADOS = Path(r"C:\dados")
PASTA = PASTA_DADOS if PASTA_DADOS.is_dir() else Path(__file__).parent

ARQUIVO_MONITORAMENTO = PASTA / "stg.Monitora_Gestante.csv"
ARQUIVO_BUSCA_ATIVA   = PASTA / "stg.Busca_Ativa.csv"
ARQUIVO_ADM           = PASTA / "stg.Monitora_Gestante_Adm.csv"

# Colunas do CSV de monitoramento (Finalizar Atendimento)
CAMPOS_MONITORAMENTO = [
    "data_hora_modificacao",
    "enfermeira",
    "teleoperador",
    "cns",
    "data_contato",
    "numero",
    "conseguiu_contato",
    "motivo_sem_contato",
    "classificacao",
    "tratamento_sifilis",
    "gestante_risco",
    "pre_natal",
    "nasceu_vivo",
    "local_parto",
    "outro_local",
    "bebe_risco",
    "obito_neonatal",
    "obito_materno",
    "houve_violencia",
    "tipo_violencia",
    "tipo_parto",
    "risco_gestacional",
    "qual_risco",
    "observacoes",
]

# Colunas do CSV de busca ativa (Registrar Busca Ativa)
CAMPOS_BUSCA_ATIVA = [
    "data_hora_modificacao",
    "enfermeira",
    "gestante",
    "cns",
    "data_contato",
    "ig_semanas",
    "data_retorno",
    "alto_risco",
    "observacoes",
    "gestante_gestante",     # classificação da gestante (Sim = marcado)
    "gestante_puerpera",
    "gestante_aborto",
]

# Colunas do CSV administrativo: TODAS as informações das duas janelas juntas.
# A coluna "formulario" diz de qual janela veio a linha.
# "observacoes" aqui é o que a enfermeira digitou, sem o texto do caso crítico
# (o caso crítico tem colunas próprias).
CAMPOS_ADM = [
    "data_hora_modificacao",
    "formulario",
    "enfermeira",
    "teleoperador",
    "gestante",
    "cns",
    "data_contato",
    "numero",
    "conseguiu_contato",
    "motivo_sem_contato",
    "classificacao",
    "tratamento_sifilis",
    "gestante_risco",
    "pre_natal",
    "nasceu_vivo",
    "local_parto",
    "outro_local",
    "bebe_risco",
    "obito_neonatal",
    "obito_materno",
    "houve_violencia",
    "tipo_violencia",
    "tipo_parto",
    "risco_gestacional",
    "qual_risco",
    "ig_semanas",
    "data_retorno",
    "alto_risco",
    "caso_critico",
    "qual_caso_critico",
    "observacoes",
    "gestante_puerpera",     # caixas "Classificação da gestante"
    "gestante_aborto",
    "gestante_gestante",
]

# As perguntas Sim/Não guardam 1, 0 ou -1; no CSV vira texto
SIM_NAO = {1: "Sim", 0: "Não", -1: ""}


# ============================================================
# VALIDAÇÕES E REGRAS (usadas pelas janelas)
# ============================================================
def cns_valido(texto):
    """CNS válido = exatamente 15 dígitos."""
    texto = (texto or "").strip()
    return texto.isdigit() and len(texto) == 15


def ler_data(texto):
    """Converte 'dd/mm/aaaa' em data. Devolve None se estiver vazio ou inválido."""
    try:
        return datetime.strptime((texto or "").strip(), "%d/%m/%Y").date()
    except ValueError:
        return None


def data_futura(data):
    """True se a data for depois de hoje (contato não pode ser no futuro)."""
    return data > datetime.now().date()


def ler_ig(texto):
    """Converte a IG digitada em (semanas, dias). Formato 'ss+dd' (ex.: 30+2);
    só 'ss' também vale (dias = 0). Devolve None se estiver vazio ou inválido
    (semanas de 0 a 45, dias de 0 a 6)."""
    partes = (texto or "").replace(" ", "").split("+")
    if len(partes) > 2 or not all(p.isdigit() and len(p) <= 2 for p in partes):
        return None
    semanas = int(partes[0])
    dias = int(partes[1]) if len(partes) == 2 else 0
    if not 0 <= semanas <= 45 or not 0 <= dias <= 6:
        return None
    return semanas, dias


def formatar_ig(semanas, dias):
    """(30, 2) -> '30s 02d'."""
    return f"{semanas:02d}s {dias:02d}d"


def calcular_retorno(data_contato, ig_semanas, ig_dias=0):
    """Mesma regra da VIEW: intervalo de retorno conforme a IG."""
    dias = ig_semanas * 7 + ig_dias
    if dias < 196:
        intervalo = 28      # até 28 semanas: a cada 4 semanas
    elif dias < 238:
        intervalo = 14      # 28 a 34 semanas: a cada 2 semanas
    elif dias < 273:
        intervalo = 7       # 34 a 39 semanas: toda semana
    elif dias < 287:
        intervalo = 3       # 39 a 41 semanas: a cada 3 dias
    else:
        intervalo = 1       # 41 semanas ou mais: todo dia
    return data_contato + timedelta(days=intervalo)


# ============================================================
# GRAVAÇÃO (só acrescenta linhas; a única alteração é acrescentar colunas novas
# no cabeçalho de um arquivo de versão anterior, sem perder nenhuma linha)
# ============================================================
def _para_texto(valor):
    """Converte o valor da janela em texto para o CSV."""
    if valor is None:
        return ""
    if isinstance(valor, int):
        return SIM_NAO.get(valor, str(valor))
    texto = str(valor).strip()
    # quebra de linha vira " / ": cada registro fica numa linha só do CSV
    # (mais seguro para o Excel e para o BULK INSERT no SQL)
    return " / ".join(parte.strip() for parte in texto.splitlines() if parte.strip())


def _cabecalho_atual(arquivo):
    """Lê a primeira linha (cabeçalho) de um CSV que já existe."""
    with open(arquivo, newline="", encoding="utf-8-sig") as f:
        return next(csv.reader(f, delimiter=";"), [])


def _gravar(arquivo, campos, dados):
    """Acrescenta UMA linha no CSV, com a data/hora atual."""
    linha = {campo: "" for campo in campos}
    for chave, valor in dados.items():
        if chave in linha:
            linha[chave] = _para_texto(valor)

    # formato ano-mês-dia: ordena certo e não confunde dia com mês
    linha["data_hora_modificacao"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # arquivo de versão anterior (faltam só colunas novas no fim): atualiza o cabeçalho
    _migrar_cabecalho(arquivo, campos)

    arquivo_novo = not arquivo.exists() or arquivo.stat().st_size == 0

    # proteção: não mistura linhas de formatos diferentes no mesmo arquivo
    if not arquivo_novo and _cabecalho_atual(arquivo) != campos:
        raise ValueError(
            f"O arquivo {arquivo.name} é de uma versão antiga (colunas diferentes). "
            "Mova-o para outra pasta e tente de novo: um arquivo novo será criado."
        )
    # BOM ("utf-8-sig") só na criação, para o Excel ler os acentos
    codificacao = "utf-8-sig" if arquivo_novo else "utf-8"

    with open(arquivo, mode="a", newline="", encoding=codificacao) as f:
        escritor = csv.DictWriter(f, fieldnames=campos, delimiter=";")
        if arquivo_novo:
            escritor.writeheader()
        escritor.writerow(linha)
    return arquivo


def observacoes_com_caso_critico(dados):
    """Se for caso crítico, põe '[CASO CRÍTICO] descrição' no começo das observações,
    para a enfermeira ver no quadro de observações da tela principal."""
    obs = (dados.get("observacoes") or "").strip()
    qual = (dados.get("qual_caso_critico") or "").strip()
    if dados.get("caso_critico") == 1 and qual:
        return f"[CASO CRÍTICO] {qual}" + (f"\n{obs}" if obs else "")
    return obs


def _migrar_cabecalho(arquivo, campos):
    """Se o arquivo é da versão anterior (cabeçalho = começo da lista atual, sem as
    colunas novas no fim), reescreve com as colunas novas vazias. Nada é perdido."""
    if not arquivo.exists() or arquivo.stat().st_size == 0:
        return
    atual = _cabecalho_atual(arquivo)
    if atual == campos or campos[:len(atual)] != atual:
        return
    with open(arquivo, newline="", encoding="utf-8-sig") as f:
        linhas = list(csv.DictReader(f, delimiter=";"))
    temporario = arquivo.with_suffix(".tmp")
    try:
        with open(temporario, mode="w", newline="", encoding="utf-8-sig") as f:
            escritor = csv.DictWriter(f, fieldnames=campos, delimiter=";")
            escritor.writeheader()
            escritor.writerows(linhas)
        temporario.replace(arquivo)
    except OSError:
        temporario.unlink(missing_ok=True)
        raise


def _gravar_adm(formulario, dados):
    """Copia o registro (com todos os campos) no CSV administrativo."""
    _migrar_cabecalho(ARQUIVO_ADM, CAMPOS_ADM)
    _gravar(ARQUIVO_ADM, CAMPOS_ADM, {**dados, "formulario": formulario})


def _salvar_com_adm(arquivo, campos, formulario, dados):
    """Grava o CSV da enfermeira (com o caso crítico dentro das observações) e depois
    a cópia no CSV administrativo. Devolve uma lista de avisos (vazia = tudo certo).
    Se só o ADM falhar, o registro principal já está salvo: não se perde nada."""
    dados_enfermeira = {**dados, "observacoes": observacoes_com_caso_critico(dados)}
    _gravar(arquivo, campos, dados_enfermeira)

    avisos = []
    try:
        _gravar_adm(formulario, dados)
    except PermissionError:
        avisos.append(f"O registro foi salvo, mas o arquivo {ARQUIVO_ADM.name} está aberto "
                      "em outro programa (ex.: Excel) e a cópia administrativa NÃO foi gravada.")
    except (ValueError, OSError) as erro:
        avisos.append(f"O registro foi salvo, mas a cópia administrativa NÃO foi gravada: {erro}")
    return avisos


def salvar(dados):
    """Registro do 'Finalizar Atendimento'. Devolve lista de avisos."""
    return _salvar_com_adm(ARQUIVO_MONITORAMENTO, CAMPOS_MONITORAMENTO,
                           "Finalizar Atendimento", dados)


def salvar_busca_ativa(dados):
    """Registro do 'Registrar Busca Ativa'. Devolve lista de avisos."""
    return _salvar_com_adm(ARQUIVO_BUSCA_ATIVA, CAMPOS_BUSCA_ATIVA,
                           "Busca Ativa", dados)


# ============================================================
# LEITURA DAS OBSERVAÇÕES (usada pela tela principal)
# Só LÊ os CSVs: nada é alterado.
# ============================================================
def _ler_csv(arquivo):
    """Devolve as linhas do CSV como dicionários (lista vazia se não existir)."""
    if not arquivo.exists():
        return []
    try:
        with open(arquivo, newline="", encoding="utf-8-sig") as f:
            return list(csv.DictReader(f, delimiter=";"))
    except OSError:
        return []            # arquivo bloqueado: só não mostra nada desta vez


def ler_observacoes(cns):
    """Todas as observações já salvas para esse CNS, da mais nova para a mais antiga.
    Cada item: (data_hora, origem, enfermeira, texto)."""
    cns = (cns or "").strip()
    if not cns:
        return []
    fontes = [
        (ARQUIVO_MONITORAMENTO, "Finalizar Atendimento"),
        (ARQUIVO_BUSCA_ATIVA,   "Busca Ativa"),
    ]
    encontradas = []
    for arquivo, origem in fontes:
        for linha in _ler_csv(arquivo):
            texto = (linha.get("observacoes") or "").strip()
            if linha.get("cns") == cns and texto:
                encontradas.append((linha.get("data_hora_modificacao", ""), origem,
                                    linha.get("enfermeira", ""), texto))
    # data no formato ano-mês-dia: ordenar como texto já dá a ordem certa.
    # Empate no mesmo segundo: a que foi lida depois (gravada depois) fica em cima.
    ordem = {id(item): posicao for posicao, item in enumerate(encontradas)}
    encontradas.sort(key=lambda item: (item[0], ordem[id(item)]), reverse=True)
    return encontradas


# ============================================================
# IG E RETORNO ATUALIZADOS PELO APP (usados para atualizar o grid da tela principal)
# Só LÊ os CSVs: nada é alterado.
# ============================================================
def ultimas_atualizacoes():
    """Dicionário {cns: {"ig": (data_contato, semanas), "retorno": (data_contato, data_retorno),
                        "alto_risco": (data_contato, True/False)}}.
    Para cada CNS vale o registro mais recente que trouxe aquele dado
    (Busca Ativa e Finalizar Atendimento). Registro sem IG não mexe na IG;
    registro sem retorno não mexe no retorno; o alto risco vem só da Busca Ativa."""
    linhas = _ler_csv(ARQUIVO_BUSCA_ATIVA)
    # a Busca Ativa também é copiada no ADM: aqui só entram os Finalizar Atendimento
    linhas += [l for l in _ler_csv(ARQUIVO_ADM) if l.get("formulario") == "Finalizar Atendimento"]

    atualizacoes = {}
    chaves = {}          # (cns, tipo) -> (data_contato, data_hora) do valor guardado
    for linha in linhas:
        cns = (linha.get("cns") or "").strip()
        contato = ler_data(linha.get("data_contato"))
        if not cns or contato is None or not entra_no_grid(linha):
            continue
        ordem = (contato, linha.get("data_hora_modificacao", ""))

        ig = ler_ig(linha.get("ig_semanas"))
        retorno = ler_data(linha.get("data_retorno"))
        risco = (linha.get("alto_risco") or "").strip()      # só a Busca Ativa preenche
        for tipo, valor in (("ig", ig),
                            ("retorno", retorno),
                            ("alto_risco", {"Sim": True, "Não": False}.get(risco))):
            if valor is None:
                continue
            if (cns, tipo) not in chaves or ordem >= chaves[(cns, tipo)]:
                chaves[(cns, tipo)] = ordem
                atualizacoes.setdefault(cns, {})[tipo] = (contato, valor)
    return atualizacoes


# ============================================================
# GESTANTES NOVAS CADASTRADAS PELA BUSCA ATIVA (entram na lista da enfermeira)
# Só LÊ o CSV: nada é alterado.
# ============================================================
def entra_no_grid(linha):
    """Só quem é Gestante entra na lista da tela principal.
    Puérpera e Aborto ficam salvos, mas fora da lista. Registros antigos
    (sem a classificação) contam como gestante."""
    return not (linha.get("gestante_puerpera") == "Sim" or linha.get("gestante_aborto") == "Sim")


def gestantes_busca_ativa(enfermeira):
    """Gestantes cadastradas pela Busca Ativa para essa enfermeira.
    Uma por CNS, com os dados do registro mais recente; se o registro mais recente
    for de outra enfermeira, a gestante pertence a ela (foi repassada).
    Cada item: dict com gestante, cns, data_contato, ig, data_retorno, alto_risco."""
    ultimas = {}
    for linha in _ler_csv(ARQUIVO_BUSCA_ATIVA):
        cns = (linha.get("cns") or "").strip()
        contato = ler_data(linha.get("data_contato"))
        if not cns or contato is None:
            continue
        ordem = (contato, linha.get("data_hora_modificacao", ""))
        if cns not in ultimas or ordem >= ultimas[cns][0]:
            ultimas[cns] = (ordem, linha)

    resultado = []
    for cns, (ordem, linha) in ultimas.items():
        if (linha.get("enfermeira") or "").strip() != enfermeira or not entra_no_grid(linha):
            continue
        resultado.append({
            "gestante": (linha.get("gestante") or "").strip(),
            "cns": cns,
            "data_contato": ordem[0],
            "ig": ler_ig(linha.get("ig_semanas")),      # (semanas, dias) ou None
            "data_retorno": ler_data(linha.get("data_retorno")),
            "alto_risco": (linha.get("alto_risco") or "").strip() == "Sim",
        })
    return resultado


# ============================================================
# ÚLTIMA DATA DE CONTATO (usada para atualizar a lista da tela principal)
# Só LÊ os CSVs: nada é alterado.
# ============================================================
def ultimos_contatos():
    """Dicionário {cns: data do contato mais recente registrada nos CSVs}.
    Lê cada arquivo uma vez só, para a lista abrir rápido."""
    contatos = {}
    for arquivo in (ARQUIVO_MONITORAMENTO, ARQUIVO_BUSCA_ATIVA):
        for linha in _ler_csv(arquivo):
            cns = (linha.get("cns") or "").strip()
            data = ler_data(linha.get("data_contato"))
            if cns and data and (cns not in contatos or data > contatos[cns]):
                contatos[cns] = data
    return contatos
