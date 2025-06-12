from grafo_modelo import dibujar_grafo_por_temporada
from grafo_modelo import dibujar_grafo_por_cada_t
'''esto dibujará el archivo pkl y guardará cada imágen 
en la carpeta de salida'''

dibujar_grafo_por_temporada(
    archivo_pkl="resultados_modelo_simple_p.pkl",
    carpeta_salida="grafos_faenas_modelo_ppl",
)

dibujar_grafo_por_cada_t(
    archivo_pkl="resultados_modelo_simple_p.pkl",
    carpeta_salida="grafos_faenas_modelo_ppl",
)
