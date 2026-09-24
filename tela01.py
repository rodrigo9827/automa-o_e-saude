from tkinter import *
from tkinter import ttk

root = Tk()
frm = ttk.Frame(root, padding=10)
frm.grid()
# Campo do nome da enfermeira
ttk.Label(frm, text="Enfermeira" ).grid(column=0, row=0)
ttk.Entry(frm,  ).grid(column=1, row=0)



# campo de inserir CNs


ttk.Button(frm, text="Confirmar", command=root.destroy).grid(column=1, row=1)
root.mainloop()