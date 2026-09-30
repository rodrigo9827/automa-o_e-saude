from datetime import date
from tkinter import *
from tkinter import ttk, messagebox
import tratando_csv
import monitora_gestante

# Nomes dos teleoperadores (por enquanto fixos aqui; "Nenhum" = atendimento sem teleoperador)
TELEOPERADORES = [
    "Nenhum",
    "Rodrigo",
    "Beatriz",
    "Ana",
    "Marina",
    "Deivide",
    "Fernando",
]

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

def linha_sim_nao(pai, texto, linha, janela, comando=None):
    """Pergunta com Radio Sim/Não. Retorna o IntVar (1 = Sim, 0 = Não, -1 = sem resposta)."""
    ttk.Label(pai, text=texto, width=LARGURA_LABEL).grid(column=0, row=linha, sticky="w", pady=4)
    var = IntVar(master=janela, value=-1)
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


def caixa_observacoes(pai, linha):
    """Label + caixa de texto de várias linhas para as observações. Retorna o Text."""
    ttk.Label(pai, text="Observações:", width=LARGURA_LABEL).grid(column=0, row=linha, sticky="nw", pady=4)
    caixa = Text(pai, width=60, height=4, wrap="word")
    caixa.grid(column=1, row=linha, sticky="w", pady=4)
    return caixa


