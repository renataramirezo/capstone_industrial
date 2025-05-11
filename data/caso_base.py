import sys

import networkx as nx
import matplotlib.pyplot as plt
import grafos as gf
import datos as dt

plt.title("Rodales")
plt.show()
cap_rodales = {}

for rodal in range(1, 20):
    volumen_rodal = 0
    for hect in dt.rodales[rodal]:
        volumen_rodal += dt.N[hect]["v"]
        cap_rodales[rodal] = volumen_rodal
#print(cap_rodales)
ordenado = sorted(cap_rodales.items(), key=lambda x: x[1], reverse=True)
'''dado este orden, y las restricciones de adyacencia decidimos
 instalar las faenas skider en los nodos: 37, 142, 180
 y las faenas torres en: 58'''



bases_faena_s = [37, 142, 180]#se ingresa a mano
bases_faena_t = [58]#se ingresa a mano
nodos_a_cosechar_sk = []
for base in bases_faena_s:
    for hect in dt.R_jk[(base, "skidder")]["radio"]:
        nodos_a_cosechar_sk.append(hect)
nodos_a_cosechar_t = []
for base in bases_faena_t:
    for hect in dt.R_jk[(base, "torre")]["radio"]:
        nodos_a_cosechar_t.append(hect)
#print(nodos_a_cosechar_t)
#print(nodos_a_cosechar_sk)
rodales_inicial = set() #este set contiene todos los rodales que son tocados por R_jk 
for nodo in nodos_a_cosechar_sk + nodos_a_cosechar_t:
    rodales_inicial.add(gf.G.nodes[nodo]["r"])
'''
 Por las restricciones de adyacencia, decidimos manualmente cosehar
  en la primera temporada los siguientes
    rodales: 17	18	15	19	4	7	1	2	12
no cosecho las hectáreas que pertenecen a los rodales
16, 14, 8, 6 a pesar de que sí están en el radio'''
rodal_excluido = {16, 14, 8, 6} #se ingresa a mano
nodos_a_cosechar_sk = [
    nodo for nodo in nodos_a_cosechar_sk
    if gf.G.nodes[nodo]["r"] not in rodal_excluido
]

nodos_a_cosechar_t = [
    nodo for nodo in nodos_a_cosechar_t
    if gf.G.nodes[nodo]["r"] not in rodal_excluido
]
node_colors_gris = ["grey"] * len(gf.G.nodes())

#print(nodos_a_cosechar_t)'''

Orden= list(gf.G.nodes())
for nodo in nodos_a_cosechar_sk:
    node_colors_gris[Orden.index(nodo)] = "deeppink"
for nodo in nodos_a_cosechar_t:
    node_colors_gris[Orden.index(nodo)] = "red"
for nodo in bases_faena_s + bases_faena_t:
    node_colors_gris[Orden.index(nodo)] = "white"

node_colors_gris[gf.Posicion169] = "yellow"
node_colors_gris[gf.Posicion147] = "yellow"


# Dibujar nodos y aristas
nx.draw(gf.G, gf.pos, with_labels=True, edge_color=gf.edge_colors,
         node_color=node_colors_gris, edgecolors= gf.nodo_bordes_faen, 
         linewidths= 1.5,node_size=150, font_weight='bold', font_size=5)
#gf.ax2.set_title("Grafo asignación cosecha primera temporada")
#plt.show()

#sumar cantidad de madera en nodos a cosechar por faena
base_cant_madera_s = {}# diccionario: (id_base: suma v de radio operante)
for base in bases_faena_s:
    suma_madera = gf.G.nodes[base]["v"]
    for nodo in gf.G.nodes[base]["R_jk"]:
        if gf.G.nodes[nodo]["r"] not in rodal_excluido:
            suma_madera += gf.G.nodes[nodo]["v"]
        base_cant_madera_s[base] = suma_madera
