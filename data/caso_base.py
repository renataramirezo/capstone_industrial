import sys

import networkx as nx
import matplotlib.pyplot as plt
import grafos as gf
import datos as dt

#######################################################
###########----- PRIMERA TEMPORADA-----################
#######################################################

'''Primero ordenamos los rodales según la cantidad de madera que tienen disponible'''
cap_rodales = {}
for rodal in range(1, 20):
    volumen_rodal = 0
    for hect in dt.rodales[rodal]:
        volumen_rodal += dt.N[hect]["v"]
        cap_rodales[rodal] = volumen_rodal
#print(cap_rodales)
ordenado = sorted(cap_rodales.items(), key=lambda x: x[1], reverse=True)
#print(ordenado)

'''dado este orden, y las restricciones de adyacencia decidimos
 instalar las faenas skider en los nodos: 37 142	180
 y las faenas torres en: 58'''

bases_faena_s = [8, 104, 180, 130, 141, 202]#[37, 142, 180]#se ingresa a mano
bases_faena_t = [62, 39]#[58]#se ingresa a mano

'''comenzamos la cosechar con bases SKIDDERS
y hacemos lista de los nodos que serán cosechados 
que son todos los que pertenecen al radio de cosecha 
de la base'''
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
    rodales: 17	15	14	7	1	4	19 11 3 13 9
