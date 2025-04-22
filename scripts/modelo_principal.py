import gurobipy as gp
from gurobipy import GRB
from funciones_auxiliares import cargar_datos  

def main():
    # --- Cargar datos ---
    rodales, hectareas, costos = cargar_datos("data/")

    # --- Crear modelo ---
    modelo = gp.Model("Cosecha_Forestal")

    # --- Definir variables ---
    mu = {}  # Ejemplo: μ_jkt
    for j in hectareas:
        for k in ["skidder", "torre"]:
            for t in range(1, 25):  # 24 meses
                mu[j, k, t] = modelo.addVar(vtype=GRB.BINARY, name=f"mu_{j}_{k}_{t}")

    # --- Restricciones ---
    # Ejemplo: No instalar más de una faena por hectárea (Restricción 8)
    for j in hectareas:
        for t in range(1, 25):
            modelo.addConstr(
                gp.quicksum(mu[j, k, t] for k in ["skidder", "torre"]) <= 1,
                name=f"max_una_faena_{j}_{t}"
            )

    # --- Función objetivo ---
    # Ejemplo simplificado (adaptar según PDF)
    modelo.setObjective(
        gp.quicksum(P * tau_dt for d in destinos for t in meses) 
        - gp.quicksum(cif_ki * mu[j, k, t] for ...),
        sense=GRB.MAXIMIZE
    )

    # --- Optimizar ---
    modelo.optimize()

    # --- Guardar resultados ---
    if modelo.status == GRB.OPTIMAL:
        with open("results/soluciones/solucion.txt", "w") as f:
            for v in modelo.getVars():
                if v.X > 0.5:  # Para variables binarias
                    f.write(f"{v.VarName}: {v.X}\n")

if __name__ == "__main__":
    main()