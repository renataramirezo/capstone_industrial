import pandas as pd

def alcance(df, lista_s, lista_t):
    '''arroja un diccionario del siguiente tipo:
    {(id_nodo_i, "tipo_faena_i"): {'radio': [id_nodoj, id_nodoj,.....], 'cv_rad': x, 'id': y, 'cv_base': z}, 
    (3,"skidder"): {'radio': [1, 4, 6], 'cv_rad': 14, 'id': 3, 'cv_base': 10}, etc}'''
    
    # pasar todas las entradas del df que sean ' ' o NaN a 0
    df.fillna(0, inplace=True)
    df.replace(' ', 0, inplace=True)

    # agregar 3 filas con solo 0s
    zeros_df = pd.DataFrame(0, index=range(3), columns=df.columns)
    df = pd.concat([df, zeros_df], ignore_index=True)

    for col in df.columns:
        df[col] = df[col].astype(int)

    # diccionario
    alcance_dict = {}

    # recorrer las columnas e ir viendo los valores distintos a 0
    largo = len(df)
    for i in range(largo - 3):  # Restamos 3 para evitar índices fuera de rango
        for j in range(largo - 3):
            if df.iloc[i,j] != 0:
                current_id = int(df.iloc[i,j])

                if current_id in lista_s:
                    lista = []
                    for dx in range(-2, 3):
                        for dy in range(-2, 3):
                            # Omitir las esquinas
                            if abs(dx) == 2 and abs(dy) == 2:
                                continue
                            # Omitir el centro
                            if dx == 0 and dy == 0:
                                continue
                            # Verificar límites del DataFrame
                            if 0 <= i + dx < largo and 0 <= j + dy < largo:
                                if df.iloc[i + dx, j + dy] != 0:
                                    lista.append(int(df.iloc[i + dx, j + dy]))
                    
                    # Agregar el id actual al principio de la lista
                    lista = [current_id] + lista
                    alcance_dict[(current_id, 'skidder')] = {
                        "radio": lista,
                        "cv_rad": 14,
                        "id": current_id,
                        "cv_base": 10
                    }

                elif current_id in lista_t:
                    lista = []
                    # Lista de coordenadas a excluir
                    excluir = [
                        (i-3, j-3), (i-3, j+3), (i+3, j-3), (i+3, j+3),
                        (i-2, j-3), (i-3, j-2),
                        (i-2, j+3), (i-3, j+2),
                        (i+2, j-3), (i+3, j-2),
                        (i+2, j+3), (i+3, j+2),
                        (i, j)  # También excluimos el centro
                    ]

                    # Recorremos todas las celdas dentro del 7x7
                    for dx in range(-3, 4):
                        for dy in range(-3, 4):
                            x, y = i + dx, j + dy
                            if (x, y) in excluir:
                                continue
                            # Verificar límites del DataFrame
                            if 0 <= x < largo and 0 <= y < largo:
                                if df.iloc[x, y] != 0:
                                    lista.append(int(df.iloc[x, y]))
                    
                    # Agregar el id actual al principio de la lista
                    lista = [current_id] + lista
                    alcance_dict[(current_id, 'torre')] = {
                        "radio": lista,
                        "cv_rad": 16,
                        "id": current_id,
                        "cv_base": 16
                    }
    
    return alcance_dict