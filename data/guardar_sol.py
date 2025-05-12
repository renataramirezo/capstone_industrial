from gurobipy import *

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