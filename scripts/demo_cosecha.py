import gurobipy as gp
from gurobipy import GRB
import random

# === Definición de la cuadrícula y configuración inicial ===
grid_7x7 = [
    [None,     None,     (0, 2),  (0, 3),  (0, 4),  None,     None],
    [None,     (1, 1),   (1, 2),  (1, 3),  (1, 4),  (1, 5),   None],
    [(2, 0),   (2, 1),   (2, 2),  (2, 3),  (2, 4),  (2, 5),   (2, 6)],
    [(3, 0),   (3, 1),   (3, 2),  (3, 3),  (3, 4),  (3, 5),   (3, 6)],
    [(4, 0),   (4, 1),   (4, 2),  (4, 3),  (4, 4),  (4, 5),   (4, 6)],
    [None,     (5, 1),   (5, 2),  (5, 3),  (5, 4),  (5, 5),   None],
    [None,     None,     (6, 2),  (6, 3),  (6, 4),  None,     None]
]

blocked_nodes = [(2, 1), (4, 4)]  # Definir nodos bloqueados

# Crear diccionario de nodos conectados (adyacentes)
edges_dict = {}
rows, cols = len(grid_7x7), len(grid_7x7[0])
blocked_set = set(blocked_nodes)  # Convertir en conjunto para mejorar rendimiento

# Definir direcciones para los vecinos
directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

# Buscar vecinos válidos para cada nodo
for i in range(rows):
    for j in range(cols):
        current = grid_7x7[i][j]
        if current is None or current in blocked_set:
            continue  # Ignorar nodos nulos o bloqueados

        neighbors = []
        for dx, dy in directions:
            ni, nj = i + dx, j + dy
            if 0 <= ni < rows and 0 <= nj < cols:
                neighbor = grid_7x7[ni][nj]
                if neighbor is not None and neighbor not in blocked_set:
                    neighbors.append(neighbor)

        edges_dict[current] = neighbors

# === Asignar recursos de madera aleatorios ===
random.seed(42)  # Semilla para resultados reproducibles

wood_resources = {}
for i in range(len(grid_7x7)):
    for j in range(len(grid_7x7[i])):
        node = grid_7x7[i][j]
        if node and node not in blocked_nodes:
            wood_resources[node] = random.randint(120, 770)

# === Asignar costos de instalación ===
installation_costs = {}
for i in range(len(grid_7x7)):
    for j in range(len(grid_7x7[i])):
        node = grid_7x7[i][j]
        if node and node not in blocked_nodes:
            is_near_blocked = False
            for dx, dy in directions:
                ni, nj = i + dx, j + dy
                if 0 <= ni < len(grid_7x7) and 0 <= nj < len(grid_7x7[ni]):
                    neighbor = grid_7x7[ni][nj]
                    if neighbor in blocked_nodes:
                        is_near_blocked = True
                        break
            installation_costs[node] = 50 if is_near_blocked else 10

# === Asignar rodales ===
rodales = {}
for i in range(7):  # filas
    for j in range(7):  # columnas
        node = grid_7x7[i][j]
        if node is None or node in blocked_nodes:
            continue
        if i <= 2:  # Parte superior
            rodales[node] = 1 if j <= 3 else 2  # Rodal 1 o 2
        else:  # Parte inferior
            rodales[node] = 3 if j <= 3 else 4  # Rodal 3 o 4

# === Asignar tipos de máquinas ===
machine_type = {}
for node, cost in installation_costs.items():
    if cost == 50:
        machine_type[node] = 'tower'
    elif cost == 10:
        machine_type[node] = 'skidder'

# === Parámetros de máquinas y costos ===
wood_price = 35000
capacity = {'skidder': 4000, 'tower': 5500}
skidder_cost = {'up_to_100m': 10000, 'more_than_100m': 14000}
tower_cost = 16000

# === Cobertura de las máquinas (modificado para skidder con cobertura Manhattan) ===
skidder_coverage = {}  # Cobertura de skidder
tower_coverage = {}    # Cobertura de torre

# === Función para calcular vecinos en forma de diamante (distancia Manhattan) ===
def manhattan_coverage(center, max_distance, grid, blocked_set):
    rows, cols = len(grid), len(grid[0])
    coverage = []
    x0, y0 = center
    for dx in range(-max_distance, max_distance + 1):
        for dy in range(-max_distance, max_distance + 1):
            if abs(dx) + abs(dy) in range(1, max_distance + 1):  # Distancias 1 hasta max_distance
                nx, ny = x0 + dx, y0 + dy
                if 0 <= nx < rows and 0 <= ny < cols:
                    neighbor = grid[nx][ny]
                    if neighbor is not None and neighbor not in blocked_set:
                        coverage.append(neighbor)
    return coverage

