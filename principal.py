from tkinter import *
from tkinter import ttk, messagebox
import tratando_csv
import automacao
import reg_busca
import forms
import monitora_gestante
from datetime import datetime, date

# Configurações
def formatar_data(data):
    return data.strftime("%d/%m/%Y") if data else "—"


def so_data(valor):
    if isinstance(valor, datetime):
        return valor.date()
    return valor


def texto_ou_traco(valor):
    """Mostra — quando o valor vier vazio do banco (em vez de 'None')."""
    return "—" if valor in (None, "") else str(valor)


def texto_busca_ativa(busca, contato_banco=None):
    """'Busca ativa 30/09 14:35' enquanto a busca ativa estiver em andamento.
    Some quando chega um contato novo do e-Saúde (data da VIEW depois da data da busca);
    quando a enfermeira finaliza o atendimento, o monitora_gestante já não a devolve."""
    if not busca:
        return ""
    if contato_banco is not None and contato_banco > busca["data_contato"]:
        return ""
    return f"Busca ativa {busca['hora']}"


def eh_alto_risco(valor):
    return str(valor).strip().upper() in ("1", "TRUE", "S", "SIM")


# Mostra as gestantes da enfermeira escolhida no menu
def mostrar_gestantes(event=None):
    enfermeira = nome.get()
    try:
        gestantes = tratando_csv.buscar_gestantes(enfermeira)
    except Exception:
        messagebox.showerror("Banco de dados",
                             "Não foi possível buscar as gestantes.\n"
                             "Verifique se o SQL Server está ligado.", parent=root)
        return

    # contatos registrados pelo app (CSVs); o banco continua intocado
    contatos_app = monitora_gestante.ultimos_contatos()
    # IG e retorno atualizados pelo app
    atualizacoes_app = monitora_gestante.ultimas_atualizacoes()
    # buscas ativas ainda em andamento (informação temporária da coluna "Busca Ativa")
    buscas_app = monitora_gestante.buscas_ativas_pendentes()

    for item in tabela.get_children():
        tabela.delete(item)

    linhas = []          # (retorno para ordenar, valores da linha, etiqueta)
    chaves_da_lista = set()

    for g in gestantes:
        # chave da gestante: o CNS; sem CNS, "CPF ..." (é assim que os CSVs e o banco a acham)
        k = monitora_gestante.chave(g.cns, g.cpf)
        chaves_da_lista.add(k)
        # Contato: vale a data mais recente entre a VIEW e o que foi salvo no app
        data_contato = so_data(g.data_contato)
        contato_banco = data_contato          # contato da VIEW, antes de olhar o app
        data_app = contatos_app.get(k)
        if data_app and (data_contato is None or data_app > data_contato):
            data_contato = data_app

        ig = "—" if g.ig_semanas is None else monitora_gestante.formatar_ig(g.ig_semanas, g.ig_dias_resto)
        data_retorno = g.data_retorno

        # IG e retorno do app valem se o registro for do mesmo dia (ou mais novo) que o contato da VIEW
        atual = atualizacoes_app.get(k, {})
        if "ig" in atual and (contato_banco is None or atual["ig"][0] >= contato_banco):
            ig = monitora_gestante.formatar_ig(*atual["ig"][1])
        if "retorno" in atual and (contato_banco is None or atual["retorno"][0] >= contato_banco):
            data_retorno = atual["retorno"][1]
        alto = eh_alto_risco(g.alto_risco)
        if "alto_risco" in atual and (contato_banco is None or atual["alto_risco"][0] >= contato_banco):
            alto = atual["alto_risco"][1]
        risco = "Alto Risco" if alto else ""
        etiqueta = ("alto_risco",) if alto else ()
        busca = texto_busca_ativa(buscas_app.get(k), contato_banco)

        retorno = so_data(data_retorno)
        linhas.append((retorno, (
            texto_ou_traco(g.gestante),
            texto_ou_traco(g.cns),
            formatar_data(data_contato),
            ig,
            formatar_data(retorno),
            risco,
            busca,
            texto_ou_traco(g.cpf),             # coluna escondida (usada pela automação)
        ), etiqueta))

    # gestantes NOVAS cadastradas pela Busca Ativa (ainda não estão no banco)
    novas = [n for n in monitora_gestante.gestantes_busca_ativa(enfermeira)
             if n["chave"] not in chaves_da_lista]
    for n in novas:
        ig_nova = "—" if n["ig"] is None else monitora_gestante.formatar_ig(*n["ig"])
        linhas.append((n["data_retorno"], (
            texto_ou_traco(n["gestante"]),
            texto_ou_traco(n["cns"]),
            formatar_data(n["data_contato"]),
            ig_nova,
            formatar_data(n["data_retorno"]),
            "Alto Risco" if n["alto_risco"] else "",
            texto_busca_ativa(buscas_app.get(n["chave"])),
            texto_ou_traco(n["cpf"]),
        ), ("alto_risco",) if n["alto_risco"] else ()))

    # mais urgente primeiro; sem data de retorno vai para o fim (a ordem anterior se mantém)
    linhas.sort(key=lambda l: (l[0] is None, l[0] or date.max))
    for _, valores, etiqueta in linhas:
        tabela.insert("", END, values=valores, tags=etiqueta)

    status.config(text=f"{len(linhas)} gestante(s)")
    mostrar_observacoes()          # lista nova: limpa o quadro de observações


