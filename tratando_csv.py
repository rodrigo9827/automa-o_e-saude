import csv

# Ler csv e retornar apenas o CNS do atendimento da(o) enfermeira(o).
def buscar_cns(nome):
    texto = ""
    with open('Efetividade_6.0_2026.csv', mode='r', encoding='utf-8') as f:
        leitor = csv.reader(f, delimiter=',')
        for linha in leitor:
            if "Enfermeira (o)" in linha[1]:
                if linha[2] == nome:
                     if linha[3]=="Sim":
                        texto += "CNS: " + linha[4] + ", " + linha[0].split(" ")[0] + '\n'           
    return texto

# Mostrar o nome da enfermeira para evitar erro humano.
def listar_enfermeiras():
    nomes = []
    with open('Efetividade_6.0_2026.csv', mode='r', encoding='utf-8') as f:
        leitor = csv.reader(f, delimiter=',')
        for linha in leitor:
            if "Enfermeira (o)" in linha[1]:
                if linha[2] != "" and linha[2] not in nomes:
                    nomes.append(linha[2])
    nomes.sort()
    return nomes                   

