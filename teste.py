import tratando_csv

enfermeiras = tratando_csv.listar_enfermeiras()
print("Enfermeiras:", len(enfermeiras))

primeira = enfermeiras[0]
gestantes = tratando_csv.buscar_gestantes(primeira)
print("Gestantes da primeira enfermeira:", len(gestantes))

for g in gestantes[:3]:
    print(g.data_contato, g.ig_semanas, g.ig_dias_resto, g.data_retorno, g.alto_risco)