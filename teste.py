import tkinter as tk
from tkinter import messagebox

def mostrar_resultados():
    # Coleta os valores atuais
    status_checkbox = "Sim" if valor_check.get() else "Não"
    status_radio = valor_radio.get()
    
    messagebox.showinfo("Resultados", f"Checkbox selecionado? {status_checkbox}\nRadio selecionado: {status_radio}")

# Configuração da janela principal
janela = tk.Tk()
janela.title("Exemplo Sim ou Não")
janela.geometry("300x250")

# --- 1. EXEMPLO COM CHECKBOX (Checkbutton) ---
tk.Label(janela, text="Exemplo Checkbox:", font=("Arial", 10, "bold")).pack(pady=(10, 0))

valor_check = tk.BooleanVar()  # Guarda True (marcado) ou False (desmarcado)
checkbox = tk.Checkbutton(janela, text="Deseja continuar?", variable=valor_check)
checkbox.pack(pady=5)


# --- 2. EXEMPLO COM RADIO BUTTONS (Radiobutton) ---
tk.Label(janela, text="Exemplo Radio Button:", font=("Arial", 10, "bold")).pack(pady=(20, 0))

valor_radio = tk.StringVar(value="Sim") # Define "Sim" como padrão

radio_sim = tk.Radiobutton(janela, text="Sim", variable=valor_radio, value="Sim")
radio_sim.pack()

radio_nao = tk.Radiobutton(janela, text="Não", variable=valor_radio, value="Não")
radio_nao.pack()


# --- Botão para verificar o estado ---
tk.Button(janela, text="Verificar Respostas", command=mostrar_resultados).pack(pady=20)

janela.mainloop()
