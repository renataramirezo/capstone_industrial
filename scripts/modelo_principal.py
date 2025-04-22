# /scripts/modelo_principal.py

import gurobipy as gp
from gurobipy import GRB
from data.datos import N, A, K, T, D, P, rodales

def main():
    try:
        modelo = gp.Model("Cosecha_Forestal")

        # Variables: mu[j, k, t] = 1 si se instala maquinaria k en hectárea j en mes t
        mu = modelo.addVars(N, K, T, vtype=GRB.BINARY, name="mu")

        # Restricción: No más de una faena instalada por hectárea en cada mes
        for j in N:
            for t in T:
                modelo.addConstr(
                    gp.quicksum(mu[j, k, t] for k in K) <= 1,
                    name=f"una_faena_por_hectarea_{j}_{t}"
                )

        # Función objetivo simplificada: sumar ingresos por τdt (a definir luego)
        modelo.setObjective(
            gp.quicksum(P * 1 for _ in D for _ in T),  # reemplazar por sum(P * tau_dt)
            GRB.MAXIMIZE
        )

        modelo.optimize()

        # Guardar resultados
        if modelo.status == GRB.OPTIMAL:
            with open("results/soluciones/solucion.txt", "w") as f:
                for v in modelo.getVars():
                    if v.X > 0.5:
                        f.write(f"{v.VarName}: {v.X}\n")
            print("Optimización completada y resultados guardados.")
        else:
            print("No se encontró solución óptima.")

    except Exception as e:
        print(f"Error durante la ejecución del modelo: {str(e)}")

if __name__ == "__main__":
    main()
