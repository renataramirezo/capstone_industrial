import gurobipy as gp
from gurobipy import GRB

n = 5  # tamaño de la grilla 5x5
capacidad_total = 500  # límite total de cosecha (ejemplo)
v = [[10, 20, 30, 40, 50],
     [15, 25, 35, 45, 55],
     [20, 30, 40, 50, 60],
     [25, 35, 45, 55, 65],
     [30, 40, 50, 60, 70]]  # volumen de madera por celda

m = gp.Model("cosecha_simplificada")

# x_ij = 1 si se cosecha la celda (i,j), 0 si no
x = m.addVars(n, n, vtype=GRB.BINARY, name="x")

# Restricción: no superar la capacidad total
m.addConstr(gp.quicksum(x[i, j] * v[i][j] for i in range(n) for j in range(n)) <= capacidad_total,
            name="CapacidadTotal")

# Función objetivo: maximizar volumen cosechado
m.setObjective(gp.quicksum(x[i, j] * v[i][j] for i in range(n) for j in range(n)), GRB.MAXIMIZE)

# Resolver
m.optimize()

# Resultados
for i in range(n):
    for j in range(n):
        if x[i, j].x > 0.5:
            print(f"Cosechar celda ({i},{j}) con volumen {v[i][j]}")
