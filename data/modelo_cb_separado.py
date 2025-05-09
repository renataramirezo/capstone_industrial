from gurobipy import *
from datos import *
from grafos import *


def main():
    try:
        modelo_1 = Model("Asignacion_cosecha")
        modelo_2 = Model("Camino_flujo_cosecha")
        #modelo.ModelSense = GRB.MAXIMIZE

        #======= DEFINICION DE VARIABLES ==========
        
        # Variable Binaria Instalacion y existencia de maquinaria
        mu = {}
        f = {}
        for k in K:
            for i in N:
                for t in T:
                    mu[i,k,t] = modelo_1.addVar(vtype=GRB.BINARY, name=f"mu_{i}_{k}_{t}")
                    f[i,k,t] = modelo_1.addVar(vtype=GRB.BINARY, name=f"f_{i}_{k}_{t}")
        
        # Variables asignacion de cosecha y cantidad de madera
        # Estas variables son las que mas me generan dudas 
        x = {}
        w = {}
        for (i, k), datos_faena in R_jk.items():
            for j in datos_faena['radio']:
                for t in T:
                    x[i,j,k,t] = modelo_1.addVar(vtype=GRB.BINARY, name=f"x_{i}_{j}_{k}_{t}")
                    w[i,j,k,t] = modelo_1.addVar(vtype=GRB.CONTINUOUS, name=f"w_{i}_{j}_{k}_{t}")

        # Variables de rodales cosechados por temporada
        s = modelo_1.addVars(list(range(1,20)), U, vtype=GRB.BINARY, name="s")

        # Variable construccion camino
        y = modelo_2.addVars(G.edges(), T, vtype=GRB.BINARY, name="y")

        # Variable existencia camino (Variable de estado)
        l = modelo_2.addVars(G.edges(), T, vtype=GRB.BINARY, name="l")

        # Variables de transporte e inventario
        p = modelo_1.addVars(N, T, vtype=GRB.CONTINUOUS, name="p")
        z = modelo_2.addVars(G.edges(), T, vtype=GRB.CONTINUOUS, name="z")
        q = modelo_2.addVars(D, T, vtype=GRB.CONTINUOUS, name="q")

        

        modelo_1.update()
        modelo_2.update()

        # ========== FUNCIÓN OBJETIVO ==========

        # Agrego variables auxiliares que pidio el profe
        ingreso_venta = quicksum(P * p[n,t] for n in N for t in T) #Modificado para modelo_1


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
            if (i,k,t) in mu and isinstance(N[i]["cf"], (int, float))
        )

        lista_recorrido = []
        for i,j in G.edges():
            if (j,i) not in lista_recorrido:
                lista_recorrido.append((i,j))

        costo_construccion_caminos = quicksum(C * y[i,j,t] for i, j in lista_recorrido for t in T)

        costo_transporte_madera = quicksum(ct * z[i,j,t] for i, j in G.edges() for t in T)


        # FUNCION OBJETIVO


        modelo_1.setObjective( ingreso_venta 
                            - costos_cosechar 
                            - costos_instalacion 
                            ,sense=GRB.MAXIMIZE
                            )
        
        modelo_2.setObjective(- costo_construccion_caminos
                            - costo_transporte_madera
                            ,sense=GRB.MAXIMIZE
                            )
        

        # ========== RESTRICCIONES ==========

        # 1.
        for i in N:
            for t in T:
                modelo_1.addConstr(
                    p[i,t] ==  quicksum(
                    w[i,j,k,t] 
                    for k in K 
                    if (i,k) in R_jk  
                    for j in R_jk[(i,k)]['radio'] 
                ),
                    name=f"restriccion_2_{i}_{t}"
                )
        
        # 2. Cosechar hectáreas solo del radio de cosecha
        for (i, k), datos_faena in R_jk.items():
            for j in datos_faena['radio']:
                M_jk = min(N[j]['v'], K[k]['mcc'])
                for t in T:
                    modelo_1.addConstr(w[i, j, k, t] <= x[i, j, k, t], name=f'restriccion_3_{i}_{j}_{k}_{t}')

        # 3. Que no exista más de una faena por hectárea
        for i in N:
            for t in T:
                modelo_1.addConstr(quicksum(f[i, k, t] for k in K) <= 1, name=f"restriccion_4_{i}_{j}_{k}")

        # 4. Relación entre faena y faena instalada
        for i in N:
            for k in K:
                for t in T:
                    if t in [1, 13]:
                        modelo_1.addConstr(mu[i, k, t] == f[i, k, t], name=f"restriccion_5_{i}_{j}_{k}")

        # 5. Continuidad de la faena
        for i in N:
            for k in K:
                for t in T:
                    if t not in [1, 13]:
                        modelo_1.addConstr(f[i, k, t] == f[i, k, t - 1] + mu[i, k, t], name=f'restriccion_6_{i}_{j}_{k}')
        
        # Asignacion de cosecha desde una hectarea faena a una hectarea no-faena
        # 6.
        for (i, k), datos_faena in R_jk.items(): #i es base
            for j in datos_faena['radio']:#j es radio
                for t in T:
                    modelo_1.addConstr(x[i,j,k,t] <= f[i,k,t], name=f"restriccion_7_{i}_{j}_{k}_{t}")
        
        # 7.
        for j in N:
            for t in T:
                for k in K:
                    modelo_1.addConstr(
                    quicksum(x[i,j,k,t] for (i,b), datos_faena in R_jk.items()
                                        if j in datos_faena['radio'] and b == k) <= 1,#sumo en radio j
                    name=f"restriccion_8_{j}_{k}_{t}"
                )

        # 8.
        for j in N:
            modelo_1.addConstr(
                quicksum(w[i,j,k,t] for (i,k), datos_faena in R_jk.items()
                                    for t in T
                                    if j in datos_faena['radio']
                        ) <= N[j]['v'],
                name=f"restriccion_9_{i}"
            )


        # No cosechar mas de la capacidad de cada faena
        # 9.
        for k in K:
            for i in N:
                for t in T:
                    if (i,k) in R_jk: # Con esta condicion lo hice mas eficiente, pero revisa solo en los que se puede cosechar,
                                      # creo que no necesita revisar todas las posibles combinaciones, asi lo resuelve mas rapido.
                        modelo_1.addConstr(
                            quicksum(w[i,j,k,t] for j in R_jk[(i,k)]['radio']) <= K[k]['mcc'],
                            name=f"restriccion_10_{i}__{j}_{k}_{t}"
                        )

        # Control de cosecha en rodales con restricción de adyacencia
        # 10.
        for r in range(1,20):
            
            for u in U:
                # Obtener los periodos de la temporada u (asumiendo 6 meses por temporada)
                T_u = T[(u-1)*6 : u*6] if u == 1 else T[6:]  # T1: meses 1-6, T2: meses 13-18
                
                # |N_r| es el número de nodos en el rodal r
                N_R = datos.rodales[r]
                N_r = len(datos.rodales[r])
                
                # Factor M grande (|N_r|² * |T| * |K|)
                M = (N_r ** 2) * len(T) * len(K)
                M_r = 0
                for k in K:
                    for i in N_R:
                        if k == 'skidder':
                            lista_nodos = nodos_skidders
                        else:
                            lista_nodos = nodos_torres
                        if i in lista_nodos:
                            lista_auxiliar = []
                            rango = R_jk[(i,k)]['radio']
                            for j in rango:
                                if j in N_R:
                                    lista_auxiliar.append(j)
                            M_r += len(lista_auxiliar)
                
                M_r = M_r * len(T_u)

                
                # Suma de todas las asignaciones de cosecha en el rodal r durante la temporada u
                modelo_1.addConstr(
                    quicksum(x[i,j,k,t] for k in K
                                    for i in datos.rodales[r]
                                    for j in datos.rodales[r]
                                    for t in T_u
                                    if (i,k) in R_jk and j in R_jk[(i,k)]['radio']) <= M_r * s[r,u],
                    name=f"restriccion_10_{r}_{u}"
                )

        # Rodales adyacentes no pueden cosecharse en la misma temporada
        # 11.
        for r in RA_r:  # RA_r contiene los rodales con restricciones de adyacencia
            for a in RA_r[r]:  # q son los rodales adyacentes a r
                for u in U:
                    modelo_1.addConstr(
                        s[r,u] + s[a,u] <= 1,
                        name=f"restriccion_11_{r}_{a}_{u}"
                    )

        # Actualización del estado del camino para períodos normales
        # 12.
        for (i,j) in G.edges():
            for t in T:
                if t != 1 and t != 13:  # T \ {1, 13}
                    modelo_2.addConstr(
                        l[i,j,t] == l[i,j,t-1] + y[i,j,t],
                        name=f"restriccion_13_{i}_{j}_{t}"
                    )

        # Actualización del estado del camino para período 13 (excluyendo XA)
        # 13:
        for i, j in G.edges():
            if G[i][j]["XA"] == False:  # A \ XA    
                modelo_2.addConstr(
                    l[i,j,13] == l[i,j,6] + y[i,j,13],
                    name=f"restriccion_14_{i}_{j}"
                )

        # Inicialización del camino en período 1
        # 14.
        for i, j in G.edges():
            modelo_2.addConstr(
                y[i,j,1] == l[i,j,1],
                name=f"restriccion_15_{i}_{j}"
            )

        # Camino en período 13 para arcos en XA
        # 15.
        for i, j in G.edges():
            if G[i][j]["XA"] == True:  # XA    
            #if (i,j) != (100,104):
                modelo_2.addConstr(
                    y[i,j,13] == l[i,j,13],
                    name=f"restriccion_16_{i}_{j}"
                )

        # Relacion entre asignacion de cosecha y modelo de red
        # 16.
        '''for i in N:
            if i not in D:  # excluyo los nodos destino, espero no genere problema por ser N una biblioteca y D una lista
                for t in T:
                    modelo_2.addConstr(
                        (quicksum(z[i,b,t] for a,b in G.edges() if a == i)  # tengo mis dudas con el orden, revisar porfavor
                         - quicksum(z[a,i,t] for a,b in G.edges() if b == i)) == p[i,t],
                        name=f"restriccion_17_{i}_{t}"
                    )'''
        # R auxiliar
        for i,j in G.edges():
            for t in T:
                modelo_2.addConstr(
                    y[i,j,t] == y[j,i,t],
                    name="Restriccion_direccion_caminos"
                )


        # 17.
        for d in D:
            for t in T:
                flow = 0
                for i,j in G.edges():
                    if d == i:
                        flow += z[i,j,t]
                    elif d == j:
                        flow -= z[i,j,t]
                modelo_2.addConstr(
                    flow == -q[d,t],
                    name=f"restriccion_18_{d}_{t}"
                )
                
                '''modelo_2.addConstr(
                    (quicksum(z[d,b,t] for a,b in G.edges() if a == d) + quicksum(z[d,a,t] for a,b in G.edges() if b == d)
                     - quicksum(z[a,d,t] for a,b in G.edges() if b == d) + quicksum(z[b,d,t] for a,b in G.edges() if a == d)) == -q[d,t],
                    name=f"restriccion_18_{d}_{t}"
                )'''

        # Flujo de madera requiere camino construido, definimos M grande
        # 18.
        M = sum(N[j]["v"] for j in N if 'v' in N[j])

        for i,j in G.edges():
            M_ij = min(M,sum(4000 for i in nodos_skidders) + sum(5000 for i in nodos_torres))
            for t in T:
                modelo_2.addConstr(
                    z[i,j,t] <= M_ij * l[i,j,t],  # Usamos l[i,j,t] que es la variable de existencia del camino
                    name=f"restriccion_19_{i}_{j}_{t}"
                )
        modelo_1.optimize()

        dic_pit = {}
        for i in N:
            for t in T:
                dic_pit[i,t] = p[i,t].X

        print("ingresos:", ingreso_venta.getValue())
        print("costo cosechar:", costos_cosechar.getValue())
        print("costo instalacion:", costos_instalacion.getValue())

        """for i in N:
            if i not in D:  # excluyo los nodos destino, espero no genere problema por ser N una biblioteca y D una lista
                for t in T:
                    modelo_2.addConstr(
                        (quicksum(z[i,b,t] for a,b in G.edges() if a == i or b == i)  
                         - quicksum(z[a,i,t] for a,b in G.edges() if b == i)) == dic_pit[i,t],
                        name=f"restriccion_17_{i}_{t}"
                    )"""

        for n in N:
            if n not in D:
                for t in T:
                    flow = 0
                    for i,j in G.edges():
                        if n == i:
                            flow += z[i,j,t]
                        elif n == j:
                            flow -= z[i,j,t]
                    modelo_2.addConstr(
                        flow == dic_pit[n,t],
                        name=f"restriccion_20_{n}_{t}"
                    )
        
        modelo_2.optimize()

        print("consto transporte", costo_transporte_madera.getValue())
        print("costo construccion camino:", costo_construccion_caminos.getValue())

        ingreso_total = ingreso_venta - costos_cosechar - costos_instalacion - costo_construccion_caminos- costo_transporte_madera

        print(" Valor Funcion Objetivo:", ingreso_total.getValue())
        print(f"P : {P}")

        # Verificar el estado del modelo
        estado = modelo_1.Status
        if estado == GRB.Status.OPTIMAL:
            print("Solución óptima encontrada.")
            print("Valor objetivo:", modelo_2.ObjVal)
            print("")
            print("ingresos:", ingreso_venta.getValue())
            print("costo cosechar:", costos_cosechar.getValue())
            print("costo instalacion:", costos_instalacion.getValue())
            print("consto transporte", costo_transporte_madera.getValue())
            print("costo construccion camino:", costo_construccion_caminos.getValue())
            for i in N:
                for t in T:
                    if p[i,t].X > 0:
                        print(f"p de {i},{t}: {p[i,t].X}")

            for d in D:
                for t in T:
                    if q[d,t].X > 0:
                        print(f"q de {d},{t}: {q[d,t].X}")

        elif estado == GRB.Status.INFEASIBLE:
            print("El modelo es infactible.")
            modelo_2.computeIIS()
            modelo_2.write("modelo_cb_infactible.ilp")  # Esto te genera un archivo con las restricciones conflictivas
        elif estado == GRB.Status.UNBOUNDED:
            print("El modelo no tiene cota inferior (es no acotado).")
        else:
            print(f"Estado del modelo: {estado}")

    except Exception as e:
        print(f"Error durante la ejecución del modelo: {str(e)}")
        modelo_2.computeIIS()
        modelo_2.write("modelo_cb_infactible.ilp")
        raise

if __name__ == "__main__":
    main()