def dados_da_linha(item):
    """(cns, cpf, nome) de uma linha da lista; '—' vira vazio."""
    def valor(coluna):
        texto = tabela.set(item, coluna)
        return "" if texto == "—" else texto
    return valor("cns"), valor("cpf"), valor("gestante")


# Clique com o MOUSE numa gestante: manda os dados para a automação
# (as setas do teclado só movem a seleção, sem abrir o e-Saúde)
#   com CNS -> busca pelo CNS | sem CNS -> busca pelo CPF
def clicou_gestante(event):
    item = tabela.identify_row(event.y)
    if not item:
        return                                   # clicou no cabeçalho ou em área vazia
    cns, cpf, nome = dados_da_linha(item)
    if not cns and not cpf:
        status_automacao.config(text="Essa gestante não tem CNS nem CPF: não dá para buscar no e-Saúde.")
        return
    if not automacao.iniciar(cns, cpf, nome):
        status_automacao.config(text="Aguarde: ainda buscando a gestante anterior.")


def selecionada():
    """(cns, cpf, nome) da gestante selecionada na lista (vazios se nenhuma)."""
    item = tabela.selection()
    return dados_da_linha(item[0]) if item else ("", "", "")


def chave_selecionada():
    """Chave da gestante selecionada: o CNS; sem CNS, 'CPF ...' (ou vazio)."""
    cns, cpf, _ = selecionada()
    return monitora_gestante.chave(cns, cpf)


