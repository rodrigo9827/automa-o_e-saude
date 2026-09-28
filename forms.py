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

MOTIVOS_SEM_CONTATO = [
    "Não existe",
    "Caixa postal",
    "Não Atende",
    "Desconhece",
    "Sem Número",
    "Chamada não completada",
]

TIPOS_VIOLENCIA = [
    "Obstétrica",
    "Doméstica",
    "Verbal",
    "Médica",
    "Psicológica",
    "Física",
    "Sexual",
]

TIPOS_PARTO = ["Vaginal", "Cesárea", "Forceps", "Domiciliar"]

LARGURA_LABEL = 30


# ---------- funções auxiliares para não repetir código ----------

def linha_sim_nao(pai, texto, linha, root, comando=None):
    """Pergunta com Radio Sim/Não. Retorna o IntVar (1 = Sim, 0 = Não, -1 = sem resposta)."""
    ttk.Label(pai, text=texto, width=LARGURA_LABEL).grid(column=0, row=linha, sticky="w", pady=4)
    var = IntVar(master=root, value=-1)
    opcoes = ttk.Frame(pai)
    opcoes.grid(column=1, row=linha, sticky="w")
    ttk.Radiobutton(opcoes, text="Sim", value=1, variable=var, command=comando).grid(column=0, row=0)
    ttk.Radiobutton(opcoes, text="Não", value=0, variable=var, command=comando).grid(column=1, row=0, padx=(10, 0))
    return var


def linha_combo(pai, texto, valores, linha, largura=30):
    """Label + Combobox (somente leitura). Retorna o Combobox."""
    ttk.Label(pai, text=texto, width=LARGURA_LABEL).grid(column=0, row=linha, sticky="w", pady=4)
    combo = ttk.Combobox(pai, values=valores, width=largura, state="readonly")
    combo.grid(column=1, row=linha, sticky="w")
    return combo


def linha_texto(pai, texto, linha, largura=40):
    """Label + caixa de texto. Retorna o Entry."""
    ttk.Label(pai, text=texto, width=LARGURA_LABEL).grid(column=0, row=linha, sticky="w", pady=4)
    entrada = ttk.Entry(pai, width=largura)
    entrada.grid(column=1, row=linha, sticky="w")
    return entrada


def container_condicional(pai, linha):
    """Frame que começa escondido; serve para campos que só aparecem se algo for marcado."""
    f = ttk.Frame(pai)
    f.grid(column=0, row=linha, columnspan=2, sticky="w")
    f.grid_remove()
    return f


def mostrar(frame, condicao):
    if condicao:
        frame.grid()
    else:
        frame.grid_remove()


