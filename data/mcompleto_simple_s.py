from gurobipy import *
from datos import *
from grafos import *
#from guardar_sol import *
import pickle

# Este modelo considera solo temporadas, no distingue por meses

def main():
    try:
        modelo_1 = Model("Asignacion_cosecha")
        modelo_2 = Model("Camino_flujo_cosecha")
        #modelo.ModelSense = GRB.MAXIMIZE

        #======= DEFINICION DE VARIABLES ==========#
        
        # Variable Binaria Instalacion y existencia de maquinaria
        mu = {}
        for k in K:
            for i in N:
                for u in U:
                    mu[i,k,u] = modelo_1.addVar(vtype=GRB.BINARY, name=f"mu_{i}_{k}_{u}")
        
        # Variables asignacion de cosecha y cantidad de madera
        x = {}
        w = {}
        for t in T:
            for (i, k), datos_faena in R_jk.items():
                for j in datos_faena['radio']:                
                    x[i,j,k,t] = modelo_1.addVar(vtype=GRB.BINARY, name=f"x_{i}_{j}_{k}_{t}")
            for k in K:
                for i in N:
                    for j in N:#aquí hay que tener ojo porque igual queremos cosechar en la base faena entonces i puede ser =j
                        w[i,j,k,t] = modelo_1.addVar(vtype=GRB.CONTINUOUS, name=f"w_{i}_{j}_{k}_{t}")

        # Variables de rodales cosechados por temporada
        s = modelo_1.addVars(list(range(1,20)), U, vtype=GRB.BINARY, name="s")

        # Variable construccion camino
        y = modelo_2.addVars(G.edges(), U, vtype=GRB.BINARY, name="y")

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
            N[i]["cf"] * mu[i,k,u] 
            for k in K 
            for i in N 
            for u in U 
            if (i,k,u) in mu and isinstance(N[i]["cf"], (int, float))
        )

        lista_recorrido = []
        for i,j in G.edges():
            if (j,i) not in lista_recorrido:
                lista_recorrido.append((i,j))

        costo_construccion_caminos = (quicksum(C * y[i,j,1] for i, j in lista_recorrido) 
                                      + quicksum(C * y[i,j,2] for i, j in lista_recorrido if (i,j) in XA))

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
                    name=f"restriccion_1_{i}_{t}"
                )
        
        # 2. Cosechar hectáreas solo del radio de cosecha
        for (i, k), datos_faena in R_jk.items():
            for j in datos_faena['radio']:
                for t in T:
                    modelo_1.addConstr(w[i, j, k, t] <= N[j]['v'] * x[i, j, k, t], name=f'restriccion_2_{i}_{j}_{k}_{t}')

        # 3. Que no exista más de una faena por hectárea
        for i in N:
            for u in U:
                modelo_1.addConstr(quicksum(mu[i, k, u] for k in K) <= 1, name=f"restriccion_3_{i}_{k}_{u}")


        # Asignacion de cosecha desde una hectarea faena a una hectarea no-faena
        # 6.    
        for i in N:
            for k in K:
                if (i,k) in R_jk:
                    for j in R_jk[(i,k)]['radio']:
                        if i == j:
                            modelo_1.addConstr(x[i,j,k,1] == mu[i,k,1], name=f"restriccion_4.1_{i}_{j}_{k}_{t}")
                            modelo_1.addConstr(x[i,j,k,13] == mu[i,k,2], name=f"restriccion_4.2_{i}_{j}_{k}_{t}")
                        for t in T:
                            if t <= 6:
                                modelo_1.addConstr(x[i,j,k,t] <= mu[i,k,1], name=f"restriccion_4.3_{i}_{j}_{k}_{t}")
                            else:
                                modelo_1.addConstr(x[i,j,k,t] <= mu[i,k,2], name=f"restriccion_4.4_{i}_{j}_{k}_{t}")

        for i in N:
            for u in U:
                indices_efectivos = []
                for j in nodos_skidders:
                    cobertura = R_jk[j,'skidder']
                    if i in cobertura:
                        indices_efectivos.append([j,'skidder'])
                for j in nodos_torres:
                    cobertura = R_jk[j,'torre']
                    if i in cobertura:
                        indices_efectivos.append([j,'torre'])
                Miu = len(cobertura) * 6 * 2
                modelo_1.addConstr(quicksum(x[key[0],i,key[1],t_] 
                                    for key in indices_efectivos 
                                    for k in K
                                    if key[0] != i for t_ in T_u[u]) <= (1 - quicksum(mu[i,k,u] for k in K)) * Miu,
                                        name="restriccion_miau")

        
        # 7.
        for j in N:
            for t in T:
                for k in K:
                    modelo_1.addConstr(
                    quicksum(x[i,j,k,t] for (i,b), datos_faena in R_jk.items()
                                        if j in datos_faena['radio'] and b == k) <= 1,
                    name=f"restriccion_7_{i}_{j}_{k}_{t}"
                )

        # 8.
        for j in N:
            modelo_1.addConstr(
                quicksum(w[i,j,k,t] for (i,k), datos_faena in R_jk.items()
                                    for t in T
                                    if j in datos_faena['radio']
                        ) <= N[j]['v'],
                name=f"restriccion_8_{i}"
            )

        # No cosechar mas de la capacidad de cada faena
        # 9.
        for k in K:
            for i in N:
                for t in T:
                    if (i,k) in R_jk: # Revisa solo en los que se puede cosechar
                        modelo_1.addConstr(
                            quicksum(w[i,j,k,t] for j in R_jk[(i,k)]['radio']) <= K[k]['mcc'],
                            name=f"restriccion_9_{i}__{j}_{k}_{t}"
                        )

        # Control de cosecha en rodales con restricción de adyacencia
        # 10.
        """for r in rodales:
            for u in U:
                # Obtener los periodos de la temporada u (asumiendo 6 meses por temporada)
                T_u = T[(u-1)*6 : u*6] if u == 1 else T[6:]  # T1: meses 1-6, T2: meses 13-18
           
                N_R = rodales[r]
                
                # Suma de todas las asignaciones de cosecha en el rodal r durante la temporada u
                modelo_1.addConstr(
                    quicksum(x[i,j,k,t] for k in K
                                    for i in N
                                    for j in N_R
                                    for t in T_u
                                    if (i,k) in R_jk and j in R_jk[(i,k)]['radio']) <= Big_M[r] * s[r,u],
                    name=f"restriccion_10_{r}_{u}"
                )"""

        # Rodales adyacentes no pueden cosecharse en la misma temporada
        # 11.
        for r in RA_r:  
            for a in RA_r[r]: 
                for u in U:
                    modelo_1.addConstr(
                        s[r,u] + s[a,u] <= 1,
                        name=f"restriccion_11_{r}_{a}_{u}"
                    )


        for r in Rodales:
            for u in U:
                for (i,k), datos_faena in R_jk.items():
                    for j in rodales[r]:
                        if j in datos_faena['radio']:
                            for t in T_u[u]:
                                modelo_1.addConstr(x[i,j,k,t] <= s[r,u], name=f"restriccion_12.1_{i}_{j}_{t}")


        # 16.
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
                    name=f"restriccion_16_{d}_{t}"
                )
                

        # Flujo de madera requiere camino construido, definimos M grande
        # 18.

        for i,j in G.edges():
            for t in T_u[1]:
                modelo_2.addConstr(
                    z[i,j,t] <= M_ij * y[i,j,1],  
                    name=f"restriccion_17.1_{i}_{j}_{t}"
                )

        for i,j in G.edges():
            if (i,j) not in XA:
                for t in T_u[2]:
                    modelo_2.addConstr(
                        z[i,j,t] <= M_ij * y[i,j,1],  
                        name=f"restriccion_17.2_{i}_{j}_{t}"
                    )

        for i,j in G.edges():
            if (i,j) in XA:
                for t in T_u[2]:
                    modelo_2.addConstr(
                        z[i,j,t] <= M_ij * y[i,j,2],  
                        name=f"restriccion_17.2_{i}_{j}_{t}"
                    )

    
        
        modelo_1.setParam('MIPGap', 0.005)
        modelo_1.optimize()

        dic_pit = {}
        for i in N:
            for t in T:
                dic_pit[i,t] = p[i,t].X

        print("ingresos:", ingreso_venta.getValue())
        print("costo cosechar:", costos_cosechar.getValue())
        print("costo instalacion:", costos_instalacion.getValue())

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
                        name=f"restriccion_18_{n}_{t}"
                    )
        

        modelo_2.setParam('MIPGap', 0.05)
        modelo_2.optimize()

        print("costo transporte", costo_transporte_madera.getValue())
        print("costo construccion camino:", costo_construccion_caminos.getValue())

        ingreso_total = ingreso_venta - costos_cosechar - costos_instalacion - costo_construccion_caminos- costo_transporte_madera

        print(" Valor Funcion Objetivo:", ingreso_total.getValue())

        # Verificar el estado del modelo
        estado_1 = modelo_1.Status
        estado_2 = modelo_2.Status
        if estado_1 == GRB.Status.OPTIMAL and estado_2 == GRB.Status.OPTIMAL:
            print("ingresos:", ingreso_venta.getValue())
            print("costo cosechar:", costos_cosechar.getValue())
            print("costo instalacion:", costos_instalacion.getValue())
            print("costo transporte", costo_transporte_madera.getValue())
            print("costo construccion camino:", costo_construccion_caminos.getValue())
        
             # Diccionario con todos los resultados
            resultados = {
                'status': 'OPTIMAL',
                'valor_objetivo': ingreso_total.getValue(),
                'ingresos': ingreso_venta.getValue(),
                'costos': {
                    'cosecha': costos_cosechar.getValue(),
                    'instalacion': costos_instalacion.getValue(),
                    'transporte': costo_transporte_madera.getValue(),
                    'construccion_caminos': costo_construccion_caminos.getValue(),
                },
                'variables': {
                    'p': {(i, t): p[i, t].X for i in N for t in T},
                    'w': {(i, j, k, t): w[i, j, k, t].X 
                        for (i, k), datos_faena in R_jk.items() 
                        for j in datos_faena['radio'] 
                        for t in T },
                    'x': {(i, j, k, t): x[i, j, k, t].X 
                        for (i, k), datos_faena in R_jk.items() 
                        for j in datos_faena['radio'] 
                        for t in T },
                    'mu': {(i, k, u): mu[i, k, u].X 
                        for i in N for k in K for u in U},
                    'q': {(d, t): q[d, t].X for d in D for t in T},
                    'y': {(i,j,u): y[i,j,u].X for (i,j) in G.edges() for u in U},
                    'z': {(i,j,t): z[i,j,t].X for (i,j) in G.edges() for t in T},
                    's': {(r, u): s[r,u].X for r in range(1,20) for u in U}

                }
            }

            with open('resultados_modelo_simple.pkl', 'wb') as archivo:
                pickle.dump(resultados, archivo)

            print("Resultados guardados en 'resultados_modelo_simple.pkl'")
            visualizar_resultados()

        elif estado_1 == GRB.Status.INFEASIBLE:
            print("El modelo 1 es infactible.")
            modelo_1.computeIIS()
            modelo_1.write("modelo_cb_infactible.ilp") 
        elif estado_2 == GRB.Status.INFEASIBLE:
            print("El modelo 2 es infactible.")
            modelo_2.computeIIS()
            modelo_2.write("modelo_cb_infactible.ilp")

    except Exception as e:
        print(f"Error durante la ejecución del modelo: {str(e)}")
        modelo_1.computeIIS()
        modelo_1.write("modelo_cb_infactible.ilp")
        raise

