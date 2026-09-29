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


def calcular_retorno(data_contato, ig_semanas):
    """Mesma regra da VIEW: intervalo de retorno conforme a IG."""
    dias = ig_semanas * 7
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
# GRAVAÇÃO (só acrescenta linhas; nunca apaga nem altera)
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


def salvar(dados):
    """Registro do 'Finalizar Atendimento'."""
    return _gravar(ARQUIVO_MONITORAMENTO, CAMPOS_MONITORAMENTO, dados)


def salvar_busca_ativa(dados):
    """Registro do 'Registrar Busca Ativa'."""
    return _gravar(ARQUIVO_BUSCA_ATIVA, CAMPOS_BUSCA_ATIVA, dados)


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
