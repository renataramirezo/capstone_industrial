import grafos as gf
import modelo_cb_separado as mdc

for t in mdc.T:
    nodos_a_cosechar = mdc.sol_hectareas_cosechadas[t]
    aristas_seleccionadas = mdc.sol_aristas_seleccionadas[t]
    bases_faena =mdc.sol_bases_faenas[t]

    Orden= list(gf.G.nodes())
    for nodo in nodos_a_cosechar:
        gf.node_colors_gris[Orden.index(nodo)] = "deeppink"
    for nodo in bases_faena:
        gf.node_colors_gris[Orden.index(nodo)] = "white"

    gf.node_colors_gris[gf.Posicion169] = "yellow"
    gf.node_colors_gris[gf.Posicion147] = "yellow"


        # Dibujar nodos y aristas
    gf.nx.draw(gf.G, gf.pos, with_labels=True, edge_color=gf.edge_colors,
            node_color=gf.node_colors_gris, edgecolors= gf.nodo_bordes_faen, 
            linewidths= 1.5,node_size=150, font_weight='bold', font_size=5)
        #gf.ax2.set_title("Grafo asignación cosecha primera temporada")
        #plt.show()

            # 3. Dibujar encima esos arcos con mayor grosor y color llamativo
    gf.nx.draw_networkx_edges(
        gf.G,
        gf.pos,
        edgelist=aristas_seleccionadas,
        edge_color="black",    # o el color que desees
        width=10             # más grueso para que destaque
    )

        # 4. Mostrar el plot
    gf.plt.title(f"grafo en mes {t}")
    gf.plt.show()