base_cant_madera_t = {}# diccionario: (id_base: suma v de radio operante)
costo_instalación_faenas = 0
for base in bases_faena_t:
    costo_instalación_faenas += gf.G.nodes[base]["cf"]
    suma_madera = gf.G.nodes[base]["v"]
    for nodo in gf.G.nodes[base]["R_jk"]:
        if gf.G.nodes[nodo]["r"] not in rodal_excluido:
            suma_madera += gf.G.nodes[nodo]["v"]
        base_cant_madera_t[base] = suma_madera
#print(base_cant_madera_t, base_cant_madera_s)

total_volumen_cosechado = 0
for base in base_cant_madera_t:
    costo_instalación_faenas += gf.G.nodes[base]["cf"]
    suma_madera = gf.G.nodes[base]["v"]
    if base_cant_madera_t[base] <= 6*dt.K["torre"]["mcc"]:
        total_volumen_cosechado += base_cant_madera_t[base]
        
    else:
        print(f"queda {base_cant_madera_t[base]-6*dt.K['torre']['mcc']} madera")
        #print(f"base{base_cant_madera_t[base]}")
        
        #print(f"se cosechó todo en la temporada{total_volumen_cosechado}")
for base in base_cant_madera_s:
    if base_cant_madera_s[base] <= 6*dt.K["skidder"]["mcc"]:
        total_volumen_cosechado += base_cant_madera_s[base]
        
    else:
        print(f"queda {base_cant_madera_s[base]-6*dt.K['skidder']['mcc']} madera")
        #print(f"se cosechó todo en la temporada{total_volumen_cosechado}")
'''En las cuatro faenas instaladas se cosechó todo por lo tanto
 procedamos a los cálculos de cosecha'''
print(f"el total cosechado por las faenas fue: {total_volumen_cosechado}")
costo_var_cosecha_t = 0
for base in base_cant_madera_t:
    costo_var_cosecha_t += base*gf.G.nodes[base]["cv_rad"]
costo_var_cosecha_s = 0
for base in base_cant_madera_s:
    vol_base = gf.G.nodes[base]["v"]
    costo_var_cosecha_s += (base - vol_base) * gf.G.nodes[base]["cv_rad"] + vol_base * gf.G.nodes[base]["cv_base"]

#resultado asignación aún sin caminos
utilidad_neta_asignacion = total_volumen_cosechado * dt.P - costo_instalación_faenas - costo_var_cosecha_s - costo_var_cosecha_t
print (f"la utilidad neta de asignación de la temporada 1 fue: {utilidad_neta_asignacion}")

# Almacenar las mejores rutas y sus costos
mejores_rutas = {}

for base in bases_faena_s + bases_faena_t:
    mejor_ruta = None
    menor_costo = float("inf")

    for salida in dt.D:
        try:
            ruta = nx.shortest_path(gf.G, source=base, target=salida, weight="C")
            costo = nx.shortest_path_length(gf.G, source=base, target=salida, weight="C")

            if costo < menor_costo:
                menor_costo = costo
                mejor_ruta = ruta

        except nx.NetworkXNoPath:
            continue  # no hay camino posible

    if mejor_ruta:
        mejores_rutas[base] = {"ruta": mejor_ruta, "costo": menor_costo}
#print(mejores_rutas)
#############------------------------
# 2. Obtener los arcos de la ruta como pares (u, v)
ruta_arcos = set()
for base in mejores_rutas:
    #print(base)
    inicio = mejores_rutas[base]["ruta"][:-1]
    fin= mejores_rutas[base]["ruta"][1:]
    camino = set(zip(inicio,fin))
    ruta_arcos.update(camino)
ruta_arcos.update({(142,141)})
elementos_a_eliminar_t1 = {(145,148), (148,147), (142,145)}
ruta_arcos.difference_update(elementos_a_eliminar_t1)
#print(ruta_arcos)
costo_construccion = 0
for camino in ruta_arcos:
    costo_construccion += dt.C
costo_transporte = dt.ct * total_volumen_cosechado

Utilidad_primera_temporada = utilidad_neta_asignacion - costo_construccion - costo_transporte
print(f"La utilidad total de la primera temporada fue: {Utilidad_primera_temporada}")

# 3. Dibujar encima esos arcos con mayor grosor y color llamativo
nx.draw_networkx_edges(
    gf.G,
    gf.pos,
    edgelist=ruta_arcos,
    edge_color="black",    # o el color que desees
    width=10             # más grueso para que destaque
)

