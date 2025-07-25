from gurobipy import *
from datos import *
from grafos import *
#from guardar_sol import *
import pickle


def main():
    try:
        modelo_1 = Model("Asignacion_cosecha")
        modelo_2 = Model("Camino_flujo_cosecha")
        #modelo.ModelSense = GRB.MAXIMIZE

        #======= DEFINICION DE VARIABLES ==========#
        
        # Variable Binaria Instalacion y existencia de maquinaria
        mu = {}
        f = {}
        for k in K:
            for i in N:
                for t in T:
                    mu[i,k,t] = modelo_1.addVar(vtype=GRB.BINARY, name=f"mu_{i}_{k}_{t}")
                    f[i,k,t] = modelo_1.addVar(vtype=GRB.BINARY, name=f"f_{i}_{k}_{t}")
        
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
                    name=f"restriccion_1_{i}_{t}"
                )
        
        # 2. Cosechar hectáreas solo del radio de cosecha
        for (i, k), datos_faena in R_jk.items():
            for j in datos_faena['radio']:
                for t in T:
                    modelo_1.addConstr(w[i, j, k, t] <= N[j]['v'] * x[i, j, k, t], name=f'restriccion_2_{i}_{j}_{k}_{t}')

        # 3. Que no exista más de una faena por hectárea
        for i in N:
            for t in T:
                modelo_1.addConstr(quicksum(f[i, k, t] for k in K) <= 1, name=f"restriccion_3_{i}_{j}_{k}")

        # 4. Relación entre faena y faena instalada
        for i in N:
            for k in K:
                for t in T:
                    if t in [1, 13]:
                        modelo_1.addConstr(mu[i, k, t] == f[i, k, t], name=f"restriccion_4_{i}_{j}_{k}")

        # 5. Continuidad de la faena
        for i in N:
            for k in K:
                for t in T:
                    if t not in [1, 13]:
                        modelo_1.addConstr(f[i, k, t] == f[i, k, t - 1] + mu[i, k, t], name=f'restriccion_5_{i}_{j}_{k}')
        
        # Asignacion de cosecha desde una hectarea faena a una hectarea no-faena
        # 6.    
        for i in N:
            for k in K:
                for t in T:
                    if (i,k) in R_jk:
                        for j in R_jk[(i,k)]['radio']:
                            if i == j:
                                modelo_1.addConstr(x[i,j,k,t] == f[i,k,t], name=f"restriccion_6_{i}_{j}_{k}_{t}")
                            else:
                                modelo_1.addConstr(x[i,j,k,t] <= f[i,k,t], name=f"restriccion_6_{i}_{j}_{k}_{t}")

        for i in N:
            for t in T:
                indices_efectivos = []
                for j in nodos_skidders:
                    cobertura = R_jk[j,'skidder']
                    if i in cobertura:
                        indices_efectivos.append([j,'skidder'])
                for j in nodos_torres:
                    cobertura = R_jk[j,'torre']
                    if i in cobertura:
                        indices_efectivos.append([j,'torre'])
                modelo_1.addConstr(quicksum(x[key[0],i,key[1],t_] 
                                    for key in indices_efectivos 
                                        if key[0] != i for t_ in range(t,19) 
                                        if t_ not in list(range(7,13))) <= (1 - quicksum(mu[i,k,t] for k in K)) * M_rnueva,
                                        name="restriccion_nueva")

        
        # 7.
        for j in N:
            for t in T:
                for k in K:
                    modelo_1.addConstr(
                    quicksum(x[i,j,k,t] for (i,b), datos_faena in R_jk.items()
                                        if j in datos_faena['radio'] and b == k) <= 1,
                    name=f"restriccion_7_{j}_{k}_{t}"
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
        for r in rodales:
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
                )

        # Rodales adyacentes no pueden cosecharse en la misma temporada
        # 11.
        """for r in RA_r:  
            for a in RA_r[r]: 
                for u in U:
                    modelo_1.addConstr(
                        s[r,u] + s[a,u] <= 1,
                        name=f"restriccion_11_{r}_{a}_{u}"
                    )"""

        # Actualización del estado del camino para períodos normales
        # 12.
        for (i,j) in G.edges():
            for t in T:
                if t != 1 and t != 13:  # T \ {1, 13}
                    modelo_2.addConstr(
                        l[i,j,t] == l[i,j,t-1] + y[i,j,t],
                        name=f"restriccion_12_{i}_{j}_{t}"
                    )

        # Actualización del estado del camino para período 13 (excluyendo XA)
        # 13:
        for i, j in G.edges():
            if G[i][j]["XA"] == False:  # A \ XA    
                modelo_2.addConstr(
                    l[i,j,13] == l[i,j,6] + y[i,j,13],
                    name=f"restriccion_13_{i}_{j}"
                )

        #######

        # Restricción de simetria 1: y[i,j,t] >= y[i,j,t+1] para t en la temporada 1 (meses 1-6)
        for (i,j) in G.edges():
            for t in range(1, 6):
                modelo_2.addConstr(
                    y[i,j,t] >= y[i,j,t+1],
                    name=f"restriccion_simetria_1_{i}_{j}_{t}"
                )

        # Restricción de simetria 2: y[i,j,t] >= y[i,j,t+1] para t en la temporada 2 (meses 13-18)
        for (i,j) in G.edges():
            for t in range(13, 18): 
                modelo_2.addConstr(
                    y[i,j,t] >= y[i,j,t+1],
                    name=f"restriccion_simetria_2_{i}_{j}_{t}"
                ) 

        # Inicialización del camino en período 1
        # 14.
        for i, j in G.edges():
            modelo_2.addConstr(
                y[i,j,1] == l[i,j,1],
                name=f"restriccion_14_{i}_{j}"
            )

        # Camino en período 13 para arcos en XA
        # 15.
        for i, j in G.edges():
            if G[i][j]["XA"] == True:
                modelo_2.addConstr(
                    y[i,j,13] == l[i,j,13],
                    name=f"restriccion_15_{i}_{j}"
                )


        # R auxiliar
        for i,j in G.edges():
            for t in T:
                modelo_2.addConstr(
                    y[i,j,t] == y[j,i,t],
                    name="Restriccion_direccion_caminos"
                )


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
            for t in T:
                modelo_2.addConstr(
                    z[i,j,t] <= M_ij * l[i,j,t],  
                    name=f"restriccion_17_{i}_{j}_{t}"
                )

    
        
        modelo_1.setParam('MIPGap', 0.01)
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
        

        modelo_2.setParam('MIPGap', 0.09)
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
                    'mu': {(i, k, t): mu[i, k, t].X 
                        for i in N for k in K for t in T},
                    'f': {(i, k, t): f[i, k, t].X 
                        for i in N for k in K for t in T},
                    'q': {(d, t): q[d, t].X for d in D for t in T},
                    'y': {(i,j,t): y[i,j,t].X for (i,j) in G.edges() for t in T},
                    'l': {(i,j,t): l[i,j,t].X for (i,j) in G.edges() for t in T},
                    'z': {(i,j,t): z[i,j,t].X for (i,j) in G.edges() for t in T},
                    's': {(r, u): s[r,u].X for r in range(1,20) for u in U}

                }
            }

            with open('resultados_modelo.pkl', 'wb') as archivo:
                pickle.dump(resultados, archivo)

            print("Resultados guardados en 'resultados_modelo.pkl'")
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

def visualizar_resultados(archivo_pkl='resultados_modelo.pkl', archivo_txt='resultados_modelo.txt'):

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