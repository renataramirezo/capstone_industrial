from gurobipy import *
import pickle

def guardar_solucion_inicial(resultados, archivo='solucion_inicial.sol'):
    """Guarda la solución inicial en formato .sol para Gurobi"""
    with open(archivo, 'w') as f:
        f.write('# Solution for model Asignacion_cosecha\n')
        f.write('# Objective value = {}\n'.format(resultados['valor_objetivo']))
        
        # Escribir todas las variables no cero
        for var_name, var_dict in resultados['variables'].items():
            for key, value in var_dict.items():
                if abs(value) > 1e-6:  # Solo variables no cero
                    if isinstance(key, tuple):
                        # Construir nombre de variable según convención Gurobi
                        if var_name in ['mu', 'f', 'x', 'w', 's']:
                            var_str = f"{var_name}[{','.join(map(str, key))}]"
                        elif var_name in ['y', 'l', 'z']:
                            var_str = f"{var_name}[{key[0]},{key[1]},{key[2]}]"
                        elif var_name in ['p', 'q']:
                            var_str = f"{var_name}[{key[0]},{key[1]}]"
                        f.write(f"{var_str} {value}\n")
    print(f"Solución inicial guardada en {archivo}")

def cargar_solucion_inicial(modelo: Model, archivo='solucion_inicial.sol'):
    """Carga una solución inicial desde archivo .sol"""
    try:
        modelo.read(archivo)
        print(f"Solución inicial cargada desde {archivo}")
    except Exception as e:
        print(f"No se pudo cargar solución inicial: {str(e)}")

def cargar_solucion_desde_pkl(archivo_pkl='resultados_modelo.pkl'):
    """Carga la solución desde un archivo .pkl y la prepara para Gurobi"""
    try:
        with open(archivo_pkl, 'rb') as f:
            datos = pickle.load(f)
        
        # Crear archivo .sol temporal
        archivo_sol = 'solucion_inicial.sol'
        guardar_solucion_inicial(datos, archivo_sol)
        return archivo_sol
    except Exception as e:
        print(f"Error al cargar solución inicial: {str(e)}")
        return None