no cosecho las hectáreas que pertenecen a los rodales
2, 6, 8, 5, 10, 12, 16, 18 a pesar de que sí están en el radio.
Por lo tanto se quitan del listado de nodos a cosechar los que están 
en un rodal con restricción de adyacencia'''
rodal_excluido = {2, 6, 8, 5, 10, 12, 16, 18} #se ingresa a mano
nodos_a_cosechar_sk = [
    nodo for nodo in nodos_a_cosechar_sk
    if gf.G.nodes[nodo]["r"] not in rodal_excluido
]

nodos_a_cosechar_t = [
    nodo for nodo in nodos_a_cosechar_t
    if gf.G.nodes[nodo]["r"] not in rodal_excluido
]

#######################################################
######-----GRAFO PRIMERA TEMPORADA-----################
#######################################################
'''Pintamos los nodos de colores según si son:
Base Faena
Salida
Cosechados por faena K
'''
node_colors_gris = ["white"] * len(gf.G.nodes())
#print(nodos_a_cosechar_t)
Orden= list(gf.G.nodes())
for nodo in nodos_a_cosechar_sk:
    node_colors_gris[Orden.index(nodo)] = "deeppink"
for nodo in nodos_a_cosechar_t:
    node_colors_gris[Orden.index(nodo)] = "red"
for nodo in bases_faena_s + bases_faena_t:
    node_colors_gris[Orden.index(nodo)] = "blue"
node_colors_gris[gf.Posicion169] = "yellow"
node_colors_gris[gf.Posicion147] = "yellow"


# Dibujar nodos y aristas
nx.draw(gf.G, gf.pos, with_labels=True, 
        #edge_color=gf.edge_colors,
         node_color=node_colors_gris, 
         #edgecolors= gf.nodo_bordes_faen, 
         linewidths= 1.5,node_size=150, font_weight='bold', font_size=5)
gf.plt.title("Grafo asignación cosecha primera temporada")
#plt.show()

'''Comenzamos con el cálculo de costos y volumenes de la primera temporada'''
#SKIDDER sumar cantidad de madera en nodos a cosechar por faena
base_cant_madera_s = {}# diccionario: (id_base: suma v de radio operante)
costo_instalacion_faenas = 0
for base in bases_faena_s:
    costo_instalacion_faenas += gf.G.nodes[base]["cf"]
    suma_madera = gf.G.nodes[base]["v"] #se suma el volumen que se cosecha en la misma base
    for nodo in gf.G.nodes[base]["R_jk"]:
        if gf.G.nodes[nodo]["r"] not in rodal_excluido:
            suma_madera += gf.G.nodes[nodo]["v"] #se suma el volumen de los nodes cosechados del radio
            base_cant_madera_s[base] = suma_madera
        else:
            base_cant_madera_s[base] = suma_madera

#TORRE sumar cantidad de madera en nodos a cosechar por faena
base_cant_madera_t = {}# diccionario: (id_base: suma v de radio operante)
for base in bases_faena_t:
    costo_instalacion_faenas += gf.G.nodes[base]["cf"]
    suma_madera = gf.G.nodes[base]["v"]
    for nodo in gf.G.nodes[base]["R_jk"]:
        if gf.G.nodes[nodo]["r"] not in rodal_excluido:
            suma_madera += gf.G.nodes[nodo]["v"] #se suma el volumen de los nodes cosechados del radio
        base_cant_madera_t[base] = suma_madera
#print(f"cantidad madera cosechada por faena de torre: {base_cant_madera_t}, cantidda madera cosechada por faena de skidder:{base_cant_madera_s}")

'''sumamos el total del volumen cosechado'''
total_volumen_cosechado = 0
'''TORRE revisamos si el volumen cosechado es menor a la capacidad de la maquinaria para 6 meses'''
for base in base_cant_madera_t:
    if base_cant_madera_t[base] <= 6*dt.K["torre"]["mcc"]: 
        total_volumen_cosechado += base_cant_madera_t[base] #como se puede cosechar todo, se cosecha todo
    else:
        print(f"queda {base_cant_madera_t[base]-6*dt.K['torre']['mcc']} madera")
        #print(f"base{base_cant_madera_t[base]}")
'''SKIDDER revisamos si el volumen cosechado es menor a la capacidad de la maquinaria para 6 meses'''       
        #print(f"se cosechó todo en la temporada{total_volumen_cosechado}")
for base in base_cant_madera_s:
    if base_cant_madera_s[base] <= 6*dt.K["skidder"]["mcc"]:
        total_volumen_cosechado += base_cant_madera_s[base]  #como se puede cosechar todo, se cosecha todo
    else:
        print(f"queda {base_cant_madera_s[base]-6*dt.K['skidder']['mcc']} madera")
        #print(f"se cosechó todo en la temporada{total_volumen_cosechado}")
'''En las 8 faenas instaladas se cosechó todo por lo tanto
 procedamos a los cálculos costos variables de cosecha'''

#TORRE COSTO VARIABLE
costo_var_cosecha_t = 0
for base in base_cant_madera_t:
    #print(f"valor que está printeando base{base}")
    costo_var_cosecha_t += gf.G.nodes[base]["cv_rad"]*base_cant_madera_t[base]
#SKIDDER COSTO VARIABLE
costo_var_cosecha_s = 0
for base in base_cant_madera_s:
    #vol_base = gf.G.nodes[base]["v"]
    costo_var_cosecha_s +=  gf.G.nodes[base]["cv_rad"]*base_cant_madera_s[base]
'''print(f"costo_variable cosecha skidder: {costo_var_cosecha_s}")
print(f"costo_variable cosecha torre: {costo_var_cosecha_t}")
print(f"costo instalación faena: {costo_instalacion_faenas}")'''
#resultado asignación aún sin caminos
utilidad_neta_asignacion = total_volumen_cosechado * dt.P - costo_instalacion_faenas - costo_var_cosecha_s - costo_var_cosecha_t
#print (f"la utilidad neta de asignación de la temporada 1 fue: {utilidad_neta_asignacion}")

'''Construímos los caminos'''
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
'''al ver el gráfico, como hay un camino que pasa por una parte que se destruye y es igual si 
lo hacemos por otro que no se destruye editamos manualemnte la construcción de caminos, 
tambien para que sea eficiente la segunda temporada'''
#AQUI
ruta_arcos.update({(129,130), (139,138), (175, 167), (180, 175), (100, 104)}) 
elementos_a_eliminar_t1 = {(143,146), (140,143), (137,140), (133, 137), 
                           (129, 133), (148,147), (139, 142), (142, 145), 
                           (145, 148), (180, 181), (181, 176), (176, 177), 
                           (177, 169), (100, 101), (101, 105), (105, 109)}
ruta_arcos.difference_update(elementos_a_eliminar_t1)
#print(ruta_arcos)

'''Comenzamos a calcular costos de construcción'''
costo_construccion = 0
for camino in ruta_arcos:
    costo_construccion += dt.C
costo_transporte = dt.ct * total_volumen_cosechado #esto es una simplificación, 
#se está transportando toda la madera por todos los caminos por lo tanto el costo saldrá más alto que la realidad
'''print(f"costo_transporte: {costo_transporte}")
print(f"costo construcción: {costo_construccion}")'''

Utilidad_primera_temporada = utilidad_neta_asignacion - costo_construccion - costo_transporte
#print(f"La utilidad total de la primera temporada fue: {Utilidad_primera_temporada}")

######GRAFO CON CAMINOS PRIMERA TEMPORADA#####
# 3. Dibujar encima esos arcos con mayor grosor y color llamativo
nx.draw_networkx_edges(
    gf.G,
    gf.pos,
    edgelist=ruta_arcos,
    edge_color="orange",    # o el color que desees
    width=10             # más grueso para que destaque
)
plt.title("Ruta más corta sobre grafo original")
plt.show()

set_nodos_sk_1=set(nodos_a_cosechar_sk)
set_nodos_tr_1 =set(nodos_a_cosechar_t)
set_faenas_sk_1=set(bases_faena_s)
set_faenas_tr_1=set(bases_faena_t)

cantidad_cosechada_temporada_1 = 0
setcosechadostemp1=set(nodos_a_cosechar_sk + nodos_a_cosechar_t + bases_faena_s + bases_faena_t)
for nodo in setcosechadostemp1:
    cantidad_cosechada_temporada_1+=gf.G.nodes[nodo]["v"]

costo_variable_cosecha_sk_temp1 = 0
for nodo in set_nodos_sk_1-set_faenas_sk_1:
    costo_variable_cosecha_sk_temp1+=gf.G.nodes[nodo]["v"]*14
for nodo in set_faenas_sk_1:
    costo_variable_cosecha_sk_temp1+=gf.G.nodes[nodo]["v"]*10

costo_variable_cosecha_tr_temp1 = 0
for nodo in set_nodos_tr_1-set_faenas_tr_1-set_nodos_sk_1-set_faenas_sk_1:
    costo_variable_cosecha_tr_temp1+=gf.G.nodes[nodo]["v"]*16
for nodo in set_faenas_tr_1:
    costo_variable_cosecha_tr_temp1+=gf.G.nodes[nodo]["v"]*16
#######################################################
###########----- SEGUNDA TEMPORADA-----################
#######################################################

'''Ahora empezamos a ver la TEMPORADA DOS, 
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
16 18 8 6 2 12 5 10 17 13 3 1 15 4 7 9 11 14 19 
'''
Orden= list(gf.G.nodes())
for nodo in nodos_a_cosechar_sk:
    gf.node_colors_rod[Orden.index(nodo)] = "white"
for nodo in nodos_a_cosechar_t:
    gf.node_colors_rod[Orden.index(nodo)] = "white"
for nodo in bases_faena_s + bases_faena_t:
    gf.node_colors_rod[Orden.index(nodo)] = "white"

nx.draw(gf.G, gf.pos, with_labels=True, 
        edge_color= None,#gf.edge_colors,
         node_color=gf.node_colors_rod, 
         #edgecolors= gf.nodo_bordes_faen, 
         linewidths= 1.5,node_size=150, font_weight='bold', font_size=5)
nx.draw_networkx_edges(
    gf.G,
    gf.pos,
    edgelist=ruta_arcos,
    edge_color="orange",    # o el color que desees
    width=10             # más grueso para que destaque
)
#plt.show()
'''Por lo tanto pondremos 6 skidders y 2 torre
skidders: 160, 194, 118, 92, 18, 90
torres: 52, 66
Por otro lado los nodos que estén en los rodales:
12, 9, 17,  7, 2, 4, 15 no serán cosechados
'''
bases_faena_s_t2 = [160, 194, 118, 92, 18, 90]#se ingresa a mano
bases_faena_t_t2 = [52, 66]#se ingresa a mano
nodos_a_cosechar_sk_t2 = []

'''SKIDDER: Vemos los nodos que serán cosechados'''
for base in bases_faena_s_t2:
    for hect in dt.R_jk[(base, "skidder")]["radio"]:
        nodos_a_cosechar_sk_t2.append(hect)
'''TORRE: Vemos los nodos que serán cosechados'''
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
  en la segunda temporada los siguientes
    rodales: 16 18 8 6 2 12 5 10 1 19
por lo tanto no cosecho las hectáreas que pertenecen a los rodales
17 13 3 15 4 7 9 11 14 a pesar de que sí están en el radio'''
rodal_excluido_t2 = {17, 13, 11, 15, 9, 14, 4, 7, 3} #se ingresa a mano
nodos_a_cosechar_sk_t2 = [
    nodo for nodo in nodos_a_cosechar_sk_t2
    if gf.G.nodes[nodo]["r"] not in rodal_excluido_t2
]#quitamos los nodos de skidder que están en rodales con restricción