def start_forms(parent=None, cns_inicial="", enfermeira_inicial="", ao_salvar=None,
                cpf_inicial="", nome_inicial=""):
    """Abre o formulário 'Finalizar Atendimento'.
    parent: a janela principal (abre como janela filha). Sem parent, abre sozinho (para testes).
    cns_inicial / cpf_inicial / nome_inicial / enfermeira_inicial: já vêm preenchidos
    com a gestante selecionada na lista. Precisa de CNS ou CPF (sem CNS, a busca é pelo CPF).
    ao_salvar: função chamada depois de salvar (a principal usa para atualizar as observações)."""
    if parent is None:
        janela = Tk()
    else:
        janela = Toplevel(parent)
        janela.transient(parent)          # fica sempre na frente da janela principal
    janela.title("Finalizar Atendimento")

    frm = ttk.Frame(janela, padding=10)
    frm.grid()

    # ================= CAMPOS FIXOS =================

    enfermeiras = tratando_csv.listar_enfermeiras()
    nome = linha_combo(frm, "Enfermeira (o):", enfermeiras, 0, largura=45)
    if enfermeira_inicial in enfermeiras:
        nome.set(enfermeira_inicial)

    teleoperador = linha_combo(frm, "Teleoperador (a):", TELEOPERADORES, 1, largura=25)

    def atualizar_contato():
        resposta = conseguiu_contato.get()
        mostrar(frame_sem_contato, resposta == 0)
        mostrar(frame_contato, resposta == 1)

    conseguiu_contato = linha_sim_nao(frm, "Conseguiu o contato?", 2, janela, comando=atualizar_contato)

    # identificação da gestante (sempre visível): CNS, ou CPF quando não houver CNS
    nome_gestante = linha_texto(frm, "Nome da Gestante:", 3, largura=45)
    nome_gestante.insert(0, nome_inicial or "")

    cns = linha_texto(frm, "CNS da Gestante (15 números):", 4, largura=25)
    cns.insert(0, cns_inicial or "")

    cpf = linha_texto(frm, "CPF da Gestante (11 números):", 5, largura=25)
    cpf.insert(0, cpf_inicial or "")

    numero = linha_texto(frm, "Número do contato:", 6, largura=25)

    data_contato = linha_texto(frm, "Data do contato (dd/mm/aaaa):", 7, largura=12)
    data_contato.insert(0, date.today().strftime("%d/%m/%Y"))    # já vem com hoje

    # ================= SE NÃO CONSEGUIU O CONTATO =================

    frame_sem_contato = ttk.Frame(frm)
    frame_sem_contato.grid(column=0, row=8, columnspan=2, sticky="w", pady=(10, 0))
    motivo = linha_combo(frame_sem_contato, "Qual o motivo?", MOTIVOS_SEM_CONTATO, 0)
    frame_sem_contato.grid_remove()

    # ================= SE CONSEGUIU O CONTATO =================

    frame_contato = ttk.Frame(frm)
    frame_contato.grid(column=0, row=9, columnspan=2, sticky="w", pady=(10, 0))

    classificacao = linha_combo(frame_contato, "Classificação:", ["Gestante", "Puérpera", "Aborto"], 0, largura=25)

    # ---------- Frame: PUÉRPERA ----------
    frame_puerpera = ttk.Frame(frame_contato)
    frame_puerpera.grid(column=0, row=1, columnspan=2, sticky="w")

    nasceu_vivo = linha_sim_nao(frame_puerpera, "Nasceu vivo?", 0, janela)

    local_parto = linha_combo(frame_puerpera, "Local do parto:", HOSPITAIS, 1, largura=60)
    cont_outro = container_condicional(frame_puerpera, 2)
    outro_local = linha_texto(cont_outro, "Qual outro local?", 0, largura=60)

    def ao_selecionar_local(event=None):
        eh_outro = local_parto.get() == "Outro"
        mostrar(cont_outro, eh_outro)
        if not eh_outro:
            outro_local.delete(0, END)

    local_parto.bind("<<ComboboxSelected>>", ao_selecionar_local)

    bebe_risco = linha_sim_nao(frame_puerpera, "É um bebê de risco?", 3, janela)
    obito_neonatal = linha_sim_nao(frame_puerpera, "Óbito neonatal?", 4, janela)
    obito_materno = linha_sim_nao(frame_puerpera, "Houve óbito materno?", 5, janela)

    def atualizar_violencia():
        teve = houve_violencia.get() == 1
        mostrar(cont_violencia, teve)
        if not teve:
            tipo_violencia.set("")

    houve_violencia = linha_sim_nao(frame_puerpera, "Houve violência?", 6, janela,
                                    comando=atualizar_violencia)
    cont_violencia = container_condicional(frame_puerpera, 7)
    tipo_violencia = linha_combo(cont_violencia, "Qual violência?", TIPOS_VIOLENCIA, 0)

    tipo_parto = linha_combo(frame_puerpera, "Tipo de parto:", TIPOS_PARTO, 8)

    def atualizar_risco_puerpera():
        teve = risco_gest_puerpera.get() == 1
        mostrar(cont_risco_puerpera, teve)
        if not teve:
            qual_risco_puerpera.delete(0, END)

    risco_gest_puerpera = linha_sim_nao(frame_puerpera, "Teve risco gestacional?", 9, janela,
                                        comando=atualizar_risco_puerpera)
    cont_risco_puerpera = container_condicional(frame_puerpera, 10)
    qual_risco_puerpera = linha_texto(cont_risco_puerpera, "Qual?", 0, largura=60)

    frame_puerpera.grid_remove()

    # ---------- Frame: GESTANTE ----------
    frame_gestante = ttk.Frame(frame_contato)
    frame_gestante.grid(column=0, row=1, columnspan=2, sticky="w")

    gestante_risco = linha_sim_nao(frame_gestante, "É gestante de risco?", 0, janela)
    pre_natal = linha_sim_nao(frame_gestante, "Acompanhamento pré-natal?", 1, janela)

    # Atualização da IG e do retorno: aparecem na lista da tela principal (ambos opcionais)
    ig_gestante = linha_texto(frame_gestante, "Idade Gestacional \n(ss+dd, ex.: 30+2):", 2, largura=8)
    retorno_gestante = linha_texto(frame_gestante, "Data de retorno (opcional):", 3, largura=12)
    ttk.Label(frame_gestante, text="Se informar a IG e deixar o retorno vazio, o retorno é calculado pela regra da IG.",
              foreground="gray").grid(column=1, row=4, sticky="w")

    frame_gestante.grid_remove()

    # ---------- ABORTO: sem campos extras ----------

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
    sifilis = linha_sim_nao(frame_contato, "Tratamento de sífilis?", 2, janela)

    frame_contato.grid_remove()     # só aparece quando marcar "Sim" em "Conseguiu o contato?"


    # ================= CASO CRÍTICO (sempre aparece) =================

    def atualizar_caso_critico():
        critico = caso_critico.get() == 1
        mostrar(cont_caso_critico, critico)
        if not critico:
            qual_caso_critico.delete(0, END)

    caso_critico = linha_sim_nao(frm, "Caso crítico?", 10, janela, comando=atualizar_caso_critico)
    cont_caso_critico = container_condicional(frm, 11)
    qual_caso_critico = linha_texto(cont_caso_critico, "Qual o caso crítico?", 0, largura=60)


    # ================= OBSERVAÇÕES (sempre aparece) =================

    observacoes = caixa_observacoes(frm, 12)


    # ================= VALIDAÇÃO =================

    def validar(dados):
        """Devolve a lista de problemas encontrados (lista vazia = tudo certo)."""
        erros = []
        if not dados["enfermeira"]:
            erros.append("Escolha a enfermeira.")
        if not dados["teleoperador"]:
            erros.append("Escolha o teleoperador (ou 'Nenhum').")
        erros += monitora_gestante.validar_identificacao(dados["cns"], cpf.get(), dados["gestante"])
        data = monitora_gestante.ler_data(dados["data_contato"])
        if data is None:
            erros.append("Data do contato inválida (use dd/mm/aaaa).")
        elif monitora_gestante.data_futura(data):
            erros.append("A data do contato não pode ser depois de hoje.")
        if dados["caso_critico"] == -1:
            erros.append("Responda se é caso crítico.")
        elif dados["caso_critico"] == 1 and not dados["qual_caso_critico"]:
            erros.append("Informe qual é o caso crítico.")
        if dados["conseguiu_contato"] == -1:
            erros.append("Responda se conseguiu o contato.")
        elif dados["conseguiu_contato"] == 0 and not dados.get("motivo_sem_contato"):
            erros.append("Escolha o motivo de não ter conseguido o contato.")
        elif dados["conseguiu_contato"] == 1:
            if not dados.get("classificacao"):
                erros.append("Escolha a classificação (Gestante, Puérpera ou Aborto).")
            if dados.get("classificacao") == "Gestante":
                ig_txt = dados.get("ig_semanas", "")
                if ig_txt and monitora_gestante.ler_ig(ig_txt) is None:
                    erros.append("Idade gestacional deve estar no formato semanas+dias, "
                                 "ex.: 30+2 (semanas 0 a 45, dias 0 a 6).")
                ret_txt = dados.get("data_retorno", "")
                if ret_txt:
                    retorno = monitora_gestante.ler_data(ret_txt)
                    if retorno is None:
                        erros.append("Data de retorno inválida (use dd/mm/aaaa) ou deixe vazia.")
                    elif data is not None and retorno < data:
                        erros.append("A data de retorno não pode ser antes da data do contato.")
            if dados.get("local_parto") == "Outro" and not dados.get("outro_local"):
                erros.append("Informe qual foi o outro local do parto.")
            if dados.get("houve_violencia") == 1 and not dados.get("tipo_violencia"):
                erros.append("Escolha qual foi a violência.")
            if dados.get("risco_gestacional") == 1 and not dados.get("qual_risco"):
                erros.append("Informe qual foi o risco gestacional.")
        return erros

    # ================= BOTÃO ENVIAR =================

    def enviar():
        dados = {
            "enfermeira": nome.get(),
            "teleoperador": teleoperador.get(),
            "conseguiu_contato": conseguiu_contato.get(),
            "cns": cns.get().strip(),
            "cpf": monitora_gestante.so_digitos(cpf.get()),
            "gestante": nome_gestante.get().strip(),
            "numero": numero.get().strip(),
            "data_contato": data_contato.get().strip(),
            "caso_critico": caso_critico.get(),
            "qual_caso_critico": qual_caso_critico.get().strip() if caso_critico.get() == 1 else "",
            "observacoes": observacoes.get("1.0", END).strip(),
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
                    "outro_local": outro_local.get().strip(),
                    "bebe_risco": bebe_risco.get(),
                    "obito_neonatal": obito_neonatal.get(),
                    "obito_materno": obito_materno.get(),
                    "houve_violencia": houve_violencia.get(),
                    "tipo_violencia": tipo_violencia.get(),
                    "tipo_parto": tipo_parto.get(),
                    "risco_gestacional": risco_gest_puerpera.get(),
                    "qual_risco": qual_risco_puerpera.get().strip(),
                })
            elif classificacao.get() == "Gestante":
                dados.update({
                    "gestante_risco": gestante_risco.get(),
                    "pre_natal": pre_natal.get(),
                    "ig_semanas": ig_gestante.get().strip(),
                    "data_retorno": retorno_gestante.get().strip(),
                })

        # --- validação: não salva registro incompleto ---
        erros = validar(dados)
        if erros:
            messagebox.showwarning("Faltam dados", "\n".join(erros), parent=janela)
            return

        # IG informada e retorno vazio: calcula pela mesma regra da VIEW
        if dados.get("data_retorno"):
            dados["data_retorno"] = monitora_gestante.ler_data(dados["data_retorno"]).strftime("%d/%m/%Y")
        elif dados.get("ig_semanas"):
            contato = monitora_gestante.ler_data(dados["data_contato"])
            dados["data_retorno"] = monitora_gestante.calcular_retorno(
                contato, *monitora_gestante.ler_ig(dados["ig_semanas"])).strftime("%d/%m/%Y")
        if dados.get("ig_semanas"):          # guarda sempre como ss+dd
            dados["ig_semanas"] = "{}+{}".format(*monitora_gestante.ler_ig(dados["ig_semanas"]))

        # --- salva nos CSVs (o banco de dados NÃO é alterado) ---
        try:
            avisos = monitora_gestante.salvar(dados)
        except PermissionError:
            messagebox.showerror(
                "Arquivo em uso",
                "Não foi possível salvar: o arquivo stg.Monitora_Gestante.csv está aberto "
                "em outro programa (ex.: Excel). Feche-o e clique em Enviar de novo.",
                parent=janela,
            )
            return
        except ValueError as erro:          # CSV de versão antiga
            messagebox.showerror("Arquivo antigo", str(erro), parent=janela)
            return

        if avisos:
            messagebox.showwarning("Salvo com aviso", "\n\n".join(avisos), parent=janela)
        else:
            messagebox.showinfo("Salvo", "Atendimento registrado com sucesso.", parent=janela)
        janela.destroy()      # fecha: o próximo atendimento começa com o formulário limpo
        if ao_salvar:
            # avisa a tela principal qual gestante foi salva (pelo CNS ou, sem CNS, pelo CPF)
            ao_salvar(monitora_gestante.chave(dados["cns"], dados["cpf"]))

    ttk.Button(frm, text="Enviar", command=enviar).grid(column=0, row=13, columnspan=2, pady=(15, 0))

    if parent is None:
        janela.mainloop()
    else:
        janela.focus_set()