# 4. Mostrar el plot
plt.title("Primera temporada")
plt.show()

'''Ahora empezamos a ver la TEMPORADA DOS dos, 
por eso vaciamos de contenido los rodales cosechados 
y volvemos a ver dónde conviene instalar las bases faenas.
Atención si hay caminos que se destruyen, deben ser eliminados'''
for nodo in nodos_a_cosechar_sk+nodos_a_cosechar_t+bases_faena_s+bases_faena_t:
    gf.G.nodes[nodo]["v"] = 0
for rodal in range(1, 20):
    volumen_rodal = 0
    for hect in dt.rodales[rodal]:
        volumen_rodal += gf.G.nodes[hect]["v"]
        cap_rodales[rodal] = volumen_rodal
#print(cap_rodales)
ordenado = sorted(cap_rodales.items(), key=lambda x: x[1], reverse=True)
#print(ordenado)
'''orden de prioridad rodales temporada 2: 
16,14,8,11,9,6,18,10,12,1,19,13,3,2,17,5,15,4,7
'''
Orden= list(gf.G.nodes())
for nodo in nodos_a_cosechar_sk:
    gf.node_colors_rod[Orden.index(nodo)] = "white"
for nodo in nodos_a_cosechar_t:
    gf.node_colors_rod[Orden.index(nodo)] = "white"
for nodo in bases_faena_s + bases_faena_t:
    gf.node_colors_rod[Orden.index(nodo)] = "white"

nx.draw(gf.G, gf.pos, with_labels=True, edge_color=gf.edge_colors,
         node_color=gf.node_colors_rod, edgecolors= gf.nodo_bordes_faen, 
         linewidths= 1.5,node_size=150, font_weight='bold', font_size=5)
nx.draw_networkx_edges(
    gf.G,
    gf.pos,
    edgelist=ruta_arcos,
    edge_color="black",    # o el color que desees
    width=10             # más grueso para que destaque
)
#plt.show()

'''Por lo tanto pondremos 3 skidders y una torre
skidders: 103, 160, 130
torres: 33

Por otro lado los nodos que estén en los rodales:
12, 9, 17,  7, 2, 4, 15 no serán cosechados
'''
bases_faena_s_t2 = [103, 160, 130]#se ingresa a mano
bases_faena_t_t2 = [36]#se ingresa a mano
nodos_a_cosechar_sk_t2 = []
for base in bases_faena_s_t2:
    for hect in dt.R_jk[(base, "skidder")]["radio"]:
        nodos_a_cosechar_sk_t2.append(hect)
nodos_a_cosechar_t_t2 = []
for base in bases_faena_t_t2:
    for hect in dt.R_jk[(base, "torre")]["radio"]:
        nodos_a_cosechar_t_t2.append(hect)
#print(nodos_a_cosechar_t)
#print(nodos_a_cosechar_sk)
rodales_inicial_t2 = set() #este set contiene todos los rodales que son tocados por R_jk 
for nodo in nodos_a_cosechar_sk_t2 + nodos_a_cosechar_t_t2:
    rodales_inicial_t2.add(gf.G.nodes[nodo]["r"])
'''
 Por las restricciones de adyacencia, decidimos manualmente cosehar
  en la primera temporada los siguientes
    rodales: 16, 14,8,11,13,3,6
no cosecho las hectáreas que pertenecen a los rodales
12, 9, 17,  7, 2, 5, 4, 15 a pesar de que sí están en el radio'''
rodal_excluido_t2 = {12, 9, 5, 17, 7, 2, 4, 15} #se ingresa a mano
nodos_a_cosechar_sk_t2 = [
    nodo for nodo in nodos_a_cosechar_sk_t2
    if gf.G.nodes[nodo]["r"] not in rodal_excluido_t2
]

nodos_a_cosechar_t_t2 = [
    nodo for nodo in nodos_a_cosechar_t_t2
    if gf.G.nodes[nodo]["r"] not in rodal_excluido_t2
]

