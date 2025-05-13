import grafos as gf
import pickle
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import datos as dt
import os

edge_colors = [
    "white" for u, v in gf.G.edges()]

with open('resultados_modelo_principal.pkl', 'rb') as f:
    resultados = pickle.load(f)
#import modelo_cb_separado as mdc
f = resultados['variables']['f']
x = resultados['variables']['x']
l = resultados['variables']['l']
T=[1,2,3,4,5,6,13,14,15,16,17,18]
T1=[1,2,3,4,5,6]
T2=[13,14,15,16,17,18]
# Por ejemplo, iterar para imprimir solo las aristas activadas en t=0:
node_colors_gris = ["white"] * len(gf.G.nodes())
nodes_list = list(gf.G.nodes())
node_colors_t_1 = node_colors_gris.copy()
'''for t in T1:
    # --- Colorear nodos
    for i in gf.G.nodes():
        es_faena = any(f.get((i, k, t), 0) > 0.5 for k in dt.K)
        es_cosechado = any(x.get((i_, i, k, t), 0) > 0.5 for i_ in gf.G.nodes() for k in dt.K)
        
        if es_faena:
            idx = nodes_list.index(i)
            node_colors_t_1[idx] = "red"
              # nodo con faena
        elif es_cosechado:
            idx = nodes_list.index(i)
            node_colors_t_1[idx] = "blue"
            #node_colors.append('blue')   # nodo cosechado
      

    # --- Dibujar grafo base
gf.nx.draw(
    gf.G, gf.pos,
    with_labels=True,
    node_color=node_colors_t_1,
    edge_color=edge_colors,
    #edgecolors= gf.nodo_bordes_faen,
    linewidths= 1.5,
    node_size=150,
    font_size=5
)
    # --- Colorear caminos construidos
edges_activados = [(i, j) for (i, j) in gf.G.edges() if l.get((i, j, t), 0) > 0.5]
gf.nx.draw_networkx_edges(
    gf.G, gf.pos,
    edgelist=edges_activados,
    edge_color='orange',
    width=3.5
)

# --- (Opcional) Dibujar flechas de faena a hectáreas cosechadas
for (i, j, k_, t_), val in x.items():
    if t_ == t and val > 0.5 and i in gf.G.nodes() and j in gf.G.nodes():
        gf.nx.draw_networkx_edges(
            gf.G, gf.pos,
            edgelist=[(i, j)],
            edge_color='black',
            width=1.5,
            arrowstyle='->',
            arrowsize=12,
            connectionstyle="arc3,rad=0.2"
        )

plt.title(f"Grafo de faenas y caminos presentes en temporada 1")
plt.axis('off')
output_path = os.path.join("data","grafos_faenas_modelo_ppl", f"grafo_resultado_modelo_en Temp 1.png")
plt.savefig(output_path, format="png", dpi=300, bbox_inches="tight")
plt.close() 
plt.show()

node_colors_t_1=node_colors_gris.copy()

for t in T2:
    # --- Colorear nodos
    for i in gf.G.nodes():
        es_faena = any(f.get((i, k, t), 0) > 0.5 for k in dt.K)
        es_cosechado = any(x.get((i_, i, k, t), 0) > 0.5 for i_ in gf.G.nodes() for k in dt.K)
        
        if es_faena:
            idx = nodes_list.index(i)
            node_colors_t_1[idx] = "red"
              # nodo con faena
        elif es_cosechado:
            idx = nodes_list.index(i)
            node_colors_t_1[idx] = "blue"
            #node_colors.append('blue')   # nodo cosechado
      

    # --- Dibujar grafo base
gf.nx.draw(
    gf.G, gf.pos,
    with_labels=True,
    node_color=node_colors_t_1,
    edge_color=edge_colors,
    #edgecolors= gf.nodo_bordes_faen,
    linewidths= 1.5,
    node_size=150,
    font_size=5
)
    # --- Colorear caminos construidos
edges_activados = [(i, j) for (i, j) in gf.G.edges() if l.get((i, j, t), 0) > 0.5]
gf.nx.draw_networkx_edges(
    gf.G, gf.pos,
    edgelist=edges_activados,
    edge_color='orange',
    width=3.5
)

# --- (Opcional) Dibujar flechas de faena a hectáreas cosechadas
for (i, j, k_, t_), val in x.items():
    if t_ == t and val > 0.5 and i in gf.G.nodes() and j in gf.G.nodes():
        gf.nx.draw_networkx_edges(
            gf.G, gf.pos,
            edgelist=[(i, j)],
            edge_color='black',
            width=1.5,
            arrowstyle='->',
            arrowsize=12,
            connectionstyle="arc3,rad=0.2"
        )

plt.title(f"Grafo de faenas y caminos presentes en temporada 2")
plt.axis('off')
output_path = os.path.join("data","grafos_faenas_modelo_ppl", f"grafo_resultado_modelo_en Temp 2.png")
plt.savefig(output_path, format="png", dpi=300, bbox_inches="tight")
plt.close() 
plt.show()'''



for t in T:
    node_colors_t = node_colors_gris.copy()
    #plt.figure(figsize=(6, 6))
    #pos = nx.spring_layout(G, seed=42)

    # --- Colorear nodos
    
    for i in gf.G.nodes():
        es_faena = any(f.get((i, k, t), 0) > 0.5 for k in dt.K)
        es_cosechado = any(x.get((i_, i, k, t), 0) > 0.5 for i_ in gf.G.nodes() for k in dt.K)
        
        if es_faena:
            idx = nodes_list.index(i)
            node_colors_t[idx] = "red"
              # nodo con faena
        elif es_cosechado:
            idx = nodes_list.index(i)
            node_colors_t[idx] = "blue"
            #node_colors.append('blue')   # nodo cosechado
        



    # --- Dibujar grafo base
    gf.nx.draw(
        gf.G, gf.pos,
        with_labels=True,
        node_color=node_colors_t,
        edge_color=edge_colors,
        #edgecolors= gf.nodo_bordes_faen,
        linewidths= 1.5,
        node_size=150,
        font_size=5
    )
        # --- Colorear caminos construidos
    edges_activados = [(i, j) for (i, j) in gf.G.edges() if l.get((i, j, t), 0) > 0.5]
    gf.nx.draw_networkx_edges(
        gf.G, gf.pos,
        edgelist=edges_activados,
        edge_color='orange',
        width=3.5
    )

    # --- (Opcional) Dibujar flechas de faena a hectáreas cosechadas
    for (i, j, k_, t_), val in x.items():
        if t_ == t and val > 0.5 and i in gf.G.nodes() and j in gf.G.nodes():
            gf.nx.draw_networkx_edges(
                gf.G, gf.pos,
                edgelist=[(i, j)],
                edge_color='blue',
                width=1.5,
                arrowstyle='->',
                arrowsize=12,
                connectionstyle="arc3,rad=0.2"
            )

    plt.title(f"Grafo de faenas y caminos presentes en t= {t}")
    plt.axis('off')
    output_path = os.path.join("data","grafos_faenas_modelo_ppl", f"grafo_resultado_modelo_en t={t}.png")
    plt.savefig(output_path, format="png", dpi=300, bbox_inches="tight")
    plt.close() 
    plt.show()