nodos_a_cosechar_t_t2 = [
    nodo for nodo in nodos_a_cosechar_t_t2
    if gf.G.nodes[nodo]["r"] not in rodal_excluido_t2
]#quitamos los nodos de torre que están en rodales con restricción

###GRAFICAMOS
#print(nodos_a_cosechar_t)'''
node_colors_rod_t2 = ["white"] * len(gf.G.nodes())
Orden= list(gf.G.nodes())
for nodo in nodos_a_cosechar_sk_t2:
    node_colors_rod_t2[Orden.index(nodo)] = "deeppink"
for nodo in nodos_a_cosechar_t_t2:
    node_colors_rod_t2[Orden.index(nodo)] = "red"
for nodo in bases_faena_s_t2 + bases_faena_t_t2:
    node_colors_rod_t2[Orden.index(nodo)] = "blue"

node_colors_rod_t2[gf.Posicion169] = "yellow"
node_colors_rod_t2[gf.Posicion147] = "yellow"

# Dibujar nodos y aristas
nx.draw(gf.G, gf.pos, with_labels=True, 
        edge_color=None,#gf.edge_colors,
         node_color=node_colors_rod_t2, 
         #edgecolors= gf.nodo_bordes_faen, 
         linewidths= 1.5,node_size=150, font_weight='bold', font_size=5)
