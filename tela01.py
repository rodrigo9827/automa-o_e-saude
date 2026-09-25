from tkinter import *
from tkinter import ttk
import tratando_csv
import automacao

def mostrar_cns(event):
    enfermeira = nome.get()
    texto = tratando_csv.buscar_cns(enfermeira)

    resultado.delete(0, END)
    for linha in texto.split("\n"):
        if linha != "":
            resultado.insert(END, linha)

def clicou_cns(event):
    selecionado = resultado.curselection()
    if not selecionado:
        return
    linha = resultado.get(selecionado[0])
    cns = linha.replace("CNS:", "").strip()
    automacao.iniciar(cns)

root = Tk()
frm = ttk.Frame(root, padding=10)
frm.grid()

#campo do nome da(o) Enfermeira(o)
ttk.Label(frm, text="Enfermeira (o):").grid(column=0, row=0)

# campo para listar enfermeira(o)
nome = ttk.Combobox(frm, values=tratando_csv.listar_enfermeiras(), state="readonly", width=40)
nome.grid(column=1, row=0)
nome.bind("<<ComboboxSelected>>", mostrar_cns)

#mostrar a lista de CNS do enfermeiro(a)
resultado = Listbox(frm, width=45, height=15, exportselection=False)
resultado.grid(column=0, row=1, columnspan=2)

# barra de scroll
barra = ttk.Scrollbar(frm, orient=VERTICAL, command=resultado.yview)
barra.grid(column=2, row=1, sticky='ns')

# posicionamento da barra de scroll
resultado.config(yscrollcommand=barra.set)

resultado.bind("<<ListboxSelect>>", clicou_cns)


root.mainloop()