#print(nodos_a_cosechar_t)'''
node_colors_rod_t2 = ["grey"] * len(gf.G.nodes())

Orden= list(gf.G.nodes())
for nodo in nodos_a_cosechar_sk_t2:
    node_colors_rod_t2[Orden.index(nodo)] = "deeppink"
for nodo in nodos_a_cosechar_t_t2:
    node_colors_rod_t2[Orden.index(nodo)] = "red"
for nodo in bases_faena_s_t2 + bases_faena_t_t2:
    node_colors_rod_t2[Orden.index(nodo)] = "white"

node_colors_rod_t2[gf.Posicion169] = "yellow"
node_colors_rod_t2[gf.Posicion147] = "yellow"

# Dibujar nodos y aristas
nx.draw(gf.G, gf.pos, with_labels=True, edge_color=gf.edge_colors,
         node_color=node_colors_rod_t2, edgecolors= gf.nodo_bordes_faen, 
         linewidths= 1.5,node_size=150, font_weight='bold', font_size=5)
#gf.ax2.set_title("Grafo asignación cosecha segunda temporada")
#plt.show()

#sumar cantidad de madera en nodos a cosechar por faena
base_cant_madera_s_t2 = {}# diccionario: (id_base: suma v de radio operante)
for base in bases_faena_s_t2:
    suma_madera_t2 = gf.G.nodes[base]["v"]
    for nodo in gf.G.nodes[base]["R_jk"]:
        if gf.G.nodes[nodo]["r"] not in rodal_excluido_t2:
            suma_madera_t2 += gf.G.nodes[nodo]["v"]
        base_cant_madera_s_t2[base] = suma_madera_t2
base_cant_madera_t_t2 = {}# diccionario: (id_base: suma v de radio operante)
costo_instalación_faenas_t2 = 0
for base in bases_faena_t_t2:
    costo_instalación_faenas_t2 += gf.G.nodes[base]["cf"]
    suma_madera_t2 = gf.G.nodes[base]["v"]
    for nodo in gf.G.nodes[base]["R_jk"]:
        if gf.G.nodes[nodo]["r"] not in rodal_excluido_t2:
            suma_madera_t2 += gf.G.nodes[nodo]["v"]
        base_cant_madera_t_t2[base] = suma_madera_t2
#print(base_cant_madera_t, base_cant_madera_s)

total_volumen_cosechado_t2 = 0
for base in base_cant_madera_t_t2:
    costo_instalación_faenas_t2 += gf.G.nodes[base]["cf"]
    suma_madera_t2 = gf.G.nodes[base]["v"]
    if base_cant_madera_t_t2[base] <= 6*dt.K["torre"]["mcc"]:
        total_volumen_cosechado_t2 += base_cant_madera_t_t2[base]
        
    else:
        print(f"queda {base_cant_madera_t_t2[base]-6*dt.K['torre']['mcc']} madera")
        #print(f"base{base_cant_madera_t[base]}")
        
        #print(f"se cosechó todo en la temporada{total_volumen_cosechado}")
for base in base_cant_madera_s_t2:
    if base_cant_madera_s_t2[base] <= 6*dt.K["skidder"]["mcc"]:
        total_volumen_cosechado_t2 += base_cant_madera_s_t2[base]
        
    else:
        print(f"queda {base_cant_madera_s_t2[base]-6*dt.K['skidder']['mcc']} madera")
        #print(f"se cosechó todo en la temporada{total_volumen_cosechado}")
'''En las cuatro faenas instaladas se cosechó todo por lo tanto
 procedamos a los cálculos de cosecha'''
print(f"el total cosechado por las faenas fue en t2: {total_volumen_cosechado_t2}")
costo_var_cosecha_t_t2 = 0
for base in base_cant_madera_t_t2:
    costo_var_cosecha_t_t2 += base*gf.G.nodes[base]["cv_rad"]
costo_var_cosecha_s_t2 = 0
for base in base_cant_madera_s_t2:
    vol_base_t2 = gf.G.nodes[base]["v"]
    costo_var_cosecha_s_t2 += (base - vol_base_t2) * gf.G.nodes[base]["cv_rad"] + vol_base_t2 * gf.G.nodes[base]["cv_base"]

