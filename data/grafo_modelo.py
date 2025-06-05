import grafos as gf
import pickle
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import datos as dt
import os

def dibujar_grafo_por_temporada(archivo_pkl, carpeta_salida):
    """
        Dibuja y guarda 3 gráficos de un grafo con base en los resultados
        de un modelo guardado en un archivo .pkl

        Parámetros:
            archivo_pkl (str): Ruta al archivo .pkl con los resultados del modelo.
            carpeta_salida (str): Carpeta donde se guardarán los gráficos.
    """
    edge_colors = [
        "white" for u, v in gf.G.edges()]

    with open(archivo_pkl, 'rb') as f:
        resultados = pickle.load(f)
    #import modelo_cb_separado as mdc
    f = resultados['variables']['mu']#f cambió por mu
    x = resultados['variables']['x']
    l = resultados['variables']['y']#l cambió por y
    '''#for g in l:
    for t in [1,2]:
        for (i,j) in gf.G.edges():
        
            print(f"la variable y({i},{j}),{t} tomó valor: {l.get((i, j, t), 0)}")'''
            
        
    T1=[1] #[1,2,3,4,5,6]
    T2=[2]#[13,14,15,16,17,18]
    T1x= [1, 2, 3, 4, 5, 6]
    T2x=[13,14,15,16,17,18]
    # Por ejemplo, iterar para imprimir solo las aristas activadas en t=0:
    node_colors_gris = ["white"] * len(gf.G.nodes()) #pintamos todos los nodos blancos
    nodes_list = list(gf.G.nodes())
    node_colors_t_1 = node_colors_gris.copy() #hacemos copia de nuestros nodos blancos para reutilizar
    
    for t in T1:#en la temporada 1
        # --- Colorear nodos
        for i in gf.G.nodes(): #iteramos por cada nodo
            es_faena = any(f.get((i, k, t), 0) > 0.5 for k in dt.K) #revisamo si el nodo es faena
            for tx in T1x: #para cada mes de la temporada 1 revisamos si un nodo es cosechado
                es_cosechado = any(x.get((i_, i, k, tx), 0) > 0.5 for i_ in gf.G.nodes() for k in dt.K) 
                if es_cosechado:
                    idx = nodes_list.index(i)
                    node_colors_t_1[idx] = "blue"
            
            if es_faena:
                idx = nodes_list.index(i)
                node_colors_t_1[idx] = "red"
                # nodo con faena
        #revisamos en esa temporada qué caminos se construyeron    
    edges_activados = [(i, j) for (i, j) in gf.G.edges() if l.get((i, j, 1), 0) > 0.5]

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
    #edges_activados = [(i, j) for (i, j) in gf.G.edges() if l.get((i, j, t), 0) > 0.5]
    gf.nx.draw_networkx_edges(
        gf.G, gf.pos,
        edgelist=edges_activados,
        edge_color='orange',
        width=3.5
    )


    plt.title(f"Grafo de faenas y caminos presentes en temporada 1")
    plt.axis('off')
    output_path = os.path.join("data",carpeta_salida, f"grafo_resultado_modelo_en Temp 1.png")
    plt.savefig(output_path, format="png", dpi=300, bbox_inches="tight")
    plt.close() 
    plt.show()

    node_colors_t_2=node_colors_gris.copy()

    for t in T2:
        # --- Colorear nodos
        for i in gf.G.nodes():
            es_faena = any(f.get((i, k, t), 0) > 0.5 for k in dt.K)
            #son_cosechados =[]
            for tx in T2x:
                es_cosechado = any(x.get((i_, i, k, tx), 0) > 0.5 for i_ in gf.G.nodes() for k in dt.K)
                if es_cosechado:
                    idx = nodes_list.index(i)
                    node_colors_t_2[idx] = "blue"
            if es_faena:
                idx = nodes_list.index(i)
                node_colors_t_2[idx] = "red"
                # nodo con faena
            
                #node_colors.append('blue')   # nodo cosechado
    edges_activados = [(i, j) for (i, j) in gf.G.edges() if l.get((i, j, 2), 0) > 0.5]

        # --- Dibujar grafo base
    gf.nx.draw(
        gf.G, gf.pos,
        with_labels=True,
        node_color=node_colors_t_2,
        edge_color=edge_colors,
        #edgecolors= gf.nodo_bordes_faen,
        linewidths= 1.5,
        node_size=150,
        font_size=5
    )
        # --- Colorear caminos construidos
    #edges_activados = [(i, j) for (i, j) in gf.G.edges() if l.get((i, j, 2), 0) > 0.5]
    gf.nx.draw_networkx_edges(
        gf.G, gf.pos,
        edgelist=edges_activados,
        edge_color='orange',
        width=3.5
    )

    
    plt.title(f"Grafo de faenas y caminos presentes en temporada 2")
    plt.axis('off')
    output_path = os.path.join("data",carpeta_salida, f"grafo_resultado_modelo_en Temp 2.png")
    plt.savefig(output_path, format="png", dpi=300, bbox_inches="tight")
    plt.close() 
    plt.show()

    ### ambas temporadas
    node_colors_t_t=node_colors_gris.copy()
    for t in T1+T2:
        # --- Colorear nodos
        for i in gf.G.nodes():
            es_faena = any(f.get((i, k, t), 0) > 0.5 for k in dt.K)
            for tx in T1x+T2x:
                es_cosechado = any(x.get((i_, i, k, tx), 0) > 0.5 for i_ in gf.G.nodes() for k in dt.K)
                if es_cosechado:
                    idx = nodes_list.index(i)
                    node_colors_t_t[idx] = "blue"
            if es_faena:
                idx = nodes_list.index(i)
                node_colors_t_t[idx] = "red"
                # nodo con faena
            
                #node_colors.append('blue')   # nodo cosechado
        

        # --- Dibujar grafo base
    gf.nx.draw(
        gf.G, gf.pos,
        with_labels=True,
        node_color=node_colors_t_t,
        edge_color=edge_colors,
        #edgecolors= gf.nodo_bordes_faen,
        linewidths= 1.5,
        node_size=150,
        font_size=5
    )
        # --- Colorear caminos construidos
    edges_activados = [(i, j) for (i, j) in gf.G.edges() if l.get((i, j, 1), 0) > 0.5]
    gf.nx.draw_networkx_edges(
        gf.G, gf.pos,
        edgelist=edges_activados,
        edge_color='orange',
        width=3.5
    )
    edges_activados2 = [(i, j) for (i, j) in gf.G.edges() if l.get((i, j, 2), 0) > 0.5]
    gf.nx.draw_networkx_edges(
        gf.G, gf.pos,
        edgelist=edges_activados2,
        edge_color='orange',
        width=3.5
    )

    
    plt.title(f"Grafo resumen de faenas y caminos en ambas temporadas")
    plt.axis('off')
    output_path = os.path.join("data",carpeta_salida, f"grafo_resumen_ambas_temporadas.png")
    plt.savefig(output_path, format="png", dpi=300, bbox_inches="tight")
    plt.close() 
    plt.show()
    print("tus archivos por temporada ya están listos en la carpeta de salida")

