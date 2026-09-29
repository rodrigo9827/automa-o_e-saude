from datetime import date
from tkinter import *
from tkinter import ttk, messagebox
import tratando_csv
import monitora_gestante

LARGURA_LABEL = 30


def start(parent=None, enfermeira_inicial="", ao_salvar=None):
    """Abre a janela 'Registrar Busca Ativa'.
    parent: a janela principal (abre como janela filha). Sem parent, abre sozinha (para testes).
    Serve para cadastrar gestantes NOVAS para a enfermeira: só a enfermeira vem preenchida.
    ao_salvar: função chamada depois de salvar; recebe o CNS salvo (a principal atualiza a lista)."""
    if parent is None:
        janela = Tk()
    else:
        janela = Toplevel(parent)
        janela.transient(parent)
    janela.title("Registrar Busca Ativa")

    frm = ttk.Frame(janela, padding=10)
    frm.grid()

    def rotulo(texto, linha):
        ttk.Label(frm, text=texto, width=LARGURA_LABEL).grid(column=0, row=linha, sticky="w", pady=4)

    # Enfermeira
    rotulo("Enfermeira (o):", 0)
    enfermeiras = tratando_csv.listar_enfermeiras()
    nome = ttk.Combobox(frm, values=enfermeiras, state="readonly", width=45)
    nome.grid(column=1, row=0, sticky="w")
    if enfermeira_inicial in enfermeiras:
        nome.set(enfermeira_inicial)

    # Nome da gestante
    rotulo("Nome da Gestante:", 1)
    gestante = ttk.Entry(frm, width=45)
    gestante.grid(column=1, row=1, sticky="w")

    # CNS
    rotulo("CNS da Gestante (15 números):", 2)
    cns = ttk.Entry(frm, width=25)
    cns.grid(column=1, row=2, sticky="w")

    # Data do contato (já vem com a data de hoje)
    rotulo("Data do Contato (dd/mm/aaaa):", 3)
    data_ctt = ttk.Entry(frm, width=15)
    data_ctt.grid(column=1, row=3, sticky="w")
    data_ctt.insert(0, date.today().strftime("%d/%m/%Y"))

    # Idade gestacional
    rotulo("Idade Gestacional (ss+dd, ex.: 30+2):", 4)
    ig = ttk.Entry(frm, width=8)
    ig.grid(column=1, row=4, sticky="w")

    # Data do retorno (opcional: se ficar vazia, é calculada pela regra)
    rotulo("Data de retorno (opcional):", 5)
    data_retorno = ttk.Entry(frm, width=15)
    data_retorno.grid(column=1, row=5, sticky="w")
    ttk.Label(frm, text="Se ficar vazia, é calculada pela regra da IG.",
              foreground="gray").grid(column=1, row=6, sticky="w")

    # Alto risco (agora com variável própria)
    rotulo("Paciente de Alto Risco?", 7)
    alto_risco = IntVar(master=janela, value=-1)
    opcoes = ttk.Frame(frm)
    opcoes.grid(column=1, row=7, sticky="w")
    ttk.Radiobutton(opcoes, text="Sim", value=1, variable=alto_risco).grid(column=0, row=0)
    ttk.Radiobutton(opcoes, text="Não", value=0, variable=alto_risco).grid(column=1, row=0, padx=(10, 0))

    # Caso crítico (se "Sim", aparece o campo para descrever qual é)
    def atualizar_caso_critico():
        if caso_critico.get() == 1:
            cont_caso_critico.grid()
        else:
            cont_caso_critico.grid_remove()
            qual_caso_critico.delete(0, END)

    rotulo("Caso crítico?", 8)
    caso_critico = IntVar(master=janela, value=-1)
    opcoes_critico = ttk.Frame(frm)
    opcoes_critico.grid(column=1, row=8, sticky="w")
    ttk.Radiobutton(opcoes_critico, text="Sim", value=1, variable=caso_critico,
                    command=atualizar_caso_critico).grid(column=0, row=0)
    ttk.Radiobutton(opcoes_critico, text="Não", value=0, variable=caso_critico,
                    command=atualizar_caso_critico).grid(column=1, row=0, padx=(10, 0))

    cont_caso_critico = ttk.Frame(frm)
    cont_caso_critico.grid(column=0, row=9, columnspan=2, sticky="w")
    rotulo_qual = ttk.Label(cont_caso_critico, text="Qual o caso crítico?", width=LARGURA_LABEL)
    rotulo_qual.grid(column=0, row=0, sticky="w", pady=4)
    qual_caso_critico = ttk.Entry(cont_caso_critico, width=60)
    qual_caso_critico.grid(column=1, row=0, sticky="w")
    cont_caso_critico.grid_remove()

    # Classificação da gestante: só quem é "Gestante" entra na lista da tela principal.
    # Puérpera e Aborto ficam apenas salvos nos CSVs.
    def marcou_gestante():
        if gestante_gestante.get():
            gestante_puerpera.set(0)
            gestante_aborto.set(0)

    def marcou_outra():
        if gestante_puerpera.get() or gestante_aborto.get():
            gestante_gestante.set(0)

    rotulo("Classificação da gestante:", 10)
    gestante_gestante = IntVar(master=janela, value=1)
    gestante_puerpera = IntVar(master=janela, value=0)
    gestante_aborto = IntVar(master=janela, value=0)
    opcoes_class = ttk.Frame(frm)
    opcoes_class.grid(column=1, row=10, sticky="w")
    ttk.Checkbutton(opcoes_class, text="Gestante", variable=gestante_gestante,
                    command=marcou_gestante).grid(column=0, row=0)
    ttk.Checkbutton(opcoes_class, text="Puérpera", variable=gestante_puerpera,
                    command=marcou_outra).grid(column=1, row=0, padx=(10, 0))
    ttk.Checkbutton(opcoes_class, text="Aborto", variable=gestante_aborto,
                    command=marcou_outra).grid(column=2, row=0, padx=(10, 0))

    # Observações (caixa de várias linhas)
    ttk.Label(frm, text="Observações:", width=LARGURA_LABEL).grid(column=0, row=11, sticky="nw", pady=4)
    observacoes = Text(frm, width=60, height=4, wrap="word")
    observacoes.grid(column=1, row=11, sticky="w", pady=4)

    def enviar():
        erros = []

        if not nome.get():
            erros.append("Escolha a enfermeira.")
        if not gestante.get().strip():
            erros.append("Informe o nome da gestante.")
        if not monitora_gestante.cns_valido(cns.get()):
            erros.append("O CNS precisa ter exatamente 15 números.")

        contato = monitora_gestante.ler_data(data_ctt.get())
        if contato is None:
            erros.append("Data do contato inválida (use dd/mm/aaaa).")
        elif monitora_gestante.data_futura(contato):
            erros.append("A data do contato não pode ser depois de hoje.")

        texto_ig = ig.get().strip()
        ig_lida = monitora_gestante.ler_ig(texto_ig)
        if not texto_ig or ig_lida is None:
            erros.append("Idade gestacional deve estar no formato semanas+dias, "
                         "ex.: 30+2 (semanas 0 a 45, dias 0 a 6).")

        texto_retorno = data_retorno.get().strip()
        retorno = monitora_gestante.ler_data(texto_retorno) if texto_retorno else None
        if texto_retorno and retorno is None:
            erros.append("Data de retorno inválida (use dd/mm/aaaa) ou deixe vazia.")

        if alto_risco.get() == -1:
            erros.append("Responda se é paciente de alto risco.")

        if caso_critico.get() == -1:
            erros.append("Responda se é caso crítico.")
        elif caso_critico.get() == 1 and not qual_caso_critico.get().strip():
            erros.append("Informe qual é o caso crítico.")

        if not (gestante_gestante.get() or gestante_puerpera.get() or gestante_aborto.get()):
            erros.append("Marque a classificação da gestante (Gestante, Puérpera ou Aborto).")

        if erros:
            messagebox.showwarning("Faltam dados", "\n".join(erros), parent=janela)
            return

        # retorno vazio: calcula pela mesma regra da VIEW
        if retorno is None:
            retorno = monitora_gestante.calcular_retorno(contato, *ig_lida)

        dados = {
            "enfermeira": nome.get(),
            "gestante": gestante.get().strip(),
            "cns": cns.get().strip(),
            "data_contato": contato.strftime("%d/%m/%Y"),
            "ig_semanas": f"{ig_lida[0]}+{ig_lida[1]}",
            "data_retorno": retorno.strftime("%d/%m/%Y"),
            "alto_risco": alto_risco.get(),
            "gestante_gestante": gestante_gestante.get(),     # 1 = marcado
            "gestante_puerpera": gestante_puerpera.get(),
            "gestante_aborto": gestante_aborto.get(),
            "caso_critico": caso_critico.get(),
            "qual_caso_critico": qual_caso_critico.get().strip() if caso_critico.get() == 1 else "",
            "observacoes": observacoes.get("1.0", END).strip(),
        }

        try:
            avisos = monitora_gestante.salvar_busca_ativa(dados)
        except PermissionError:
            messagebox.showerror(
                "Arquivo em uso",
                "Não foi possível salvar: o arquivo stg.Busca_Ativa.csv está aberto "
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
            messagebox.showinfo("Salvo",
                                f"Busca ativa registrada.\nRetorno: {dados['data_retorno']}",
                                parent=janela)
        janela.destroy()
        if ao_salvar:
            ao_salvar(dados["cns"])   # avisa a tela principal para atualizar a lista

    ttk.Button(frm, text="Enviar para Enfermeira", command=enviar).grid(
        column=0, row=12, columnspan=2, pady=(15, 0))

    if parent is None:
        janela.mainloop()
    else:
        janela.focus_set()