# === Función para calcular cobertura agrupada por distancia Manhattan ===
def layered_manhattan_coverage(center, max_distance, grid, blocked_set):
    rows, cols = len(grid), len(grid[0])
    coverage = {d: [] for d in range(1, max_distance + 1)}
    x0, y0 = center

    for dx in range(-max_distance, max_distance + 1):
        for dy in range(-max_distance, max_distance + 1):
            d = abs(dx) + abs(dy)
            if 1 <= d <= max_distance:
                nx, ny = x0 + dx, y0 + dy
                if 0 <= nx < rows and 0 <= ny < cols:
                    neighbor = grid[nx][ny]
                    if neighbor is not None and neighbor not in blocked_set:
                        coverage[d].append(neighbor)
    return coverage

# === Cobertura con niveles de distancia para skidder y tower ===
skidder_coverage = {}
tower_coverage = {}

for node, type_machine in machine_type.items():
    if type_machine == "skidder":
        skidder_coverage[node] = layered_manhattan_coverage(node, 3, grid_7x7, blocked_set)
    elif type_machine == "tower":
        tower_coverage[node] = layered_manhattan_coverage(node, 4, grid_7x7, blocked_set)

print(tower_coverage)

# === Crear modelo de optimización ===
model = gp.Model("max_profit_month1")

# === Variables de decisión ===
x = {}  # Si el nodo es cosechado
z = {}  # Si la base está activa

# Agregar variables binarias para cada nodo (x: cosecha, z: base instalada)
for node in wood_resources:
    x[node] = model.addVar(vtype=GRB.BINARY, name=f"x_{node[0]}_{node[1]}")
for node in installation_costs:
    z[node] = model.addVar(vtype=GRB.BINARY, name=f"z_{node[0]}_{node[1]}")

model.update()

# === Función objetivo: Maximizar la utilidad ===
objective = gp.LinExpr()
for node in wood_resources:
    m3 = wood_resources[node]
    revenue = m3 * wood_price
    harvest_cost_node = 0

    for base in z:
        if machine_type.get(base) == "skidder" and node in skidder_coverage.get(base, []):
            dist = abs(node[0] - base[0]) + abs(node[1] - base[1])
            cost = skidder_cost["up_to_100m"] if dist <= 1 else skidder_cost["more_than_100m"]
            harvest_cost_node = max(harvest_cost_node, m3 * cost)
        elif machine_type.get(base) == "tower" and node in tower_coverage.get(base, []):
            harvest_cost_node = max(harvest_cost_node, m3 * tower_cost)

    net_profit = revenue - harvest_cost_node
    objective += net_profit * x[node]

model.setObjective(objective, GRB.MAXIMIZE)

# === Restricciones ===

# Restricción: cosechar solo si hay una base activa que lo cubra
for node in wood_resources:
    possible_bases = [z[base] for base in z if node in (skidder_coverage.get(base, []) + tower_coverage.get(base, []))]
    if possible_bases:
        model.addConstr(x[node] <= gp.quicksum(possible_bases), name=f"coverage_{node}")
    else:
        model.addConstr(x[node] == 0, name=f"no_coverage_{node}")

# Restricción: capacidad mensual de cada base activa
for base in z:
    covered_nodes = skidder_coverage.get(base, []) if machine_type.get(base) == "skidder" else tower_coverage.get(base, [])
    total_m3 = gp.quicksum(wood_resources[n] * x[n] for n in covered_nodes if n in x)
    model.addConstr(total_m3 <= capacity[machine_type[base]] * z[base], name=f"capacity_{base}")

# === Resolver el modelo ===
model.optimize()

# === Resultados ===
if model.status == GRB.OPTIMAL:
    print("\n=== Resultados óptimos ===")
    
    # Crear representación visual del grid
    result_grid = [[" " for _ in range(7)] for _ in range(7)]
    
    # Marcar nodos bloqueados
    for node in blocked_nodes:
        i, j = node
        result_grid[i][j] = "B"
    
    # Marcar nodos None
    for i in range(7):
        for j in range(7):
            if grid_7x7[i][j] is None:
                result_grid[i][j] = "X"
    
    # Marcar bases instaladas
    for base in z:
        if z[base].X > 0.5:
            i, j = base
            result_grid[i][j] = "T" if machine_type[base] == "tower" else "S"
    
    # Marcar nodos cosechados
    for node in x:
        if x[node].X > 0.5:
            i, j = node
            result_grid[i][j] = "C"
    
    # Imprimir el grid de resultados
    print("\nMapa de operaciones (7x7):")
    print("  " + " ".join(str(i) for i in range(7)))
    for i in range(7):
        print(f"{i} " + " ".join(result_grid[i][j] for j in range(7)))
    
    print("\nLeyenda:")
    print("X: Nodo no disponible (None)")
    print("B: Nodo bloqueado")
    print("S: Base Skidder instalada")
    print("T: Base Tower instalada")
    print("C: Nodo cosechado")
    
    # Mostrar detalles adicionales
    print("\nDetalles de operación:")
    for node in x:
        if x[node].X > 0.5:
            print(f"Nodo cosechado {node} con {wood_resources[node]} m³")

    for base in z:
        if z[base].X > 0.5:
            print(f"Base instalada {machine_type[base]} en {base}")
    
    print(f"\nUtilidad total: ${model.ObjVal:,.0f}")
else:
    print("No se encontró una solución óptima.")