def dibujar_grafo_por_cada_t(archivo_pkl, carpeta_salida):
    """
        Dibuja y guarda 3 gráficos de un grafo con base en los resultados
        de un modelo guardado en un archivo .pkl

        Parámetros:
            archivo_pkl (str): Ruta al archivo .pkl con los resultados del modelo.
            carpeta_salida (str): Carpeta donde se guardarán los gráficos.
            """
    edge_colors = [
        "white" for u, v in gf.G.edges()]

    with open(archivo_pkl, 'rb') as f:
        resultados = pickle.load(f)
    #import modelo_cb_separado as mdc
    f = resultados['variables']['mu']#f cambió por mu
    x = resultados['variables']['x']
    l = resultados['variables']['y']#l cambió por y
    T=[1, 2]#[1,2,3,4,5,6,13,14,15,16,17,18]
    #Tx =[1,2,3,4,5,6,13,14,15,16,17,18]
    T1x= [1, 2, 3, 4, 5, 6]
    T2x=[13,14,15,16,17,18]
    # Por ejemplo, iterar para imprimir solo las aristas activadas en t=0:
    node_colors_gris = ["white"] * len(gf.G.nodes())
    nodes_list = list(gf.G.nodes())
    for t in T:
        node_colors_t = node_colors_gris.copy()
        #plt.figure(figsize=(6, 6))
        #pos = nx.spring_layout(G, seed=42)

        # --- Colorear nodos
        
        for i in gf.G.nodes():
            es_faena = any(f.get((i, k, t), 0) > 0.5 for k in dt.K)
            if t ==1:
                for tx in T1x:
                    es_cosechado = any(x.get((i_, i, k, tx), 0) > 0.5 for i_ in gf.G.nodes() for k in dt.K)
                    if es_cosechado:
                        idx = nodes_list.index(i)
                        node_colors_t[idx] = "blue"
            else:
                for tx in T2x:
                    es_cosechado = any(x.get((i_, i, k, tx), 0) > 0.5 for i_ in gf.G.nodes() for k in dt.K)
                    if es_cosechado:
                        idx = nodes_list.index(i)
                        node_colors_t[idx] = "blue"    
                #node_colors.append('blue')   # nodo cosechado
            if es_faena:
                idx = nodes_list.index(i)
                node_colors_t[idx] = "red"
                # nodo con faena
            
        edges_activados = [(i, j) for (i, j) in gf.G.edges() if l.get((i, j, t), 0) > 0.5]    
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
        #edges_activados = [(i, j) for (i, j) in gf.G.edges() if l.get((i, j, t), 0) > 0.5]
        gf.nx.draw_networkx_edges(
            gf.G, gf.pos,
            edgelist=edges_activados,
            edge_color='orange',
            width=3.5
        )

        # --- (Opcional) Dibujar flechas de faena a hectáreas cosechadas
        for (i, j, k_, t_), val in x.items():
            if t_ <= 6 and t == 1 and val > 0.5 and i in gf.G.nodes() and j in gf.G.nodes():#antes t_==t
                gf.nx.draw_networkx_edges(
                    gf.G, gf.pos,
                    edgelist=[(i, j)],
                    edge_color='blue',
                    width=1.5,
                    arrowstyle='->',
                    arrowsize=12,
                    connectionstyle="arc3,rad=0.2"
                )
            elif t_ > 6 and t == 2 and val > 0.5 and i in gf.G.nodes() and j in gf.G.nodes():#antes t_==t
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
        output_path = os.path.join("data",carpeta_salida , f"grafo_resultado_modelo_en t={t}.png")
        plt.savefig(output_path, format="png", dpi=300, bbox_inches="tight")
        plt.close() 
        plt.show()
    print("tus archivos para cada t, ya están listos en la carpeta de salida")