gf.plt.title("Grafo asignación cosecha segunda temporada")
#plt.show()

'''Calculo de volumenes y costos de segunda temporada'''
#sumar cantidad de madera en nodos a cosechar por faena
#SKIDDER:
costo_instalacion_faenas_t2 = 0
base_cant_madera_s_t2 = {}# diccionario: (id_base: suma v de radio operante)
for base in bases_faena_s_t2:
    costo_instalacion_faenas_t2 += gf.G.nodes[base]["cf"]
    suma_madera_t2 = gf.G.nodes[base]["v"]
    for nodo in gf.G.nodes[base]["R_jk"]:
        if gf.G.nodes[nodo]["r"] not in rodal_excluido_t2:
            suma_madera_t2 += gf.G.nodes[nodo]["v"]
            base_cant_madera_s_t2[base] = suma_madera_t2
        else:
            base_cant_madera_s_t2[base] = suma_madera_t2

#TORRE
base_cant_madera_t_t2 = {}# diccionario: (id_base: suma v de radio operante)
for base in bases_faena_t_t2:
    costo_instalacion_faenas_t2 += gf.G.nodes[base]["cf"]
    suma_madera_t2 = gf.G.nodes[base]["v"]
    for nodo in gf.G.nodes[base]["R_jk"]:
        if gf.G.nodes[nodo]["r"] not in rodal_excluido_t2:
            suma_madera_t2 += gf.G.nodes[nodo]["v"]
            base_cant_madera_t_t2[base] = suma_madera_t2
        else:
            base_cant_madera_t_t2[base] = suma_madera_t2
#print(base_cant_madera_t, base_cant_madera_s)

total_volumen_cosechado_t2 = 0
for base in base_cant_madera_t_t2:
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
'''En las 8 faenas instaladas se cosechó todo por lo tanto
 procedamos a los cálculos de cosecha'''


'''COSTO VARIABLE DE COSECHA TORRE'''
costo_var_cosecha_t_t2 = 0
for base in base_cant_madera_t_t2:
    costo_var_cosecha_t_t2 += gf.G.nodes[base]["cv_rad"]*base_cant_madera_t_t2[base]

'''COSTO VARIABLE DE COSECHA SKIDER'''
costo_var_cosecha_s_t2 = 0
for base in base_cant_madera_s_t2:
    #vol_base_t2 = gf.G.nodes[base]["v"]
    costo_var_cosecha_s_t2 += gf.G.nodes[base]["cv_rad"]*base_cant_madera_s_t2[base]

#for base in base_cant_madera_s:
#    vol_base = gf.G.nodes[base]["v"]
#    costo_var_cosecha_s +=  gf.G.nodes[base]["cv_rad"]*base_cant_madera_s[base]

#resultado asignación aún sin caminos
utilidad_neta_asignacion_t2 = total_volumen_cosechado_t2 * dt.P - costo_instalacion_faenas_t2 - costo_var_cosecha_s_t2 - costo_var_cosecha_t_t2


