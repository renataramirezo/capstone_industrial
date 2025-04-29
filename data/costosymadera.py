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
    'cant madera': "v"
})

columnas_deseadas = ['idnodo', 'K', 'cf', 'v']
df = excel2[columnas_deseadas]
df = df.dropna(subset=['idnodo'])
# Establecer 'idnodo' como índice
df.set_index('idnodo', inplace=True)

# Convertir a diccionario
dic_nodos = df.to_dict(orient="index")




