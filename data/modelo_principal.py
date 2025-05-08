import sys
from gurobipy import *
from datos import *

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

        # Definir inventario
        # 1.
#        modelo.addConstr((p[i,0] == 0 for i in N), name='restriccion 1')

        # 2.
        for i in N:
            for t in T:
                suma_cosecha = quicksum(
                    w[i,j,k,t] 
                    for k in K 
                    if (i,k) in R_jk  
                    for j in R_jk[(i,k)]['radio'] 
                )
                
                # Suma de TODOS los flujos salientes del nodo i en el periodo t
#                flujo_saliente = quicksum(
#                    z[i,j,t] 
#                    for (a,b) in A 
#                    if a == i  # Todos los arcos que salen de i
#                )
                
                modelo.addConstr(
                    p[i,t] ==  suma_cosecha,
                    name=f"restriccion_2_{i}_{t}"
                )

#                modelo.addConstr(
#                    p[i,t] == p[i,t-1] + suma_cosecha - flujo_saliente,
#                    name=f"restriccion_2_{i}_{t}"
#                )
        
        # 3. Cosechar hectáreas solo del radio de cosecha
        for (i, k), datos_faena in R_jk.items():
            for j in datos_faena['radio']:
                for t in T:
                    modelo.addConstr(w[i, j, k, t] <= x[i, j, k, t], name=f'restriccion_3_{i}_{j}_{k}_{t}')

        # 4. Que no exista más de una faena por hectárea
        for i in N:
            for t in T:
                modelo.addConstr(quicksum(f[i, k, t] for k in K), name=f"restriccion_4_{i}_{j}_{k}")

        # 5. Relación entre faena y faena instalada
        for i in N:
            for k in K:
                for t in T:
                    if t in [1, 13]:
                        modelo.addConstr(mu[i, k, t] == f[i, k, t], name=f"restriccion_5_{i}_{j}_{k}")

        # 6. Continuidad de la faena
        for i in N:
            for k in K:
                for t in T:
                    if t not in [1, 13]:
                        modelo.addConstr(f[i, k, t] == f[i, k, t - 1] + mu[i, k, t], name=f'restriccion_6_{i}_{j}_{k}')
        
        # Asignacion de cosecha desde una hectarea faena a una hectarea no-faena
        # 7.
        for (i, k), datos_faena in R_jk.items():
            for j in datos_faena['radio']:
                for t in T:
                    modelo.addConstr(x[i,j,k,t] <= f[j,k,t], name=f"restriccion_7_{i}_{j}_{k}_{t}")
        
        # 8.
        for (i, k), datos_faena in R_jk.items():
            for t in T:
                modelo.addConstr(
                    quicksum(x[i,j,k,t] for j in datos_faena['radio']) <= 1,
                    name=f"restriccion_8_{i}_{k}_{t}"
                )

        # 9.
        for i in N:
            modelo.addConstr(
                quicksum(w[i,j,k,t] for t in T 
                                    for k in K 
                                    if (i,k) in R_jk  
                                    for j in R_jk[(i,k)]['radio']
                        ) <= N[j]['v'],
                name=f"restriccion_9_{i}"
            )


        # No cosechar mas de la capacidad de cada faena
        # 10.
        for k in K:
            for i in N:
                for t in T:
                    if (i,k) in R_jk: # Con esta condicion lo hice mas eficiente, pero revisa solo en los que se puede cosechar,
                                      # creo que no necesita revisar todas las posibles combinaciones, asi lo resuelve mas rapido.
                        modelo.addConstr(
                            quicksum(w[i,j,k,t] for j in R_jk[(i,k)]['radio']) <= K[k]['mcc'],
                            name=f"restriccion_10_{i}__{j}_{k}_{t}"
                        )

        # Restricción (11): Control de cosecha en rodales con restricción de adyacencia
        for r in rodales:
            for u in U:
                # Obtener los periodos de la temporada u (asumiendo 6 meses por temporada)
                T_u = T[(u-1)*6 : u*6] if u == 1 else T[6:]  # T1: meses 1-6, T2: meses 13-18
                
                # |N_r| es el número de nodos en el rodal r
                N_r = len(rodales[r])
                
                # Factor M grande (|N_r|² * |T| * |K|)
                M = (N_r ** 2) * len(T) * len(K)
                
                # Suma de todas las asignaciones de cosecha en el rodal r durante la temporada u
                modelo.addConstr(
                    quicksum(x[i,j,k,t] for k in K
                                    for i in rodales[r]
                                    for j in rodales[r]
                                    for t in T_u
                                    if (i,k) in R_jk and j in R_jk[(i,k)]['radio']) <= M * s[r,u],
                    name=f"restriccion_11_{r}_{u}"
                )

        # Restricción (12): Rodales adyacentes no pueden cosecharse en la misma temporada
        for r in RA_r:  # RA_r contiene los rodales con restricciones de adyacencia
            for q in RA_r[r]:  # q son los rodales adyacentes a r
                for u in U:
                    modelo.addConstr(
                        s[r,u] + s[q,u] <= 1,
                        name=f"restriccion_12_{r}_{q}_{u}"
                    )

        # Restricción (13): Actualización del estado del camino para períodos normales
        for (i,j) in A:
            for t in T:
                if t != 1 and t != 13:  # T \ {1, 13}
                    modelo.addConstr(
                        l[i,j,t] == l[i,j,t-1] + y[i,j,t],
                        name=f"restriccion_13_{i}_{j}_{t}"
                    )

        # Restricción (14): Actualización del estado del camino para período 13 (excluyendo XA)
        for (i,j) in A:
            if (i,j) not in XA:  # A \ XA
                modelo.addConstr(
                    l[i,j,13] == l[i,j,6] + y[i,j,13],
                    name=f"restriccion_14_{i}_{j}"
                )

        # Restricción (15): Inicialización del camino en período 1
        for (i,j) in A:
            modelo.addConstr(
                y[i,j,1] == l[i,j,1],
                name=f"restriccion_15_{i}_{j}"
            )

        # Restricción (16): Camino en período 13 para arcos en XA
        for (i,j) in XA:
            modelo.addConstr(
                y[i,j,13] == l[i,j,13],
                name=f"restriccion_16_{i}_{j}"
            )

        # Relacion entre asignacion de cosecha y modelo de red
        # 17.
        for i in N:
            if i not in D:  # excluyo los nodos destino, espero no genere problema por ser N una biblioteca y D una lista
                for t in T:
                    modelo.addConstr(
                        (quicksum(z[i,j,t] for (a,b) in A if b == i)  # tengo mis dudas con el orden, revisar porfavor
                         - quicksum(z[j,i,t] for (a,b) in A if a == i)) == -p[i,t],
                        name=f"restriccion_17_{i}_{t}"
                    )

        # 18.
        for d in D:
            for t in T:
                modelo.addConstr(
                    (quicksum(z[d,j,t] for (a,b) in A if a == d) 
                     - quicksum(z[i,d,t] for (a,b) in A if b == d)) == q[d,t],
                    name=f"restriccion_18_{d}_{t}"
                )

        # Flujo de madera requiere camino construido, definimos M grande
        # 19.
        M = sum(N[j]['v'] for j in N if 'v' in N[j])

        for (i,j) in A:
            for t in T:
                modelo.addConstr(
                    z[i,j,t] <= M * y[i,j,t],  # Usamos l[i,j,t] que es la variable de existencia del camino
                    name=f"restriccion_19_{i}_{j}_{t}"
                )




    except Exception as e:
        print(f"Error durante la ejecución del modelo: {str(e)}")

if __name__ == "__main__":
    main()
