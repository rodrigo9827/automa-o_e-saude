from tkinter import *
from tkinter import ttk
import tratando_csv
import automacao
import reg_busca
import forms



def formatar_data(data):
    """Transforma a data do banco em dd/mm/aaaa (ou — se estiver vazia)."""
    return data.strftime("%d/%m/%Y") if data else "—"


# Mostra as gestantes da enfermeira escolhida no menu
def mostrar_gestantes(event):
    enfermeira = nome.get()
    gestantes = tratando_csv.buscar_gestantes(enfermeira)

    # limpa a tabela antes de preencher de novo
    for item in tabela.get_children():
        tabela.delete(item)

    for g in gestantes:
        if g.ig_semanas is None:
            ig = "—"
        else:
            ig = f"{g.ig_semanas}s {g.ig_dias_resto}d"

        risco = "Alto Risco" if g.alto_risco == 1 else ""
        etiqueta = ("alto_risco",) if g.alto_risco == 1 else ()

        tabela.insert("", END, values=(
            g.gestante,
            g.cns,
            formatar_data(g.data_contato),
            ig,
            formatar_data(g.data_retorno),
            risco,
        ), tags=etiqueta)

    status.config(text=f"{len(gestantes)} gestante(s)")


# Quando clica numa gestante, manda o CNS para a automação
def clicou_gestante(event):
    selecionado = tabela.selection()
    if not selecionado:
        return
    cns = tabela.set(selecionado[0], "cns")
    automacao.iniciar(cns)


# Início da janela principal
root = Tk()
root.title("Retorno de Gestantes")
frm = ttk.Frame(root, padding=10)
frm.grid()

# campo do nome da(o) Enfermeira(o)
ttk.Label(frm, text="Enfermeira (o):").grid(column=0, row=0, sticky="w")

nome = ttk.Combobox(frm, values=tratando_csv.listar_enfermeiras(), state="readonly", width=45)
nome.grid(column=1, row=0, sticky="w")
nome.bind("<<ComboboxSelected>>", mostrar_gestantes)

# tabela com as gestantes
colunas = ("gestante", "cns", "contato", "ig", "retorno", "risco")
tabela = ttk.Treeview(frm, columns=colunas, show="headings", height=15)

titulos = {
    "gestante": ("Gestante", 260),
    "cns":      ("CNS", 130),
    "contato":  ("Contato", 90),
    "ig":       ("IG", 70),
    "retorno":  ("Retorno", 90),
    "risco":    ("Risco", 90),
}
for coluna, (titulo, largura) in titulos.items():
    tabela.heading(coluna, text=titulo)
    tabela.column(coluna, width=largura, anchor="w")

tabela.tag_configure("alto_risco", foreground="red")
tabela.grid(column=0, row=1, columnspan=2, pady=5)

# barra de scroll
barra = ttk.Scrollbar(frm, orient=VERTICAL, command=tabela.yview)
barra.grid(column=2, row=1, sticky="ns")
tabela.config(yscrollcommand=barra.set)

# contador de gestantes
status = ttk.Label(frm, text="")
status.grid(column=0, row=2, columnspan=2, sticky="w")

# clique na gestante inicia a automação
tabela.bind("<<TreeviewSelect>>", clicou_gestante)

# Registrar busca ativa
adicionar = ttk.Button(frm, text ="Registrar Busca Ativa", command=reg_busca.start)
adicionar.grid(column=1, row=3)

# finalizar atendimento
finalizar = ttk.Button(frm, text="Finalizar Atendimento", command=forms.start_forms)
finalizar.grid(column=2, row=3)



root.mainloop()