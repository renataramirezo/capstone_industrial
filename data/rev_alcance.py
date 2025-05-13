import grafos as gf
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import datos as dt
import os
node_colors_gris = ["grey"] * len(gf.G.nodes())
nodes_list = list(gf.G.nodes())
for i, lista in dt.R_jk.items():
    node_colors_t = node_colors_gris.copy()
    idx = nodes_list.index(i[0])
    node_colors_t[idx] = "blue"
    for j in lista["radio"]:
        idx = nodes_list.index(j)
        node_colors_t[idx] = "red"
        if j==i[0]:
            idx = nodes_list.index(i[0])
            node_colors_t[idx] = "blue"

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
    plt.title(f"Grafo de radio rodal= {i[0]}")
    plt.axis('off')
    output_path = os.path.join("data","grafos_radios", f"grafo_radio_base_{i[0]}.png")
    plt.savefig(output_path, format="png", dpi=300, bbox_inches="tight")
    plt.close() 
    plt.show()