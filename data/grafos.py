import sys
import networkx as nx
import datos
import matplotlib.pyplot as plt
import costosymadera
# Crear un grafo vacío

G = nx.Graph()
'''Definición de los nodos
cada nodo se llama por su id y contiene los siguientes atributos:
    K= string tipo de maquinaria, 
    v = float volumen de madera disponible,
    cf = float costo fijo instalación faena
    mcc = capacidad maxima cosecha faena k
    D = bool si es nodo de salida o no
    r = int el id del rodal al que pertenece'''

for nodo_id, atributos in datos.N.items():
    G.add_node(nodo_id,**atributos)
for nodo_id in G.nodes:
    if nodo_id in datos.D:
        G.nodes[nodo_id]["D"] = True
    else:
        G.nodes[nodo_id]["D"] = False 
 #   print(nodo)
for rodal, nodos in datos.rodales.items():
    for nodo in nodos:
        G.nodes[nodo]["r"] = rodal
#print(datos.R_jk.items())
for base_faena, nodos in datos.R_jk.items():
    G.nodes[base_faena[0]]["R_jk"] = nodos["radio"]
    G.nodes[base_faena[0]]["cv_rad"] = nodos["cv_rad"]#costo variable de nodos en su radio
    G.nodes[base_faena[0]]["cv_base"] = nodos["cv_base"]#costo variable de la base


#costo variable si es base faena y si no es base faena
#añadimos los arcos
'''Definición de los arcos
cada arco se llama por el id de los nodos que une y contiene los siguientes atributos:
    C = float Costo de construcción, 
    ct = float costo de transporte de m3,
    XA = bool t si se destruye en la intertemporada f eoc
    '''
for origen, destino in datos.A:
    G.add_edge(origen,destino)
for u, v in G.edges:
    G[u][v]["C"] = 200
    G[u][v]["ct"] = 2.6 
    if (u,v) in datos.XA or (v, u) in datos.XA:
        G[u][v]["XA"] = True
    else:
        G[u][v]["XA"] = False


# Dibujar el grafo
pos = nx.get_node_attributes(G, 'pos')
#pos = nx.spring_layout(G)  # Puedes probar también nx.kamada_kawai_layout(G) o nx.planar_layout(G)
# Diccionario de colores por tipo de maquinaria
color_map = {
    "skidder": "red",
    "torre": "blue"}
# Asignar color según atributo 'K'
node_colors_faen = [color_map.get(G.nodes[n].get("K", "default"), "gray") for n in G.nodes()]


# Lista única de bosques
rodales = list(range(1, 20))  # del 1 al 19
colors = plt.cm.tab20.colors  # paleta con hasta 20 colores distintos
# Asignar un color distinto a cada bosque
rodal_color_map = {r: colors[i % len(colors)] for i, r in enumerate(rodales)}

node_colors_rod = [rodal_color_map.get(G.nodes[n].get("r"), "gray") for n in G.nodes()]

Orden= list(G.nodes())
Posicion147 = Orden.index(147)
Posicion169 = Orden.index(169)

node_colors_rod[Posicion169] = "yellow"
node_colors_rod[Posicion147] = "yellow"
node_colors_faen[Posicion147] = "yellow"
node_colors_faen[Posicion169] = "yellow"

edge_colors = [
    "red" if G.edges[u, v].get("XA") else "green"
    for u, v in G.edges()
]


fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))
# Dibujar nodos y aristas
nx.draw(G, pos, ax=ax1, with_labels=True, edge_color=edge_colors, node_color=node_colors_rod, node_size=200, font_weight='bold', font_size=8)
ax1.set_title("Grafo rodales")
# Mostrar los atributos de los arcos como etiquetas
#edge_labels = nx.get_edge_attributes(G, 'XA')
#nx.draw_networkx_edge_labels(G, pos)

#nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)


#nx.draw(G, pos, ax = ax2, with_labels=True, edge_color=edge_colors, node_color=node_colors_faen, node_size=200, font_weight='bold', font_size=8)
#ax2.set_title("Grafo faenas")
#plt.tight_layout()
#plt.show()