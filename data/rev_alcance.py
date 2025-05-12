import grafos as gf
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import datos as dt
node_colors_gris = ["grey"] * len(gf.G.nodes())
nodes_list = list(gf.G.nodes())
for i, lista in dt.R_jk.items():
    node_colors_t = node_colors_gris.copy()
    idx = nodes_list.index(i)
    node_colors_t[idx] = "red"
    for j in lista:
        idx = nodes_list.index(j)
        node_colors_t[idx] = "red"
    gf.nx.draw(
        gf.G, gf.pos,
        with_labels=True,
        node_color=node_colors_t,
        edge_color=gf.edge_colors,
        edgecolors= gf.nodo_bordes_faen,
        linewidths= 1.5,
        node_size=150,
        font_size=5
    )
    plt.title(f"Grafo de faenas y cosechas en t={i}")
    plt.axis('off')
    plt.show()