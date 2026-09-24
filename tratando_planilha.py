import csv
# Ler csv
def print_cns(nome):
    with open('Efetividade_6.0_2026.csv', mode='r', encoding='utf-8') as f:
        leitor = csv.reader(f, delimiter=',')
        for linha in leitor:
            if linha [1] == "Enfermeira":
                if linha[2] == nome:
                     if linha[4]=="":
                         pass
                     else:
                        print("CNS:",linha[4])
                        
                     
print_cns(nome="Rafael Felipe Nascimento de Oliveira")
