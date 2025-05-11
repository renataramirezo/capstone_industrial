import grafos as gf
import pickle
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import datos as dt

with open('resultados_modelo.pkl', 'rb') as f:
    resultados = pickle.load(f)
#import modelo_cb_separado as mdc
f = resultados['variables']['f']
x = resultados['variables']['x']
l = resultados['variables']['l']
T=[1,2,3,4,5,6,13,14,15,16,17,18]
# Por ejemplo, iterar para imprimir solo las aristas activadas en t=0:
node_colors_gris = ["grey"] * len(gf.G.nodes())
nodes_list = list(gf.G.nodes())
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
        edge_color=gf.edge_colors,
        edgecolors= gf.nodo_bordes_faen,
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

    '''# --- (Opcional) Dibujar flechas de faena a hectáreas cosechadas
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
            )'''

    plt.title(f"Grafo de faenas y cosechas en t={t}")
    plt.axis('off')
    plt.show()
'''bases_faena_t =[66]
bases_faena_s_t1 = [16,	18,	37,	46,	66,	91,	96,	114,	115,	129,	174,	199]

bases_faena_s_t13 = [1,	34,	90,	102,131,147,149,150,162,169,200]
texto="1	2	2	15	15	16	18	18	19	19	22	22	25	25	28	28	31	31	34	34	37	37	38	38	39	39	42	42	46	46	47	47	66	67	67	68	68	85	85	86	86	86	90	91	91	92	92	93	93	96	96	99	99	100	100	101	101	102	102	114	115	115	122	122	125	125	129	129	130	130	130	131	134	134	138	138	138	139	139	140	140	141	141	141	144	144	147	147	148	148	149	150	150	154	154	159	159	162	163	163	166	166	167	167	168	168	169	169	169	171	171	172	172	172	172	174	177	177	182	182	187	187	191	191	195	195	199	200"
lista = list(map(int, texto.split()))
inicio_camino = [1,	2,	2,	15,	15,	16,	18,	18,	19,	19,	22,	22,	25,	25,	28,	28,	31,	31,	34,	34,	37,	37,	40,	40,	41,	41,	42,	42,	46,	46,	47,	47,	52,	52,	53,	53,	56,	56,	58,	59,	59,	85,	85,	86,	86,	90,	91,	92,	92,	93,	93,	96,	96,	96,	97,	97,	98,	98,	99,	99,	100, 100,	100,	101,	101,	102,	104,	104,	108,	108,	110,	111,	111,	112,	112,	112,	114,	114,	115,	115,	115,	123,	126,	126, 129,	129,	130,	130,	133,	133,	137,	137,	140,	140,	140,	143,	143,	146,	146,	146,	147,	147,	148,	148,	149,	149,	162,	166,	166,	167,	167,	167,	168,	168,	169,	169,	171,	171,	172,	172,	175,	175,	179,	180,	180,	180,	185,	185,	189,	189,	190,	190,	190,	191,	194,	194,	198,	204,	208,	208]
fin_camino = [2,	46,	1,	16,	19,	15,	22,	19,	15,	18,	18,	25,	22,	28,	25,	31,	34,	28,	31,	37,	34,	40,	41,	37,	40,	42,	41,	85,	47,	2,	99,	46,	53,	56,	52,	111,	59,	52,	59,	58,	56,	86,	42,	85,	93,	96,	92,	91,	140,86,	96,	90,	97,	93,	98,	96,	146,	97,	47,	100,	99,	101,	104,	100,	102,	101,	100,	108,	112,	104,	115,	112,	53,	111,	108,	114,	115,	112,	114,	110,	171,	126,	123,	130,	133,	130,	129,	126,	129,	137,	140,	133,	92,	137,143,	146,	140,	147,	98,	143,	146,	148,	147,	149,	208,	148,	166,	162,	169,	175,	168,	172,	167,	169,	168,	166,	172,	115,	167,	171,	167,	180,	180,	179,	185,	175,	180,	189,	185,	190,	194,	191,	189,	190,	190,	198,	194,	208,	149,	204]
aristas_seleccionadas = []
nodos_a_cosechar_s_t1 = {1,	163,	114,	171,	172,	174,	14,	16,	20,	22,	23,	25,	26,	164,	167,168,	173,	175,	176,	178,	179,	180,	181,	183,	184,	185,	189,	182,	186,	187,	199,	68,	122,	123,	71,	72,	75,	76,	80,	137,	138,	190,	191,	193,	194,	195,	197,	198,	202,	203,	207,31,	32,	34,	35,	36,	42,	43}
nodos_a_cosechar_s_t2 = {2,	46,	3,	4,	5,	6,	48,	8,	9,	10,	100,	101,150,	151,	104,	105,	106,	154,	159,	102,	152,	153,	155,	156,	157,	160,	165,	166,	169,	161,	162,	164,	167,	168,	175,	176,	177,	181,	182,	123,	124,	183,	125,	126,	127,	128,	188}
nodos_a_cosechar_t = {17,	56,	20,	21,	58,	59,	60,	23,	24,	61,	62,	63,	64,	119,	26,	27,	65,	67,	122,	29,	30,	69,	70,	71,	72,	33,	73,	74,	76,	77,	78}
for i in inicio_camino:
    for j in fin_camino:
        aristas_seleccionadas.append((i,j))
node_colors_gris = ["grey"] * len(gf.G.nodes())

Orden= list(gf.G.nodes())
for nodo in nodos_a_cosechar_s_t1:
    node_colors_gris[Orden.index(nodo)] = "deeppink"
for nodo in nodos_a_cosechar_s_t2:
    node_colors_gris[Orden.index(nodo)] = "lightblue"
for nodo in nodos_a_cosechar_t:
    node_colors_gris[Orden.index(nodo)] = "lightgreen"
for nodo in bases_faena_s_t1:
    node_colors_gris[Orden.index(nodo)] = "red"
for nodo in bases_faena_t:
    node_colors_gris[Orden.index(nodo)] = "darkgreen"
for nodo in bases_faena_s_t13:
    node_colors_gris[Orden.index(nodo)] = "orange"

node_colors_gris[gf.Posicion169] = "yellow"
node_colors_gris[gf.Posicion147] = "yellow"


    # Dibujar nodos y aristas
gf.nx.draw(gf.G, gf.pos, with_labels=True, edge_color=gf.edge_colors,
        node_color=node_colors_gris, edgecolors= gf.nodo_bordes_faen, 
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
gf.plt.title(f"grafo final")
gf.plt.show()'''