def data_hora_br(texto):
    """'2026-09-29 10:15:00' -> '29/09/2026 10:15' (se não der, mostra como veio)."""
    try:
        return datetime.strptime(texto, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M")
    except ValueError:
        return texto


# Mostra no quadro de baixo as observações salvas da gestante selecionada
# (lê os CSVs pelo monitora_gestante.py; o banco não é tocado)
def mostrar_observacoes(event=None):
    cns = chave_selecionada()          # CNS, ou "CPF ..." quando não há CNS
    quadro_obs.config(state="normal")
    quadro_obs.delete("1.0", END)

    if not tabela.selection():
        quadro_obs.insert(END, "Selecione uma gestante para ver as observações.")
    elif not cns:
        quadro_obs.insert(END, "Essa gestante não tem CNS nem CPF: não há como achar observações.")
    else:
        registros = monitora_gestante.ler_observacoes(cns)
        if not registros:
            quadro_obs.insert(END, "Nenhuma observação registrada para essa gestante.")
        for data_hora, origem, enfermeira, texto in registros:
            quadro_obs.insert(END, f"{data_hora_br(data_hora)} — {origem} — {enfermeira}\n", "titulo")
            quadro_obs.insert(END, f"{texto}\n\n")

    quadro_obs.config(state="disabled")      # só leitura


# Depois de salvar: recarrega a lista (datas novas) e mantém a mesma gestante selecionada
def atualizar_tela(cns_salvo=None):
    """cns_salvo: a chave da gestante salva (CNS, ou 'CPF ...')."""
    cns = cns_salvo or chave_selecionada()
    if nome.get():
        mostrar_gestantes()
    achou = False
    if cns:
        for item in tabela.get_children():
            cns_linha, cpf_linha, _ = dados_da_linha(item)
            if monitora_gestante.chave(cns_linha, cpf_linha) == cns:
                tabela.selection_set(item)
                tabela.see(item)
                achou = True
                break
    if cns_salvo and nome.get() and not achou:
        status.config(text="Registro salvo para outra enfermeira: escolha-a no menu para ver a gestante.")
    mostrar_observacoes()


def abrir_finalizar():
    cns, cpf, nome_gestante = selecionada()
    forms.start_forms(root, cns_inicial=cns, cpf_inicial=cpf, nome_inicial=nome_gestante,
                      enfermeira_inicial=nome.get(), ao_salvar=atualizar_tela)


def abrir_busca_ativa():
    reg_busca.start(root, enfermeira_inicial=nome.get(), ao_salvar=atualizar_tela)


# Mostra na janela o que a automação está fazendo (atualiza a cada 1 segundo)
def atualizar_status_automacao():
    if automacao.status:
        status_automacao.config(text=automacao.status)
    root.after(1000, atualizar_status_automacao)


def ao_fechar():
    automacao.fechar()     # fecha o Chrome da automação junto
    root.destroy()


# ================= INÍCIO DA JANELA PRINCIPAL =================
root = Tk()
root.title("Retorno de Gestantes")

# Carrega as enfermeiras; se o banco estiver fora, avisa e fecha
try:
    enfermeiras = tratando_csv.listar_enfermeiras()
except Exception:
    root.withdraw()
    messagebox.showerror("Banco de dados",
                         "Não foi possível conectar ao banco poc_gestante.\n"
                         "Verifique se o SQL Server está ligado e tente de novo.")
    root.destroy()
    raise SystemExit(1)

frm = ttk.Frame(root, padding=10)
frm.grid()

# campo do nome da(o) Enfermeira(o)
ttk.Label(frm, text="Enfermeira (o):").grid(column=0, row=0, sticky="w")
nome = ttk.Combobox(frm, values=enfermeiras, state="readonly", width=45)
nome.grid(column=1, row=0, sticky="w")
nome.bind("<<ComboboxSelected>>", mostrar_gestantes)

# tabela com as gestantes
colunas = ("gestante", "cns", "contato", "ig", "retorno", "risco", "busca", "cpf")
tabela = ttk.Treeview(frm, columns=colunas, show="headings", height=15,
                      displaycolumns=colunas[:-1])     # o CPF fica guardado, mas não aparece

titulos = {
    "gestante": ("Gestante", 260),
    "cns":      ("CNS", 150),
    "contato":  ("Contato", 90),
    "ig":       ("IG", 70),
    "retorno":  ("Retorno", 90),
    "risco":    ("Risco", 90),
    "busca":    ("Busca Ativa", 150),
}
for coluna, (titulo, largura) in titulos.items():
    tabela.heading(coluna, text=titulo)
    tabela.column(coluna, width=largura, anchor="w")

# Correção para o Windows: o tema padrão do ttk "passa por cima" da cor das tags.
# Aqui tiramos essa regra do tema, para a cor da tag (vermelho) valer de novo.
estilo = ttk.Style()


def mapa_sem_padrao(opcao):
    return [regra for regra in estilo.map("Treeview", query_opt=opcao)
            if regra[:2] != ("!disabled", "!selected")]


estilo.map("Treeview",
           foreground=mapa_sem_padrao("foreground"),
           background=mapa_sem_padrao("background"))

tabela.tag_configure("alto_risco", foreground="red")
tabela.grid(column=0, row=1, columnspan=2, pady=5)

# barra de scroll (colada na tabela)
barra = ttk.Scrollbar(frm, orient=VERTICAL, command=tabela.yview)
barra.grid(column=2, row=1, sticky="ns", pady=5)
tabela.config(yscrollcommand=barra.set)

# contador de gestantes
status = ttk.Label(frm, text="")
status.grid(column=0, row=2, columnspan=2, sticky="w")

# o que a automação está fazendo
status_automacao = ttk.Label(frm, text="", foreground="blue")
status_automacao.grid(column=0, row=3, columnspan=3, sticky="w")

# clique do mouse na gestante inicia a automação
tabela.bind("<ButtonRelease-1>", clicou_gestante)

# botões
botoes = ttk.Frame(frm)
botoes.grid(column=0, row=4, columnspan=3, sticky="e", pady=(10, 0))
ttk.Button(botoes, text="Registrar Busca Ativa", command=abrir_busca_ativa).grid(column=0, row=0, padx=5)
ttk.Button(botoes, text="Finalizar Atendimento", command=abrir_finalizar).grid(column=1, row=0)

# quadro de observações da gestante selecionada (no final da tela)
caixa_obs = ttk.LabelFrame(frm, text="Observações da gestante selecionada", padding=5)
caixa_obs.grid(column=0, row=5, columnspan=3, sticky="we", pady=(10, 0))
quadro_obs = Text(caixa_obs, height=7, width=95, wrap="word", state="disabled")
quadro_obs.grid(column=0, row=0, sticky="we")
barra_obs = ttk.Scrollbar(caixa_obs, orient=VERTICAL, command=quadro_obs.yview)
barra_obs.grid(column=1, row=0, sticky="ns")
quadro_obs.config(yscrollcommand=barra_obs.set)
quadro_obs.tag_configure("titulo", font=("TkDefaultFont", 9, "bold"))

# mudou a seleção (mouse ou teclado) -> atualiza as observações
# (a automação continua só no clique do mouse)
tabela.bind("<<TreeviewSelect>>", mostrar_observacoes)
mostrar_observacoes()

root.protocol("WM_DELETE_WINDOW", ao_fechar)
atualizar_status_automacao()

root.mainloop()