def visualizar_resultados(archivo_pkl='resultados_modelo_simple.pkl', archivo_txt='resultados_modelo_simple.txt'):

    try:
        with open(archivo_pkl, 'rb') as archivo:
            datos = pickle.load(archivo)

        # Abrir archivo de texto en modo escritura
        with open(archivo_txt, 'w', encoding='utf-8') as txt_file:
            # Escribir los resultados en el archivo
            txt_file.write("\n" + "="*60 + "\n")
            txt_file.write("📊 VISUALIZACIÓN DE RESULTADOS DEL MODELO\n")
            txt_file.write("="*60 + "\n")
            
            # Información básica
            txt_file.write(f"\n🔵 Estado del modelo: {datos['status']}\n")
            txt_file.write(f"💰 Valor objetivo (ganancia neta): ${datos['valor_objetivo']:,.2f}\n")
            
            # Ingresos y costos
            txt_file.write("\n📈 DESGLOSE ECONÓMICO:\n")
            txt_file.write(f"  - Ingresos por venta: ${datos['ingresos']:,.2f}\n")
            for nombre, valor in datos['costos'].items():
                txt_file.write(f"  - Costo de {nombre}: ${valor:,.2f}\n")
            
            # Variables clave
            txt_file.write("\n🔧 VARIABLES RELEVANTES:\n")
            
            # Madera transportada (p)
            """txt_file.write("\n  🔸 Madera transportada (p):\n")
            for (nodo, periodo), cantidad in datos['variables']['p'].items():
                if cantidad > 0:
                    txt_file.write(f"    - Nodo {nodo}, período {periodo}: {cantidad:.2f} m3\n")"""
            
            # Asignaciones de cosecha (w)
            txt_file.write("\n  🔸 Faena Cosechada (x):\n")
            for (i, j, k, t), cantidad in datos['variables']['x'].items():
                if cantidad > 0:
                    txt_file.write(f"    - Faena {i} → Hectarea {j}, máquina {k}, período {t}, cosecha: {cantidad:.2f} \n")
            
            txt_file.write("\n  🔸 Madera Cosechada (w):\n")
            for (i, j, k, t), cantidad in datos['variables']['w'].items():
                if cantidad > 0:
                    txt_file.write(f"    - Faena {i} → Hectarea {j}, máquina {k}, período {t}, cosecha: {cantidad:.2f} m3\n")
            
            # Instalaciones (mu)
            txt_file.write("\n  🔸 Faenas Instaladas (mu):\n")
            for (i, k, t), valor in datos['variables']['mu'].items():
                if valor == 1:
                    txt_file.write(f"    - Nodo {i}, máquina {k}, período {t}\n")

            """txt_file.write("\n  🔸 Faenas Existentes (f):\n")
            for (i, k, t), valor in datos['variables']['f'].items():
                if valor == 1:
                    txt_file.write(f"    - Nodo {i}, máquina {k}, período {t}\n")"""

            txt_file.write("\n🛣️ INFRAESTRUCTURA DE CAMINOS:\n")
            
            # Caminos construidos (y) y existentes (l)
            txt_file.write("\n  🔸 Construcción de caminos (y):\n")
            for (i, j, t), valor in datos['variables']['y'].items():
                if valor == 1:
                    txt_file.write(f"    - Construido: {i} ↔ {j} en período {t}\n")
             
            """txt_file.write("\n  🔸 Caminos existentes (l):\n")
            for (i, j, t), valor in datos['variables']['l'].items():
                if valor == 1:
                    txt_file.write(f"    - Disponible: {i} ↔ {j} en período {t}\n")"""
            
            """# Transporte de madera (z)
            txt_file.write("\n  🔸 Flujo de madera (z):\n")
            for (i, j, t), cantidad in datos['variables']['z'].items():
                if cantidad > 0:
                    txt_file.write(f"    - Transportado: {cantidad:.2f} m³ por {i} ↔ {j} en período {t}\n")"""
            
            txt_file.write("\n✅ Resultados guardados correctamente\n")

        print(f"Los resultados se han guardado en el archivo: {archivo_txt}")
                
    except FileNotFoundError:
        print(f"\n⚠️ Error: No se encontró el archivo {archivo_pkl}")
    except Exception as e:
        print(f"\n⚠️ Error al visualizar resultados: {str(e)}")

if __name__ == "__main__":
    main()