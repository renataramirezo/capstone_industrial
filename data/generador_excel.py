import pickle
import pandas as pd
import os

# === ARCHIVOS ===
ARCHIVO_PKL = 'resultados_modelo_simple_completo.pkl'
ARCHIVO_EXCEL = 'entregable_cliente.xlsx'

# === FUNCIONES ===
def cargar_resultados(archivo_pkl=ARCHIVO_PKL):
    with open(archivo_pkl, 'rb') as archivo:
        return pickle.load(archivo)

def exportar_variables_con_resumen(variables, resultados, archivo_excel=ARCHIVO_EXCEL):
    # --- Hoja 1: Resumen ---
    resumen_data = {
        'concepto': [
            'valor_objetivo',
            'ingresos',
            'costos_cosecha',
            'costos_instalacion',
            'costos_transporte',
            'costos_construccion'
        ],
        'valor': [
            resultados.get('valor_objetivo', 0),
            resultados.get('ingresos', 0),
            resultados.get('costos', {}).get('cosecha', 0),
            resultados.get('costos', {}).get('instalacion', 0),
            resultados.get('costos', {}).get('transporte', 0),
            resultados.get('costos', {}).get('construccion_caminos', 0),
        ]
    }
    df_resumen = pd.DataFrame(resumen_data)

    # --- Hoja 2: mu ---
    mu = variables.get('mu', {})
    filas_mu = [{'nodo': i, 'maquina': k, 'periodo': t, 'valor': valor}
                for (i, k, t), valor in mu.items() if valor == 1]
    df_mu = pd.DataFrame(filas_mu)

    # --- Hoja 3: w ---
    w = variables.get('w', {})
    filas_w = [{
        'faena': i,
        'hectarea': j,
        'maquina': k,
        'periodo': t,
        'temporada': 1 if t <= 6 else 2,
        'valor': valor
    } for (i, j, k, t), valor in w.items() if valor > 0]
    df_w = pd.DataFrame(filas_w)

    # --- Hoja 4: y ---
    y = variables.get('y', {})
    filas_y = [{'origen': i, 'destino': j, 'periodo': t, 'valor': valor}
               for (i, j, t), valor in y.items() if valor == 1]
    df_y = pd.DataFrame(filas_y)

    # --- Hoja 5: z ---
    z = variables.get('z', {})
    filas_z = [{
        'origen': i,
        'destino': j,
        'periodo': t,
        'temporada': 1 if t <= 6 else 2,
        'valor': valor
    } for (i, j, t), valor in z.items() if valor > 0]
    df_z = pd.DataFrame(filas_z)

    # Guardar todo en Excel
    with pd.ExcelWriter(archivo_excel, mode='w') as writer:
        df_resumen.to_excel(writer, sheet_name='Resumen', index=False)
        df_mu.to_excel(writer, sheet_name='mu', index=False)
        df_w.to_excel(writer, sheet_name='w', index=False)
        df_y.to_excel(writer, sheet_name='y', index=False)
        df_z.to_excel(writer, sheet_name='z', index=False)

    print(f"Archivo '{archivo_excel}' guardado con:")
    print(f" - Hoja 'Resumen': {len(df_resumen)} conceptos")
    print(f" - mu: {len(df_mu)} filas")
    print(f" - w : {len(df_w)} filas")
    print(f" - y : {len(df_y)} filas")
    print(f" - z : {len(df_z)} filas")

# ----------- EJECUCIÓN -----------

if __name__ == "__main__":
    resultados = cargar_resultados()
    variables = resultados['variables']
    exportar_variables_con_resumen(variables, resultados)
