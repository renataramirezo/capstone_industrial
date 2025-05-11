import pandas as pd
import os
from alcance import alcance
from arcos import arcos
import costosymadera

# EN ESTE ARCHIVO ESTARÁN TODOS LOS CONJUNTOS Y PARAMETROS

# ruta al csv con los nodos
csv_nodos = os.path.join(os.path.dirname(__file__), 'prediocsv.csv')
# lectura dataframe
df = pd.read_csv(csv_nodos, sep=';')  

# Datos del modelo
P = 35 #precio madera por metro cúbico
C = 200 #costo construír 100m de camino (1 camino)
ct = 0.007 #costo transporte de cada metro cúbico por 1 camino 100m

# Nodos
N=costosymadera.dic_nodos
'''N es un diccionario de nodos de este tipo,
N={"idnodo":{"K","v" "cf"}...} con K= tipo de maquinaria, 
                                    v=volumen de madera disponible,
                                    cf=costo fijo instalación faena,
                                    mcc = capacidad maxima cosecha faena k
por ejemplo:
             {1:{"K":"skidder","v":3, "cf":5000, "mcc":6}}, 
             2:{"K":"torre","v":3, "cf":5000, "mcc":6}},
              etc},
        '''

#print(type(N{"1"}:{""}))

nodos_skidders = [1, 2, 4, 7, 8, 11, 12, 14, 15, 16, 18, 19, 22, 23, 25, 28, 31, 34, 37, 40, 89, 90, 46, 47, 84, 91, 92, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 108, 109, 110, 112, 114, 115, 117, 118, 120, 121, 123, 124, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210]
nodos_torres = [50, 52, 58, 62, 63, 27, 65, 66, 36, 77, 78, 39, 42]
nodos_faena = nodos_skidders + nodos_torres
#print(len(nodos_faena))

# AUXILIARES
nodos_sin_arcos = [9,10,13,54,17,55,48,49,51,107,57,113,20,21,60,116,24,61,64,119,26,29,30,69,70,71,32,33,73,74,35,81,82,83,87,88]
A = arcos(df, nodos_sin_arcos)




# Arcos que se destruyen
XA1 = [(27, 65), (36, 77), (36, 39), (39, 38), (39, 42), (50,52), (52,53), (52,56), (53, 111), 
      (56, 59), (58, 59), (58, 62), (59, 63), (62, 63), (62,66), (63, 67), (65, 66), (66, 67),
      (67, 68), (68, 72), (68, 122), (72, 76), (72, 125), (76, 80), (76, 129), (77, 78), (79, 80),
      (80, 84), (80, 133), (84, 92), (84, 137), (92, 140), (99, 103), (103, 104), (100, 104), 
      (104, 105), (104, 108), (108, 109), (111, 112), (112, 110), (112,114), (114, 115), (114, 117),
      (117, 118), (117, 120), (120, 121), (120, 123), (122, 123), (122, 125), (123, 124), (123, 126), 
      (125, 126), (125, 129), (129, 130), (129, 133), (133, 134), (133, 137), (137, 138), (137, 140),
      (140, 141), (140, 143)]
XA = set(frozenset(i) for i in XA1)
#print(XA)
#print(f"ARCOS: {A}")

# Tipos de Faena
#incluso más que diccionario podría convenir named tupple
K = {"skidder":{"mcc":4000}, "torre":{"mcc":5500}}

# Períodos de tiempo en meses de cosecha, corresponde a los meses 
#T = ["dic 23","e24", "f24", "mar24", "ab24", "may24", "dic24", "e25", "f25","mar25","ab25","may25"]
T = [1, 2, 3, 4, 5, 6, 13, 14, 15, 16, 17, 18]

# Temporadas
U = [1, 2]

# Nodos de destino
D = [147, 169]  

# Rodales
rodales = {
     1: [1, 2, 3, 4, 5, 6, 7, 8 ,9, 10, 11, 12, 13],
     2: [14, 15, 16, 17, 18, 19, 20, 21, 22, 23],
     3: [24, 25, 26, 27, 28, 29, 30, 31, 32, 33],
     4: [34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45],
     5: [46, 47, 48, 49, 50, 51, 52, 53],
     6: [54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64],
     7: [65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76],
     8: [77, 78, 79, 80, 81, 82, 83, 84, 85, 86],
     9: [87, 88, 89, 90],
    10: [91, 92, 93, 94, 95, 96, 97, 98],
    11: [99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110],
    12: [111, 112, 113, 114, 115, 116, 117, 118],
    13: [119, 120, 121, 122, 123, 124],
    14: [125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136],
    15: [137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149],
    16: [150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169],
    17: [170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187],
    18: [188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199],
    19: [200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210],
}



#Radio cosecha por Nodo y costo variable
R_jk = alcance(df,nodos_skidders,nodos_torres)
#{(id_nodo_1, "tipo_faena"):{"radio": [id_nodoj1,id_nodoj2... ], "cv_rad":16000, "id":int(df.iloc[i,j]), "cv_base":16000}

# Rodales adyacentes que no se pueden cosechar en la misma temporada.
RA_r= {1:[],
       2:[3],
       3:[2],
       4:[9],
       5:[6],
       6:[5,7],
       7:[6,8],
       8:[7],
       9:[4],
       10:[15],
       11:[12],
       12:[11,13],
       13:[12],
       14:[18],
       15:[10],
       16:[17],
       17:[16],
       18:[14],
       19:[]}

print(R_jk)
