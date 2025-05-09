import pandas as pd

'''Alcance define el radio de alcance'''

def alcance(df,lista_s,lista_t):
    '''arroja un diccionario del siguiente tipo:
{(id_nodo_i, "tipo_faena_i"): [id_nodoj, id_nodoj,.....], 
(3,"skidder"): [1 , 4, 6], etc}'''
    # pasar todas las entradas del df que sean ' ' o NaN a 0
    df.fillna(0, inplace=True)
    df.replace(' ', 0, inplace=True)

    #agregar 3 filas con solo 0s
    zeros_df = pd.DataFrame(0, index=range(3), columns=df.columns)
    df = pd.concat([df, zeros_df], ignore_index=True)

    for col in df.columns:
        df[col] = df[col].astype(int)

    #diccionario
    alcance = {}

    #recorrer las columnas e ir viendo los valores que distintos a 0 y agregar las entradas
    largo = len(df)
    for i in range(largo):
        for j in range(largo):
            if df.iloc[i,j] != 0:

                if df.iloc[i,j] in lista_s:
                    lista = []
                    for dx in range(-2, 3):
                        for dy in range(-2, 3):
                            # Omitir las esquinas
                            if abs(dx) == 2 and abs(dy) == 2:
                                continue
                            # Omitir el centro
                            if dx == 0 and dy == 0:
                                continue
                            # Agregar valor a la lista
                            if df.iloc[i + dx, j + dy] != 0:
#                                lista.append((int(df.iloc[i + dx, j + dy]), 14000))

 #                   alcance[(int(df.iloc[i,j]),'skidder',10000)] = lista
                                lista.append(int(df.iloc[i + dx, j + dy]))

                    alcance[(int(df.iloc[i,j]),'skidder')] = {"radio": lista, "cv_rad":14, "id":int(df.iloc[i,j]), "cv_base":10}

                elif df.iloc[i,j] in lista_t:
                    lista = []

                    # Lista de coordenadas a excluir
                    excluir = [
                        (i-3, j-3), (i-3, j+3), (i+3, j-3), (i+3, j+3),
                        (i-2, j-3), (i-3, j-2),
                        (i-2, j+3), (i-3, j+2),
                        (i+2, j-3), (i+3, j-2),
                        (i+2, j+3), (i+3, j+2),
                        (i, j)  # También excluimos el centro si quieres
                    ]

                    # Recorremos todas las celdas dentro del 7x7
                    for dx in range(-3, 4):
                        for dy in range(-3, 4):
                            x, y = i + dx, j + dy
                            if (x, y) in excluir:
                                continue
                            if df.iloc[i + dx, j + dy] != 0:
#                                lista.append((int(df.iloc[x, y]), 16000))
#                    alcance[(int(df.iloc[i,j]),'torre', 16000)] = lista
                                lista.append(int(df.iloc[x, y]))
                    alcance[(int(df.iloc[i,j]),'torre')] = {"radio":lista, "cv_rad":16, "id":int(df.iloc[i,j]), "cv_base":16}
    return alcance
