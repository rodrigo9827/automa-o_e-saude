from tkinter import *
from tkinter import ttk
import tratando_csv

HOSPITAIS = [
    "Hospital das Clínicas",
    "Hospital Geral de Santa Marcelina",
    "Hospital Grajaú",
    "Hospital Guaianazes",
    "Hospital Interlagos",
    "Hospital Ipiranga",
    "Hospital Leonor Mendes de Barros",
    "Hospital Mandaqui",
    "Hospital Pedreira",
    "Hospital Penteado",
    "Hospital Regional Sul",
    "Hospital Santa Marcelina Itaquera",
    "Hospital São Mateus",
    "Hospital São Paulo - UNIFESP",
    "Hospital Sapopemba",
    "Hospital Taipas",
    "Hospital Universitário Usp-SP",
    "Hospital Vila Alpina",
    "Irmandade de Santa Casa de Misericórdia de São Paulo",
    "Hospital Amparo Maternal",
    "Hospital Campo Limpo",
    "Hospital José Soares Hungria",
    "Hospital M Boi Mirim",
    "Hospital Santo Antonio",
    "Hospital São Luiz Gonzaga",
    "Hospital Servidor Publico Municipal",
    "Hospital Tide Setúbal",
    "Hospital Vila Nova Cachoeirinha",
    "Hospital Vila Santa Catarina",
    "Hospital Municipal J. Sarah - Mario Degni",
    "Hospital Municipal de Parelheiros",
    "Maternidade Cachoeirinha",
    "Hospital Luz Vila Mariana",
    "Hospital e Maternidade Santa Bárbara",
    "Hospital Planalto (Municipal Prof. Dr. Waldomiro de Paula)",
    "HOSPITAL VERMELHINHO - Hospital Municipal Vereador José Storopolli",
    "ERMELINO MATARAZZO  - Hospital Municipal Professor Doutor Alípio Corrêa Netto",
    "Hospital João XXIII -Hospital Municipal Dr. Ignácio Proença de Gouvêa",
    "Casa Angela - Centro de Parto Humanizado",
    "Casa do Parto de Sapopemba",
    "Hospital Central Leste - Guaianazes",
    "HOSP MUN MAT ESC DR MARIO DE MORAES A SILVA - Hospital Municipal Maternidade Escola Vila Nova Cachoeirinha",
    "HOSP SERVIDO ESTADUAL - IAMSP",
    "Hospital da Mulher Maria José dos Santos Stein",
    "Hospital da Mulher de São Bernardo do Campo",
    "HOSPITAL SANTA MARCELINA TIRADENTES",
    "Outro Município",
    "Particular",
    "Outro",
]


def start_forms():
    root3 = Tk()
    frm = ttk.Frame(root3, padding=10)
    frm.grid()

    # Selecionar Enfermeira
    ttk.Label(frm, text="Enfermeira (o):").grid(column=0, row=0, sticky="w")

    nome = ttk.Combobox(frm, values=tratando_csv.listar_enfermeiras(), state="readonly", width=45)
    nome.grid(column=1, row=0, sticky="w")

    # Conseguiu o contato?
    ttk.Label(frm, text="Conseguiu o contato? ").grid(column=0, row=1)

    # master=root3 garante que a variável pertence a esta janela
    conseguiu_contato = IntVar(master=root3, value=-1)  # -1 = nada marcado

    ttk.Radiobutton(frm, text="Sim", value=1, variable=conseguiu_contato).grid(column=0, row=2)
    ttk.Radiobutton(frm, text="Não", value=0, variable=conseguiu_contato).grid(column=1, row=2)

    # CNS
    ttk.Label(frm, text="CNS da Gestante (apenas números): ").grid(column=0, row=3)
    cns = ttk.Entry(frm)
    cns.grid(column=1, row=3)

    # Número de contato
    ttk.Label(frm, text="Número do contato: ").grid(column=0, row=4)
    numero = ttk.Entry(frm)
    numero.grid(column=1, row=4)

    # Classificação
    ttk.Label(frm, text="Classificação: ").grid(column=0, row=5)
    classificacao = ttk.Combobox(
        frm, values=["Gestante", "Puérpera", "Aborto"], width=25, state="readonly"
    )
    classificacao.grid(column=0, row=6, sticky="w")

    # Bloco exibido apenas se Puérpera (criado uma vez, começa escondido)
    frame_puerpera = ttk.Frame(frm)
    frame_puerpera.grid(column=0, row=7, columnspan=2, sticky="w", pady=(10, 0))

    # Nasceu vivo?
    ttk.Label(frame_puerpera, text="Nasceu vivo?").grid(column=0, row=0, columnspan=2)

    nasceu_vivo = IntVar(master=root3, value=-1)
    ttk.Radiobutton(frame_puerpera, text="Sim", value=1, variable=nasceu_vivo).grid(column=0, row=1)
    ttk.Radiobutton(frame_puerpera, text="Não", value=0, variable=nasceu_vivo).grid(column=1, row=1)

    # Local do parto
    ttk.Label(frame_puerpera, text="Local do parto:").grid(column=0, row=2, columnspan=2, pady=(10, 0))
    local_parto = ttk.Combobox(frame_puerpera, values=HOSPITAIS, width=60, state="readonly")
    local_parto.grid(column=0, row=3, columnspan=2, sticky="w")

    # Campo de texto exibido apenas se o local for "Outro"
    frame_outro = ttk.Frame(frame_puerpera)
    frame_outro.grid(column=0, row=4, columnspan=2, sticky="w", pady=(10, 0))

    ttk.Label(frame_outro, text="Qual outro local?").grid(column=0, row=0, sticky="w")
    outro_local = ttk.Entry(frame_outro, width=60)
    outro_local.grid(column=0, row=1, sticky="w")

    frame_outro.grid_remove()  # começa escondido

    def ao_selecionar_local(event=None):
        if local_parto.get() == "Outro":
            frame_outro.grid()
        else:
            frame_outro.grid_remove()
            outro_local.delete(0, END)  # limpa o texto se trocar de opção

    local_parto.bind("<<ComboboxSelected>>", ao_selecionar_local)

    frame_puerpera.grid_remove()  # começa escondido

    def ao_selecionar_classificacao(event=None):
        if classificacao.get() == "Puérpera":
            frame_puerpera.grid()          # mostra
        else:
            frame_puerpera.grid_remove()   # esconde

    classificacao.bind("<<ComboboxSelected>>", ao_selecionar_classificacao)

    root3.mainloop()