from grafo_modelo import dibujar_grafo_por_temporada
from grafo_modelo import dibujar_grafo_por_cada_t
from grafo_modelo import dibujar_grafo_por_cada_mes
'''esto dibujará el archivo pkl y guardará cada imágen 
en la carpeta de salida'''

dibujar_grafo_por_temporada(
    archivo_pkl="resultados_modelo_simple_factor1.pkl",
    carpeta_salida="grafos_faenas_modelo_ppl",
)

dibujar_grafo_por_cada_t(
    archivo_pkl="resultados_modelo_simple_factor1.pkl",
    carpeta_salida="grafos_faenas_modelo_ppl",
)

dibujar_grafo_por_cada_mes(
    archivo_pkl="resultados_modelo_simple_factor1.pkl",
    carpeta_salida="grafos_faenas_modelo"
    )
#resultados_modelo_simple_2dias
#resultados_modelo_simple_completo_dossemanas.pkl
#resultados_modelo_simple_factor1.pkl