# /scripts/modelo_principal.py

import sys
from gurobipy import *
from data.datos import *

def main():
    try:
        modelo = Model("Cosecha_Forestal")
        modelo.ModelSense = GRB.MAXIMIZE

        #======= DEFINICION DE VARIABLES ===========
        
        # Variable Binaria Instalacion y existencia de maquinaria
        mu = {}
        f = {}
        for k in K:
            for i in N:
                if (k == "skidder" and i in nodos_skidders) or (k == "torre" and i in nodos_torres):
                    for t in T:
                        mu[i,k,t] = modelo.addVar(vtype=GRB.BINARY, name=f"mu_{i}_{k}_{t}")
                        f[i,k,t] = modelo.addVar(vtype=GRB.BINARY, name=f"f_{i}_{k}_{t}")
        
        # Variables asignacion de cosecha y cantidad de madera
        x = {}
        w = {}
        for (i, k, cv), nodos in R_jk.items():
            for j, cv_j in nodos:
                for t in T:
                    x[i,j,k,t] = modelo.addVar(vtype=GRB.BINARY, name=f"x_{i}_{j}_{k}_{t}")
                    w[i,j,k,t] = modelo.addVar(vtype=GRB.CONTINUOUS, name=f"w_{i}_{j}_{k}_{t}")

        # Variables de rodales cosechados por temporada
        s = modelo.addVars(rodales.keys(), [1, 2], vtype=GRB.BINARY, name="s")

        # Variables de construcción y estado de caminos
        y = modelo.addVars(A, T, vtype=GRB.BINARY, name="y")
        l = modelo.addVars(A, T, vtype=GRB.BINARY, name="l")

        # Variables de transporte e inventario
        p = modelo.addVars(N.keys(), T, vtype=GRB.CONTINUOUS, name="p")
        z = modelo.addVars(A, T, vtype=GRB.CONTINUOUS, name="z")
        q = modelo.addVars(D, T, vtype=GRB.CONTINUOUS, name="q")

        modelo.update()




    except Exception as e:
        print(f"Error durante la ejecución del modelo: {str(e)}")

if __name__ == "__main__":
    main()
