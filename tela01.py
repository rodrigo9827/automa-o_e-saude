from tkinter import *
from tkinter import ttk
import tratando_planilha

root = Tk()
frm = ttk.Frame(root, padding=10)
frm.grid()
# Campo do nome da enfermeira
ttk.Label(frm, text="Enfermeira" ).grid(column=0, row=0)
ttk.Entry(frm,  ).grid(column=1, row=0)

ttk.Button(frm, text="Confirmar", command=root.destroy).grid(column=1, row=1)
root.mainloop()