'''vemos los caminos de la segunda temporada'''
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
'''eliminamos y agregamos los arcos que son innecesarios porque ya estaban la primera temporada'''
ruta_arcos_t2.update({(41, 42), (96, 93), (92, 95), (129, 130), (160, 164), (110, 115)})
elementos_a_eliminar = {(160,161), (161,165), (165,168), (39,42), 
                        (110, 170), (170, 163), (163, 164), (108, 104), 
                        (104, 108), (100, 104), (41, 44), (44, 45), (45, 89),
                        (89, 90), (96, 97), (97, 98), (62, 66), (129, 133), 
                        (133, 137), (137, 140), (140, 143), (92, 140), (143, 146), 
                        (98, 146), (146, 147), (160, 164), (164, 167), (167, 168), (168, 169)}

ruta_arcos_t2.difference_update(elementos_a_eliminar)

#print(ruta_arcos_t2)
#print(ruta_arcos)
'''Calculamos costos construcción caminos en temporada 2'''
costo_construccion_t2 = 0
for camino in ruta_arcos_t2:
    costo_construccion_t2 += dt.C
costo_transporte_t2 = dt.ct * total_volumen_cosechado_t2 #esto es una simplificación del cálculo, queda un costo más alto del real

Utilidad_segunda_temporada = utilidad_neta_asignacion_t2 - costo_construccion_t2 - costo_transporte_t2

# 3. Dibujar encima esos arcos con mayor grosor y color llamativo
nx.draw_networkx_edges(
    gf.G,
    gf.pos,
    edgelist=ruta_arcos_t2,
    edge_color="black",    # o el color que desees
    width=10             # más grueso para que destaque
)

nx.draw_networkx_edges(
    gf.G,
    gf.pos,
    edgelist=[(100, 104), (104, 108), (108, 109), (62, 66), (39, 42)],
    edge_color="white",    # o el color que desees
    width=10             # más grueso para que destaque
)

# 4. Mostrar el plot
plt.title("Ruta más corta sobre grafo original")
plt.show()
plt.show()
'''print(f"arcos que construye la primera temporada: {ruta_arcos}")
print(f"arcos que construye la segunda temporada: {ruta_arcos_t2}")
print(f"faenas skideer instaladas la primera temporada: {bases_faena_s}")
print(f"faenas torre instaladas la primera temporada: {bases_faena_t}")
print(f"faenas skideer instaladas la segunda temporada: {bases_faena_s_t2}")
print(f"faenas torre instaladas la segunda temporada: {bases_faena_t_t2}")
print(f"nodos cosechados primera temporada por bases skidder: {nodos_a_cosechar_sk} en todos ellos se cosechó toda la madera")
print(f"nodos cosechados primera temporada por bases torre: {nodos_a_cosechar_t} en todos ellos se cosechó toda la madera")
print(f"nodos cosechados segunda temporada por bases skidder: {nodos_a_cosechar_sk_t2} en todos ellos se cosechó toda la madera")
print(f"nodos cosechados segunda temporada por bases torre: {nodos_a_cosechar_t_t2} en todos ellos se cosechó toda la madera")
print(f"total de madera cosechada {total_volumen_cosechado_t2 + total_volumen_cosechado}")
print(f"Costos totales: {costo_construccion+costo_construccion_t2+costo_instalacion_faenas+costo_instalacion_faenas_t2+costo_transporte+costo_transporte_t2+costo_var_cosecha_s+costo_var_cosecha_t+costo_var_cosecha_t_t2+costo_var_cosecha_s_t2}")'''



##############################################################
#################calculos ajustados###########################
##############################################################
print("##############################################################")
print("#################calculos ajustados###########################")
print("##############################################################")

cantidad_cosechada_temporada_2=0
setcosechadostemp2=set(nodos_a_cosechar_sk_t2+nodos_a_cosechar_t_t2+bases_faena_s_t2+bases_faena_t_t2)
for nodo in setcosechadostemp2-setcosechadostemp1:
    cantidad_cosechada_temporada_2+=gf.G.nodes[nodo]["v"]

set_nodos_sk_2=set(nodos_a_cosechar_sk_t2)-setcosechadostemp1
set_nodos_tr_2 =set(nodos_a_cosechar_t_t2)-setcosechadostemp1
set_faenas_sk_2=set(bases_faena_s_t2)-setcosechadostemp1
set_faenas_tr_2=set(bases_faena_t_t2)-setcosechadostemp1

