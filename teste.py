import tkinter as tk

def pegar_valor():
    # Obtém o texto digitado no Entry usando o método .get()
    texto_digitado = entrada.get()
    print(f"O valor digitado foi: {texto_digitado}")
    # Você também pode atualizar um Label ou salvar o dado em uma variável global/externa aqui

# Criar a janela principal
janela = tk.Tk()
janela.title("Exemplo Entry Tkinter")
janela.geometry("300x150")

# Criar o campo de entrada (Entry)
entrada = tk.Entry(janela, width=25)
entrada.pack(pady=20)

# Criar um botão que chama a função para resgatar o valor
botao = tk.Button(janela, text="Receber Dado", command=pegar_valor)
botao.pack()

# Iniciar o loop da janela
janela.mainloop()
