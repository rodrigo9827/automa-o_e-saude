from datetime import date
from tkinter import *
from tkinter import ttk, messagebox
import tratando_csv
import monitora_gestante

LARGURA_LABEL = 30


def start(parent=None, enfermeira_inicial="", ao_salvar=None):
    """Abre a janela 'Registrar Busca Ativa'.
    parent: a janela principal (abre como janela filha). Sem parent, abre sozinha (para testes).
    ao_salvar: função chamada depois de salvar (a principal usa para atualizar as observações)."""
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
    rotulo("Idade Gestacional (semanas):", 4)
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

    # Observações (caixa de várias linhas)
    ttk.Label(frm, text="Observações:", width=LARGURA_LABEL).grid(column=0, row=8, sticky="nw", pady=4)
    observacoes = Text(frm, width=60, height=4, wrap="word")
    observacoes.grid(column=1, row=8, sticky="w", pady=4)

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
        if not texto_ig.isdigit() or not 0 <= int(texto_ig) <= 45:
            erros.append("Idade gestacional deve ser um número de semanas (0 a 45).")

        texto_retorno = data_retorno.get().strip()
        retorno = monitora_gestante.ler_data(texto_retorno) if texto_retorno else None
        if texto_retorno and retorno is None:
            erros.append("Data de retorno inválida (use dd/mm/aaaa) ou deixe vazia.")

        if alto_risco.get() == -1:
            erros.append("Responda se é paciente de alto risco.")

        if erros:
            messagebox.showwarning("Faltam dados", "\n".join(erros), parent=janela)
            return

        # retorno vazio: calcula pela mesma regra da VIEW
        if retorno is None:
            retorno = monitora_gestante.calcular_retorno(contato, int(texto_ig))

        dados = {
            "enfermeira": nome.get(),
            "gestante": gestante.get().strip(),
            "cns": cns.get().strip(),
            "data_contato": contato.strftime("%d/%m/%Y"),
            "ig_semanas": texto_ig,
            "data_retorno": retorno.strftime("%d/%m/%Y"),
            "alto_risco": alto_risco.get(),
            "observacoes": observacoes.get("1.0", END).strip(),
        }

        try:
            monitora_gestante.salvar_busca_ativa(dados)
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

        messagebox.showinfo("Salvo",
                            f"Busca ativa registrada.\nRetorno: {dados['data_retorno']}",
                            parent=janela)
        janela.destroy()
        if ao_salvar:
            ao_salvar()       # avisa a tela principal para mostrar a observação nova

    ttk.Button(frm, text="Enviar para Enfermeira", command=enviar).grid(
        column=0, row=9, columnspan=2, pady=(15, 0))

    if parent is None:
        janela.mainloop()
    else:
        janela.focus_set()