costo_variable_cosecha_sk_temp2 = 0
for nodo in set_nodos_sk_2-set_faenas_sk_2:
    costo_variable_cosecha_sk_temp2+=gf.G.nodes[nodo]["v"]*14
for nodo in set_faenas_sk_2:
    costo_variable_cosecha_sk_temp2+=gf.G.nodes[nodo]["v"]*10

costo_variable_cosecha_tr_temp2 = 0
for nodo in set_nodos_tr_2-set_faenas_tr_2-set_nodos_sk_2-set_faenas_sk_2:
    costo_variable_cosecha_tr_temp2+=gf.G.nodes[nodo]["v"]*16
for nodo in set_faenas_tr_2:
    costo_variable_cosecha_tr_temp2+=gf.G.nodes[nodo]["v"]*16



print("#########################################################")
print("################# Temporada 1 ###########################")
print("#########################################################")

print(F"CANTIDAD COSECHADA EN TEMP 1 FUE {cantidad_cosechada_temporada_1}")
print(f"El COSTO de INSTALACIÓN de faenas TEMP 1 {costo_instalacion_faenas}")
print(f"COSTO VARIABLE COSECHA TEMP 1{costo_variable_cosecha_sk_temp1+costo_variable_cosecha_tr_temp1}")
print(f"COSTO CONSTRUCCIÓN de CAMINOS TEMP 1: {costo_construccion}")
print(f"COSTO de TRANSPORTE sobrevalorado TEMP 1: {costo_transporte}")
Utilidad_primera_temporada= cantidad_cosechada_temporada_1*dt.P-costo_instalacion_faenas-(costo_variable_cosecha_sk_temp1+costo_variable_cosecha_tr_temp1)-costo_construccion-costo_transporte
print(f"UTILIDAD temporada 1: {Utilidad_primera_temporada}")

print("#########################################################")
print("################# Temporada 2 ###########################")
print("#########################################################")
print(F"CANTIDAD COSECHADA EN TEMP 2 FUE {cantidad_cosechada_temporada_2}")
print(f"El COSTO de INSTALACIÓN de faenas TEMP 2 {costo_instalacion_faenas_t2}")
print(f"COSTO VARIABLE COSECHA TEMP 2{costo_variable_cosecha_sk_temp2+costo_variable_cosecha_tr_temp2}")
print(f"COSTO CONSTRUCCIÓN de CAMINOS TEMP 2: {costo_construccion_t2}")
print(f"COSTO de TRANSPORTE sobrevalorado TEMP 2: {costo_transporte_t2}")
Utilidad_segunda_temporada= cantidad_cosechada_temporada_2*dt.P-costo_instalacion_faenas_t2-(costo_variable_cosecha_sk_temp2+costo_variable_cosecha_tr_temp2)-costo_construccion_t2-costo_transporte_t2
print(f"UTILIDAD temporada 1: {Utilidad_segunda_temporada}")



print("#########################################################")
print("################# TOTALES ###########################")
print("#########################################################")

print(f"CANTIDAD TOTAL COSECHADA: {cantidad_cosechada_temporada_1+cantidad_cosechada_temporada_2}")
print(f"UTILIDAD TOTAL: {Utilidad_primera_temporada+Utilidad_segunda_temporada}")
print(f"El costo de instalación de faenas en ambas fue de {costo_instalacion_faenas+costo_instalacion_faenas_t2}")
print(f"El costo variable de cosecha en ambas fue de {costo_variable_cosecha_sk_temp1+costo_variable_cosecha_tr_temp1+costo_variable_cosecha_sk_temp2+costo_variable_cosecha_tr_temp2}")
print(f"El costo de construcción de caminos en ambas fue de {costo_construccion+costo_construccion_t2}")
print(f"El costo de transporte en ambas de madera fue de {costo_transporte+costo_transporte_t2}")


node_colors_blanco = ["white"] * len(gf.G.nodes())
#print(nodos_a_cosechar_t)
Orden= list(gf.G.nodes())
for nodo in setcosechadostemp1|setcosechadostemp2:
    node_colors_blanco[Orden.index(nodo)] = "blue"


# Dibujar nodos y aristas
nx.draw(gf.G, gf.pos, with_labels=True, 
        #edge_color=gf.edge_colors,
         node_color=node_colors_blanco, 
         #edgecolors= gf.nodo_bordes_faen, 
         linewidths= 1.5,node_size=150, font_weight='bold', font_size=5)
gf.plt.title("Grafo asignación ambas temporadas")
plt.show()
