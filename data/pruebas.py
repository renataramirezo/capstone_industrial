import pandas as pd
import os
from alcance import alcance
from arcos import arcos
from costosymadera import dic_nodos

csv_path = os.path.join(os.path.dirname(__file__), 'prediocsv.csv')
df = pd.read_csv(csv_path, sep=';')  

nodos_sin_arcos = [9,10,13,54,17,55,48,49,51,107,57,113,20,21,60,116,24,61,64,119,26,29,30,69,70,71,32,33,73,74,35,81,82,83,87,88]
A1 = arcos(df, nodos_sin_arcos)


A1_tuplas = {tuple(sorted(arco)) for arco in A1}


N = dic_nodos
v_i = {fila: valores['v'] for fila, valores in N.items()}

cf_ik = {fila: {'K': valores['K'], 'cf': valores['cf']} for fila, valores in N.items()}

#print(v_i[4])



