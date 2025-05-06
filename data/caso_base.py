import sys

import networkx as nx
import matplotlib.pyplot as plt
import grafos as gf
import datos as dt

cap_rodales = {}

for rodal in range(1, 20):
    volumen_rodal = 0
    for hect in dt.rodales[rodal]:
        volumen_rodal += dt.N[hect]["v"]
        cap_rodales[rodal] = volumen_rodal
#print(cap_rodales)
ordenado = sorted(cap_rodales.items(), key=lambda x: x[1], reverse=True)
'''dado este orden, y las restricciones de adyacencia decidimos
 instalar las faenas skider en los nodos: 37 142	180
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

#print(nodos_a_cosechar_t)'''

Orden= list(gf.G.nodes())
for nodo in nodos_a_cosechar_sk:
    gf.node_colors_rod[Orden.index(nodo)] = "deeppink"
for nodo in nodos_a_cosechar_t:
    gf.node_colors_rod[Orden.index(nodo)] = "red"
for nodo in bases_faena_s + bases_faena_t:
    gf.node_colors_rod[Orden.index(nodo)] = "white"

gf.node_colors_rod[gf.Posicion169] = "yellow"
gf.node_colors_rod[gf.Posicion147] = "yellow"


# Dibujar nodos y aristas
nx.draw(gf.G, gf.pos, with_labels=True, edge_color=gf.edge_colors,
         node_color=gf.node_colors_rod, edgecolors= gf.nodo_bordes_faen, 
         linewidths= 1,node_size=150, font_weight='bold', font_size=5)
gf.ax2.set_title("Grafo asignación cosecha primera temporada")
plt.show()