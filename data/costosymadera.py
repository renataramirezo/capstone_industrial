import pandas as pd

'''Este archivo es para poner los costos de instalación de faena 
y la cantidad de madera por rodal'''

# Archivo de Excel que contiene datos sobre nodos
excel = pd.read_excel("data\costos_y_madera_nodos.xlsx")

# Renombrar columnas
excel2 = excel.rename(columns={
    'tipo de feane': 'K',
    'costo inst': 'cf',
    'cant madera': "v",
    'eje vertical': "y",
    'eje horizontal': "x"
})

# Crear una columna con la posición (x, y)
excel2['pos'] = list(zip(excel2['x'], excel2['y']))

# Seleccionar columnas importantes y limpiar
columnas_deseadas = ['idnodo', 'K', 'cf', 'v', 'pos']
df = excel2[columnas_deseadas]
df = df.dropna(subset=['idnodo'])

# Establecer 'idnodo' como índice
df.set_index('idnodo', inplace=True)

# Convertir a diccionario
dic_nodos = df.to_dict(orient="index")

# Redondear los valores flotantes de cantidad de madera
for nodo_id, atributos in dic_nodos.items():
    for k, v in atributos.items():
        if isinstance(v, float):
            atributos[k] = round(v, 3)