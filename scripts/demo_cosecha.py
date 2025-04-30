import gurobipy as gp
from gurobipy import GRB
import random

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
# for i in range(n):
    #for j in range(n):
       # if x[i, j].x > 0.5:
        #    print(f"Cosechar celda ({i},{j}) con volumen {v[i][j]}")
            

grid_7x7 = [
    [None,     None,     (0, 2),  (0, 3),  (0, 4),  None,     None],
    [None,     (1, 1),   (1, 2),  (1, 3),  (1, 4),  (1, 5),   None],
    [(2, 0),   (2, 1),   (2, 2),  (2, 3),  (2, 4),  (2, 5),   (2, 6)],
    [(3, 0),   (3, 1),   (3, 2),  (3, 3),  (3, 4),  (3, 5),   (3, 6)],
    [(4, 0),   (4, 1),   (4, 2),  (4, 3),  (4, 4),  (4, 5),   (4, 6)],
    [None,     (5, 1),   (5, 2),  (5, 3),  (5, 4),  (5, 5),   None],
    [None,     None,     (6, 2),  (6, 3),  (6, 4),  None,     None]
]

exit_nodes = [(6, 4), (2, 6)]

blocked_nodes = [(2, 1), (4, 4)]

edges_dict = {}
rows = len(grid_7x7)
cols = len(grid_7x7[0])
blocked_set = set(blocked_nodes)

directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

for i in range(rows):
    for j in range(cols):
        current = grid_7x7[i][j]
        if current is None or current in blocked_set:
            continue

        neighbors = []
        for dx, dy in directions:
            ni, nj = i + dx, j + dy
            if 0 <= ni < rows and 0 <= nj < cols:
                neighbor = grid_7x7[ni][nj]
                if neighbor is not None and neighbor not in blocked_set:
                    neighbors.append(neighbor)

        edges_dict[current] = neighbors

# print(edges_dict) 

# Fijar la semilla
random.seed(42)  # Puede ser cualquier número

# Crear el diccionario de nodos válidos con valores entre 120 y 670
wood_resources = {}

for i in range(len(grid_7x7)):
    for j in range(len(grid_7x7[i])):
        node = grid_7x7[i][j]
        if node and node not in blocked_nodes: 
            wood_resources[node] = random.randint(120, 770)

# Ver resultados
for node, value in wood_resources.items():
    print(f"Nodo {node} tiene {value} metros cúbicos de madera.")