#resultado asignación aún sin caminos
utilidad_neta_asignacion_t2 = total_volumen_cosechado_t2 * dt.P - costo_instalación_faenas_t2 - costo_var_cosecha_s_t2 - costo_var_cosecha_t_t2
print (f"la utilidad neta de asignación de la temporada 2 fue: {utilidad_neta_asignacion_t2}")

# Almacenar las mejores rutas y sus costos
mejores_rutas_t2 = {}

for base in bases_faena_s_t2 + bases_faena_t_t2:
    mejor_ruta_t2 = None
    menor_costo_t2 = float("inf")

    for salida in dt.D:
        try:
            ruta_t2 = nx.shortest_path(gf.G, source=base, target=salida, weight="C")
            costo_t2 = nx.shortest_path_length(gf.G, source=base, target=salida, weight="C")

            if costo_t2 < menor_costo_t2:
                menor_costo_t2 = costo_t2
                mejor_ruta_t2 = ruta_t2

        except nx.NetworkXNoPath:
            continue  # no hay camino posible

    if mejor_ruta_t2:
        mejores_rutas_t2[base] = {"ruta": mejor_ruta_t2, "costo": menor_costo_t2}
#print(mejores_rutas)
#############------------------------
# 2. Obtener los arcos de la ruta como pares (u, v)
ruta_arcos_t2 = set()
for base in mejores_rutas_t2:
    #print(base)
    inicio_t2 = mejores_rutas_t2[base]["ruta"][:-1]
    fin_t2= mejores_rutas_t2[base]["ruta"][1:]
    camino_t2 = set(zip(inicio_t2,fin_t2))
    ruta_arcos_t2.update(camino_t2)
ruta_arcos_t2.update({(39,38)})
elementos_a_eliminar = {(160,161), (161,165), (165,168), (39,42), (42,85), (85,86), (86,93), (93,94), (94,95), (95,96)}

ruta_arcos_t2.difference_update(elementos_a_eliminar)

#print(ruta_arcos_t2)
#print(ruta_arcos)
costo_construccion_t2 = 0
for camino in ruta_arcos_t2:
    costo_construccion_t2 += dt.C
costo_transporte_t2 = dt.ct * total_volumen_cosechado_t2

Utilidad_segunda_temporada = utilidad_neta_asignacion_t2 - costo_construccion_t2 - costo_transporte_t2
print(f"La utilidad total de la segunda temporada fue: {Utilidad_segunda_temporada}")
print(f"La utilidad total de la ambas temporadas fue: {Utilidad_primera_temporada+Utilidad_segunda_temporada}")

# 3. Dibujar encima esos arcos con mayor grosor y color llamativo
nx.draw_networkx_edges(
    gf.G,
    gf.pos,
    edgelist=ruta_arcos_t2,
    edge_color="black",    # o el color que desees
    width=10             # más grueso para que destaque
)

# 4. Mostrar el plot
plt.title("Ruta más corta sobre grafo original")
plt.show()
print(f"arcos que construye la primera temporada: {ruta_arcos}")
print(f"arcos que construye la segunda temporada: {ruta_arcos_t2}")
print(f"faenas skideer instaladas la primera temporada: {bases_faena_s}")
print(f"faenas torre instaladas la primera temporada: {bases_faena_t}")
print(f"faenas skideer instaladas la segunda temporada: {bases_faena_s_t2}")
print(f"faenas torre instaladas la segunda temporada: {bases_faena_t_t2}")
print(f"nodos cosechados primera temporada por bases skidder: {nodos_a_cosechar_sk} en todos ellos se cosechó toda la madera")
print(f"nodos cosechados primera temporada por bases torre: {nodos_a_cosechar_t} en todos ellos se cosechó toda la madera")
print(f"nodos cosechados segunda temporada por bases skidder: {nodos_a_cosechar_sk_t2} en todos ellos se cosechó toda la madera")
print(f"nodos cosechados segunda temporada por bases torre: {nodos_a_cosechar_t_t2} en todos ellos se cosechó toda la madera")
