from tkinter import *
from tkinter import ttk, messagebox
import tratando_csv
import automacao
import reg_busca
import forms
import monitora_gestante
from datetime import datetime


def formatar_data(data):
    """Transforma a data do banco em dd/mm/aaaa (ou — se estiver vazia)."""
    return data.strftime("%d/%m/%Y") if data else "—"


def so_data(valor):
    """O banco pode mandar data ou data+hora; aqui fica só a data (ou None)."""
    if isinstance(valor, datetime):
        return valor.date()
    return valor


def texto_ou_traco(valor):
    """Mostra — quando o valor vier vazio do banco (em vez de 'None')."""
    return "—" if valor in (None, "") else str(valor)


def eh_alto_risco(valor):
    """Aceita os jeitos que o banco pode mandar: 1, True, "1", "S", "Sim"."""
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

    for item in tabela.get_children():
        tabela.delete(item)

    for g in gestantes:
        # Contato: vale a data mais recente entre a VIEW e o que foi salvo no app
        data_contato = so_data(g.data_contato)
        data_app = contatos_app.get(texto_ou_traco(g.cns))
        if data_app and (data_contato is None or data_app > data_contato):
            data_contato = data_app

        ig = "—" if g.ig_semanas is None else f"{g.ig_semanas}s {g.ig_dias_resto}d"
        alto = eh_alto_risco(g.alto_risco)
        risco = "Alto Risco" if alto else ""
        etiqueta = ("alto_risco",) if alto else ()

        tabela.insert("", END, values=(
            texto_ou_traco(g.gestante),
            texto_ou_traco(g.cns),
            formatar_data(data_contato),
            ig,
            formatar_data(g.data_retorno),
            risco,
        ), tags=etiqueta)

    status.config(text=f"{len(gestantes)} gestante(s)")
    mostrar_observacoes()          # lista nova: limpa o quadro de observações


# Clique com o MOUSE numa gestante: manda o CNS para a automação
# (as setas do teclado só movem a seleção, sem abrir o e-Saúde)
def clicou_gestante(event):
    item = tabela.identify_row(event.y)
    if not item:
        return                                   # clicou no cabeçalho ou em área vazia
    cns = tabela.set(item, "cns")
    if cns == "—":
        status_automacao.config(text="Essa gestante não tem CNS: não dá para buscar no e-Saúde.")
        return
    if not automacao.iniciar(cns):
        status_automacao.config(text="Aguarde: ainda buscando a gestante anterior.")


def cns_selecionado():
    """CNS da gestante selecionada na lista (ou vazio)."""
    selecionado = tabela.selection()
    if not selecionado:
        return ""
    cns = tabela.set(selecionado[0], "cns")
    return "" if cns == "—" else cns


def data_hora_br(texto):
    """'2026-09-29 10:15:00' -> '29/09/2026 10:15' (se não der, mostra como veio)."""
    try:
        return datetime.strptime(texto, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M")
    except ValueError:
        return texto


# Mostra no quadro de baixo as observações salvas da gestante selecionada
# (lê os CSVs pelo monitora_gestante.py; o banco não é tocado)
def mostrar_observacoes(event=None):
    cns = cns_selecionado()
    quadro_obs.config(state="normal")
    quadro_obs.delete("1.0", END)

    if not tabela.selection():
        quadro_obs.insert(END, "Selecione uma gestante para ver as observações.")
    elif not cns:
        quadro_obs.insert(END, "Essa gestante não tem CNS: não há como achar observações.")
    else:
        registros = monitora_gestante.ler_observacoes(cns)
        if not registros:
            quadro_obs.insert(END, "Nenhuma observação registrada para essa gestante.")
        for data_hora, origem, enfermeira, texto in registros:
            quadro_obs.insert(END, f"{data_hora_br(data_hora)} — {origem} — {enfermeira}\n", "titulo")
            quadro_obs.insert(END, f"{texto}\n\n")

    quadro_obs.config(state="disabled")      # só leitura


# Depois de salvar: recarrega a lista (datas novas) e mantém a mesma gestante selecionada
def atualizar_tela():
    cns = cns_selecionado()
    if nome.get():
        mostrar_gestantes()
    if cns:
        for item in tabela.get_children():
            if tabela.set(item, "cns") == cns:
                tabela.selection_set(item)
                tabela.see(item)
                break
    mostrar_observacoes()


def abrir_finalizar():
    forms.start_forms(root, cns_inicial=cns_selecionado(), enfermeira_inicial=nome.get(),
                      ao_salvar=atualizar_tela)


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
colunas = ("gestante", "cns", "contato", "ig", "retorno", "risco")
tabela = ttk.Treeview(frm, columns=colunas, show="headings", height=15)

titulos = {
    "gestante": ("Gestante", 260),
    "cns":      ("CNS", 150),
    "contato":  ("Contato", 90),
    "ig":       ("IG", 70),
    "retorno":  ("Retorno", 90),
    "risco":    ("Risco", 90),
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
