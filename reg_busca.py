from tkinter import *
from tkinter import ttk
import tratando_csv

def registrar_gestante(event):
    enfermeira = nome.get()

def start():
    root2 = Tk()
    frm = ttk.Frame(root2, padding=10)
    frm.grid()
    # selecionar enfermeira
    ttk.Label(frm, text="Enfermeira (o):").grid(column=0, row=0, sticky="w")

    nome = ttk.Combobox(frm, values=tratando_csv.listar_enfermeiras(), state="readonly", width=45)
    nome.grid(column=1, row=0, sticky="w")

    # Registrar nome da gestante
    ttk.Label(frm, text="Nome da Gestante: ").grid(column=0, row=1)
    gestante = ttk.Entry(frm)
    gestante.grid(column=1, row=1)

    # Adicionar nome da mãe

    
    # Registrar CNS
    ttk.Label(frm, text="CNS da Gestante: ").grid(column=0, row=2)
    cnes = ttk.Entry(frm)
    cnes.grid(column=1, row=2)

    # Data do ultimo contato 
    ttk.Label(frm, text="Data do Contato: ").grid(column=0, row=3)
    data_ctt = ttk.Entry(frm)
    data_ctt.grid(column=1, row=3)

    # Registrar idade Gestacional atual
    ttk.Label(frm, text="Idade Gestacional Atual: ").grid(column=0, row=4)
    ig = ttk.Entry(frm)
    ig.grid(column=1, row=4)

    # data do Retorno
    ttk .Label(frm, text="Inserir data de retorno: ").grid(column=0, row=5)
    data_retorno = ttk.Entry(frm)
    data_retorno.grid(column=1, row=5)
    # tratar se tiver vazio

    # Confirmar Alto risco
    ttk.Label(frm, text="Paciente de Alto Risco? ").grid(column=0, row=6)
    
    radio_sim = ttk.Radiobutton(frm, text="Sim",  value=1)
    radio_sim.grid(column=0, row=7)

    radio_nao = ttk.Radiobutton(frm, text="Não", value=0)
    radio_nao.grid(column=1, row=7)

    # Enviar para CSV ou db
    botao = ttk.Button(frm, text="Enviar para Enfermeira")
    botao.grid(column=0, row=8)

    root2.mainloop()