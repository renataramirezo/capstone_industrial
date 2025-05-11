import pickle

def imprimir_resultados_desde_pkl(archivo_pkl='resultados_modelo.pkl'):
    # Cargar los resultados desde el archivo .pkl
    with open(archivo_pkl, 'rb') as f:
        resultados = pickle.load(f)
    
    # Imprimir información básica del resultado
    print("="*50)
    print(f"Estado de la solución: {resultados['status']}")
    print("="*50)
    print(f"Valor objetivo total: {resultados['valor_objetivo']:.2f}")
    print(f"Ingresos por venta: {resultados['ingresos']:.2f}")
    print("\n" + "-"*50)
    print("DETALLE DE COSTOS:")
    print("-"*50)
    
    # Imprimir cada uno de los costos
    costos = resultados['costos']
    for nombre_costo, valor in costos.items():
        print(f"{nombre_costo.replace('_', ' ').title()}: {valor:.2f}")
    
    # Calcular y mostrar el total de costos
    total_costos = sum(costos.values())
    print("-"*50)
    print(f"TOTAL COSTOS: {total_costos:.2f}")
    
    # Calcular y mostrar la utilidad (ingresos - costos)
    utilidad = resultados['ingresos'] - total_costos
    print("\n" + "="*50)
    print(f"UTILIDAD: {utilidad:.2f}")
    print("="*50)

    s_values = resultados['variables']['s']
    for (r, u), valor in s_values.items():
        print(f"s[{r}, {u}]: {valor:}")  # 4 decimales para precisión

# Llamar a la función
imprimir_resultados_desde_pkl('resultados_modelo.pkl')