def start_forms():
    root3 = Tk()
    frm = ttk.Frame(root3, padding=10)
    frm.grid()

    # ================= CAMPOS FIXOS =================

    # Selecionar Enfermeira
    ttk.Label(frm, text="Enfermeira (o):").grid(column=0, row=0, sticky="w")
    nome = ttk.Combobox(frm, values=tratando_csv.listar_enfermeiras(), state="readonly", width=45)
    nome.grid(column=1, row=0, sticky="w")

    # Conseguiu o contato?
    ttk.Label(frm, text="Conseguiu o contato? ").grid(column=0, row=1)

    def atualizar_contato():
        resposta = conseguiu_contato.get()
        mostrar(frame_sem_contato, resposta == 0)
        mostrar(frame_contato, resposta == 1)

    conseguiu_contato = IntVar(master=root3, value=-1)
    ttk.Radiobutton(frm, text="Sim", value=1, variable=conseguiu_contato,
                    command=atualizar_contato).grid(column=0, row=2)
    ttk.Radiobutton(frm, text="Não", value=0, variable=conseguiu_contato,
                    command=atualizar_contato).grid(column=1, row=2)

    # CNS
    ttk.Label(frm, text="CNS da Gestante (apenas números): ").grid(column=0, row=3)
    cns = ttk.Entry(frm)
    cns.grid(column=1, row=3)

    # Número de contato
    ttk.Label(frm, text="Número do contato: ").grid(column=0, row=4)
    numero = ttk.Entry(frm)
    numero.grid(column=1, row=4)

    # ================= SE NÃO CONSEGUIU O CONTATO =================

    frame_sem_contato = ttk.Frame(frm)
    frame_sem_contato.grid(column=0, row=5, columnspan=2, sticky="w", pady=(10, 0))

    motivo = linha_combo(frame_sem_contato, "Qual o motivo?", MOTIVOS_SEM_CONTATO, 0)
    frame_sem_contato.grid_remove()

    # ================= SE CONSEGUIU O CONTATO =================

    frame_contato = ttk.Frame(frm)
    frame_contato.grid(column=0, row=6, columnspan=2, sticky="w", pady=(10, 0))

    # Classificação
    classificacao = linha_combo(frame_contato, "Classificação:", ["Gestante", "Puérpera", "Aborto"], 0, largura=25)

    # ---------- Frame: PUÉRPERA ----------
    frame_puerpera = ttk.Frame(frame_contato)
    frame_puerpera.grid(column=0, row=1, columnspan=2, sticky="w")

    nasceu_vivo = linha_sim_nao(frame_puerpera, "Nasceu vivo?", 0, root3)

    # Local do parto (+ campo de texto se "Outro")
    local_parto = linha_combo(frame_puerpera, "Local do parto:", HOSPITAIS, 1, largura=60)

    cont_outro = container_condicional(frame_puerpera, 2)
    outro_local = linha_texto(cont_outro, "Qual outro local?", 0, largura=60)

    def ao_selecionar_local(event=None):
        eh_outro = local_parto.get() == "Outro"
        mostrar(cont_outro, eh_outro)
        if not eh_outro:
            outro_local.delete(0, END)

    local_parto.bind("<<ComboboxSelected>>", ao_selecionar_local)

    bebe_risco = linha_sim_nao(frame_puerpera, "É um bebê de risco?", 3, root3)
    obito_neonatal = linha_sim_nao(frame_puerpera, "Óbito neonatal?", 4, root3)
    obito_materno = linha_sim_nao(frame_puerpera, "Houve óbito materno?", 5, root3)

    # Violência (+ qual, se sim)
    def atualizar_violencia():
        teve = houve_violencia.get() == 1
        mostrar(cont_violencia, teve)
        if not teve:
            tipo_violencia.set("")

    houve_violencia = linha_sim_nao(frame_puerpera, "Houve violência?", 6, root3,
                                    comando=atualizar_violencia)
    cont_violencia = container_condicional(frame_puerpera, 7)
    tipo_violencia = linha_combo(cont_violencia, "Qual violência?", TIPOS_VIOLENCIA, 0)

    tipo_parto = linha_combo(frame_puerpera, "Tipo de parto:", TIPOS_PARTO, 8)

    # Risco gestacional (+ qual, se sim)
    def atualizar_risco_puerpera():
        teve = risco_gest_puerpera.get() == 1
        mostrar(cont_risco_puerpera, teve)
        if not teve:
            qual_risco_puerpera.delete(0, END)

    risco_gest_puerpera = linha_sim_nao(frame_puerpera, "Teve risco gestacional?", 9, root3,
                                        comando=atualizar_risco_puerpera)
    cont_risco_puerpera = container_condicional(frame_puerpera, 10)
    qual_risco_puerpera = linha_texto(cont_risco_puerpera, "Qual?", 0, largura=60)

    frame_puerpera.grid_remove()

    # ---------- Frame: GESTANTE ----------
    frame_gestante = ttk.Frame(frame_contato)
    frame_gestante.grid(column=0, row=1, columnspan=2, sticky="w")

    gestante_risco = linha_sim_nao(frame_gestante, "É gestante de risco?", 0, root3)
    pre_natal = linha_sim_nao(frame_gestante, "Acompanhamento pré-natal?", 1, root3)

    frame_gestante.grid_remove()

    # ---------- ABORTO: sem campos extras, só o botão Enviar ----------

    frames_por_classificacao = {
        "Puérpera": frame_puerpera,
        "Gestante": frame_gestante,
    }

    def ao_selecionar_classificacao(event=None):
        escolhida = classificacao.get()
        for nome_class, frame in frames_por_classificacao.items():
            mostrar(frame, nome_class == escolhida)

    classificacao.bind("<<ComboboxSelected>>", ao_selecionar_classificacao)

    # ---------- Comum a todas as classificações ----------
    sifilis = linha_sim_nao(frame_contato, "Tratamento de sífilis?", 2, root3)

    # ================= BOTÃO ENVIAR =================

    def enviar():
        dados = {
            "enfermeira": nome.get(),
            "conseguiu_contato": conseguiu_contato.get(),
            "cns": cns.get(),
            "numero": numero.get(),
        }

        if conseguiu_contato.get() == 0:
            dados["motivo_sem_contato"] = motivo.get()

        elif conseguiu_contato.get() == 1:
            dados["classificacao"] = classificacao.get()
            dados["tratamento_sifilis"] = sifilis.get()

            if classificacao.get() == "Puérpera":
                dados.update({
                    "nasceu_vivo": nasceu_vivo.get(),
                    "local_parto": local_parto.get(),
                    "outro_local": outro_local.get(),
                    "bebe_risco": bebe_risco.get(),
                    "obito_neonatal": obito_neonatal.get(),
                    "obito_materno": obito_materno.get(),
                    "houve_violencia": houve_violencia.get(),
                    "tipo_violencia": tipo_violencia.get(),
                    "tipo_parto": tipo_parto.get(),
                    "risco_gestacional": risco_gest_puerpera.get(),
                    "qual_risco": qual_risco_puerpera.get(),
                })
            elif classificacao.get() == "Gestante":
                dados.update({
                    "gestante_risco": gestante_risco.get(),
                    "pre_natal": pre_natal.get(),
                })

        # TODO: trocar pelo salvamento real (ex.: uma função do tratando_csv)
        print(dados)

    ttk.Button(frm, text="Enviar", command=enviar).grid(column=0, row=7, columnspan=2, pady=(15, 0))

    root3.mainloop()