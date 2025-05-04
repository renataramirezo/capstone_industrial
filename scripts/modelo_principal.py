# /scripts/modelo_principal.py

import sys
from gurobipy import *
from data.datos import *

def main():
    try:
        modelo = Model("Cosecha_Forestal")
        modelo.ModelSense = GRB.MAXIMIZE

        #======= DEFINICION DE VARIABLES ==========
        
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
        # Estas variables son las que mas me generan dudas 
        x = {}
        w = {}
        for (i, k), datos_faena in R_jk.items():
            for j in datos_faena['radio']:
                for t in T:
                    x[i,j,k,t] = modelo.addVar(vtype=GRB.BINARY, name=f"x_{i}_{j}_{k}_{t}")
                    w[i,j,k,t] = modelo.addVar(vtype=GRB.CONTINUOUS, name=f"w_{i}_{j}_{k}_{t}")

        # Variables de rodales cosechados por temporada
        s = modelo.addVars(rodales.keys(), U, vtype=GRB.BINARY, name="s")

        # Variable construccion camino
        y = modelo.addVars(A, T, vtype=GRB.BINARY, name="y")

        # Variable existencia camino (Variable de estado)
        l = modelo.addVars(A, T, vtype=GRB.BINARY, name="l")

        # Variables de transporte e inventario
        p = modelo.addVars(nodos_faena, T, vtype=GRB.CONTINUOUS, name="p")
        z = modelo.addVars(A, T, vtype=GRB.CONTINUOUS, name="z")
        q = modelo.addVars(D, T, vtype=GRB.CONTINUOUS, name="q")

        modelo.update()

        # ========== FUNCIÓN OBJETIVO ==========

        # Agrego variables auxiliares que pidio el profe
        ingreso_venta = quicksum(P * q[d,t] for d in D for t in T)

        costos_cosechar = quicksum(
            datos_faena['cv_rad'] * w[i,j,k,t]  # Falta mejorar aca logica costos variables skkider
            for (i, k), datos_faena in R_jk.items()  
            for j in datos_faena['radio']  
            for t in T  
        )

        costos_instalacion = quicksum(
            N[i]["cf"] * mu[i,k,t] 
            for k in K 
            for i in N 
            for t in T 
            if (i,k,t) in mu 
        )

        costo_construccion_caminos = quicksum(C * y[i,j,t] for (i,j) in A for t in T)

        costo_transporte_madera = quicksum(ct * z[i,j,t] for (i,j) in A for t in T)

        # FUNCION OBJETIVO

        modelo.setObjective(  ingreso_venta 
                            - costos_cosechar 
                            - costos_instalacion 
                            - costo_construccion_caminos
                            - costo_transporte_madera)
        

        # ========== RESTRICCIONES ==========

        # Definir Inventario
        # 1.
        modelo.addConstr((p[i,0] == 0 for i in N), name='restriccion 1')

        # 2.
        modelo.addConstr((p[i,t] == p[i, (t-1)] + 
                          quicksum(w[i,j,k,t] for k in K for (base, faena), datos_faena in R_jk.items() for j in datos_faena['radio'])
                          - z[i,j] for i in N for (i,j) in A for t in T), name='restriccion 2')
        
        # Cosechar hectareas solo del radio de cosecha
        # 3.
        modelo.addConstr((w[i,j,k,t] <= x[i,j,k,t] for (i,k), datos_faena in R_jk.items() for j in datos_faena['radio'] for t in T), name='restriccion 3')

        # Que no exista mas de una faena por hectarea
        # 4.
        modelo.addConstr((quicksum(f[i,k,t] for k in K) for i in N for t in T), name='restriccion 4')

        # Relacion entre faena y faena instalada
        # 5.
        modelo.addConstr((mu[i,k,t] == f[i,k,t] for i in N for k in K for t in T if t not in [1, 13]), name='restriccion 5')

        # 6.
        modelo.addConstr((f[i,k,t] == f[i,k,(t-1)] + mu[i,k,t] for i in N for k in K for t in T if t not in [1, 13]), name='restriccion 5')


        




    except Exception as e:
        print(f"Error durante la ejecución del modelo: {str(e)}")

if __name__ == "__main__":
    main()
