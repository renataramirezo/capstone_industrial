import pickle

archivo_pkl = 'resultados_modelo_principal.pkl'
archivo_txt = 'mpb.txt'

with open(archivo_pkl, 'rb') as f:
    datos = pickle.load(f)

with open(archivo_txt, 'w', encoding='utf-8') as f:
    f.write(str(datos))
