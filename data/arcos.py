import pandas as pd

def arcos(df,nodos_sin_arcos):
    df.fillna(0, inplace=True)
    df.replace(' ', 0, inplace=True)

    for col in df.columns:
        df[col] = df[col].astype(int)

    zeros_df = pd.DataFrame(0, index=range(1), columns=df.columns)
    df = pd.concat([df, zeros_df], ignore_index=True)

    largo = len(df)

    s = set()

    for i in range(largo):
        for j in range(largo):
            nodo = int(df.iloc[i,j])
            if nodo != 0 and nodo not in nodos_sin_arcos:
                a = int(df.iloc[i-1,j])
                b = int(df.iloc[i+1,j])
                c = int(df.iloc[i,j-1])
                d = int(df.iloc[i,j+1])
                if a!=0 and a not in nodos_sin_arcos:
                    s.add(frozenset({nodo,a}))
                if b!=0 and b not in nodos_sin_arcos:
                    s.add(frozenset({nodo,b}))
                if c!=0 and c not in nodos_sin_arcos:
                    s.add(frozenset({nodo,c}))
                if d!=0 and d not in nodos_sin_arcos:
                    s.add(frozenset({nodo,d}))
    
    return s


