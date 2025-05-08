import pandas as pd
'''este archivo es para poner los costos de instalación de faena 
y la cantidad de madera por rodal'''
excel = pd.read_excel("data\costos_y_madera_nodos.xlsx")

#['idnodo', 'eje vertical', 'eje horizontal', 'tipo de feane', 
# 'costo inst', 'cant madera']
# Seleccionar solo las columnas necesarias
excel2 = excel.rename(columns={
    'tipo de feane': 'K',
    'costo inst': 'cf',
    'cant madera': "v",
    'eje vertical': "y",
    'eje horizontal': "x"
})
#excel2['y'] = excel2['y'] * -1

excel2['pos'] = list(zip(excel2['x'], excel2['y']))
columnas_deseadas = ['idnodo', 'K', 'cf', 'v', 'pos']
df = excel2[columnas_deseadas]
df = df.dropna(subset=['idnodo'])

#print(df)
sk =df.loc[2, "K"]
tr= df.loc[50,"K"]

# Establecer 'idnodo' como índice
df.set_index('idnodo', inplace=True)
#print(tr)
# Convertir a diccionario
dic_nodos = df.to_dict(orient="index")
for id in dic_nodos:
    maquina = dic_nodos[id]["K"]

    if maquina == sk:
        costo = 4000
    elif maquina == tr:
        costo = 5500
    else:
        costo = "NAN"
    dic_nodos[id]["mcc"]=costo

for nodo_id, atributos in dic_nodos.items():
    for k, v in atributos.items():
        if isinstance(v, float):
            atributos[k] = round(v, 3)




print(dic_nodos[130]["mcc"])

