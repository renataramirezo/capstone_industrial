import gurobipy as gp
from gurobipy import GRB
import random
from collections import defaultdict

# === Configuración inicial ===
grid_7x7 = [
    [None,     None,     (0, 2),  (0, 3),  (0, 4),  None,     None],
    [None,     (1, 1),   (1, 2),  (1, 3),  (1, 4),  (1, 5),   None],
    [(2, 0),   (2, 1),   (2, 2),  (2, 3),  (2, 4),  (2, 5),   (2, 6)],
    [(3, 0),   (3, 1),   (3, 2),  (3, 3),  (3, 4),  (3, 5),   (3, 6)],
    [(4, 0),   (4, 1),   (4, 2),  (4, 3),  (4, 4),  (4, 5),   (4, 6)],
    [None,     (5, 1),   (5, 2),  (5, 3),  (5, 4),  (5, 5),   None],
    [None,     None,     (6, 2),  (6, 3),  (6, 4),  None,     None]
]

blocked_nodes = [(2, 1), (4, 4)]  # Nodos bloqueados
blocked_set = set(blocked_nodes)

# === Parámetros económicos ===
P = 35000  # Precio por m3 (antes wood_price)
cf = {
    1: 10000,  # Costo instalación skidder (k=1)
    2: 50000   # Costo instalación torre (k=2)
}

# Costos variables de cosecha (cv) - ahora como diccionario de tuplas (i,j,k)
cv = {}

# Capacidades de cosecha
mcc = {
    1: 4000,  # Capacidad skidder (m3 por faena)
    2: 5500   # Capacidad torre (m3 por faena)
}

# === Generar recursos madereros ===
random.seed(42)
wood_resources = {}
for i in range(7):
    for j in range(7):
        node = grid_7x7[i][j]
        if node and node not in blocked_set:
            wood_resources[node] = random.randint(120, 770)

# === Función para calcular áreas cosechables ===
def calculate_harvest_areas(machine_type, max_distance):
    areas = {}
    for node in wood_resources:
        harvestable = set()
        x, y = node
        # Explorar todos los nodos dentro de la distancia Manhattan <= max_distance
        for i in range(7):
            for j in range(7):
                if grid_7x7[i][j] and grid_7x7[i][j] not in blocked_set:
                    if abs(i - x) + abs(j - y) <= max_distance:
                        harvestable.add(grid_7x7[i][j])
        areas[node] = harvestable
    return areas

# Áreas para cada tipo de máquina
skidder_areas = calculate_harvest_areas('skidder', 3)
tower_areas = calculate_harvest_areas('tower', 4)

# === Función para calcular costos de cosecha ===
def calculate_cv():
    cv_dict = {}
    # Costos para skidder (k=1)
    for faena in wood_resources:
        for node in skidder_areas[faena]:
            di = abs(faena[0] - node[0])
            dj = abs(faena[1] - node[1])
            distance = max(di, dj)  # Distancia de Chebyshev
            
            if distance == 0:
                cost = 10000  # same_cell
            elif distance == 1:
                cost = 10000  # adjacent
            else:
                cost = 14000  # beyond
            
            cv_dict[(faena, node, 1)] = cost
    
    # Costos para torre (k=2) - costo fijo
    for faena in wood_resources:
        for node in tower_areas[faena]:
            cv_dict[(faena, node, 2)] = 16000
    
    return cv_dict

# Calcular todos los costos variables
cv = calculate_cv()

# === Crear modelo de optimización ===
model = gp.Model("CosechaOptimaUnMes")

# === Variables de decisión ===
mu = {}  # 1 si se instala maquinaria tipo k en el nodo i (costos de instalación)
f = {}   # 1 si existe maquinaria tipo k en el nodo i (para costos de operación)
x = {}   # 1 si el nodo j es cosechado por maquinaria k instalada en el nodo i
w = {}   # Cantidad de madera cosechada en nodo j por maquinaria k instalada en i

for i in wood_resources:
    # Variables de instalación y estado para skidder (k=1)
    mu[(i, 1)] = model.addVar(vtype=GRB.BINARY, name=f"mu_skidder_{i[0]}_{i[1]}")
    f[(i, 1)] = model.addVar(vtype=GRB.BINARY, name=f"f_skidder_{i[0]}_{i[1]}")
    
    # Variables de instalación y estado para torre (k=2)
    mu[(i, 2)] = model.addVar(vtype=GRB.BINARY, name=f"mu_torre_{i[0]}_{i[1]}")
    f[(i, 2)] = model.addVar(vtype=GRB.BINARY, name=f"f_torre_{i[0]}_{i[1]}")
    
    # Variables de asignación y cosecha para nodos dentro del radio de operación
    for j in skidder_areas[i]:  # Para skidder
        x[(i, j, 1)] = model.addVar(vtype=GRB.BINARY, name=f"x_skidder_{i[0]}_{i[1]}_cosecha_{j[0]}_{j[1]}")
        w[(i, j, 1)] = model.addVar(vtype=GRB.CONTINUOUS, name=f"w_skidder_{i[0]}_{i[1]}_cosecha_{j[0]}_{j[1]}")
    
    for j in tower_areas[i]:  # Para torre
        x[(i, j, 2)] = model.addVar(vtype=GRB.BINARY, name=f"x_torre_{i[0]}_{i[1]}_cosecha_{j[0]}_{j[1]}")
        w[(i, j, 2)] = model.addVar(vtype=GRB.CONTINUOUS, name=f"w_torre_{i[0]}_{i[1]}_cosecha_{j[0]}_{j[1]}")

model.update()

# === Restricciones ===

# 1. Relación entre instalación y estado de la maquinaria
for i in wood_resources:
    for k in [1, 2]:  # 1=skidder, 2=torre
        model.addConstr(f[(i, k)] == mu[(i, k)], name=f"instalacion_estado_{i}_{k}")

# 2. Máximo una maquinaria por nodo
for i in wood_resources:
    model.addConstr(f[(i, 1)] + f[(i, 2)] <= 1, name=f"una_maquinaria_{i}")

# 3. Asignación de cosecha solo si existe la maquinaria
for i in wood_resources:
    for j in skidder_areas[i]:
        model.addConstr(x[(i, j, 1)] <= f[(i, 1)], name=f"asign_skidder_{i}_{j}")
    for j in tower_areas[i]:
        model.addConstr(x[(i, j, 2)] <= f[(i, 2)], name=f"asign_torre_{i}_{j}")

# 4. Cada nodo cosechado solo por una maquinaria
for j in wood_resources:
    # Encontrar todas las posibles faenas que pueden cosechar j
    asignaciones = []
    for i in wood_resources:
        if j in skidder_areas[i]:
            asignaciones.append((i, 1))
        if j in tower_areas[i]:
            asignaciones.append((i, 2))
    
    if asignaciones:  # Solo si hay posibles asignaciones
        model.addConstr(gp.quicksum(x[(i, j, k)] for (i, k) in asignaciones) <= 1, 
                       name=f"unica_asignacion_{j}")

# 5. Límite de volumen cosechado por nodo
for j in wood_resources:
    model.addConstr(gp.quicksum(w[(i, j, k)] for i in wood_resources for k in [1, 2] 
                   if (i, j, k) in w) <= wood_resources[j], name=f"volumen_max_{j}")

# 6. Capacidad máxima de cosecha por maquinaria
for i in wood_resources:
    # Para skidder (k=1)
    if any((i, j, 1) in w for j in skidder_areas[i]):
        model.addConstr(gp.quicksum(w[(i, j, 1)] for j in skidder_areas[i] if (i, j, 1) in w) <= mcc[1], 
                      name=f"capacidad_skidder_{i}")
    
    # Para torre (k=2)
    if any((i, j, 2) in w for j in tower_areas[i]):
        model.addConstr(gp.quicksum(w[(i, j, 2)] for j in tower_areas[i] if (i, j, 2) in w) <= mcc[2], 
                      name=f"capacidad_torre_{i}")

# === Función Objetivo ===
# Maximizar ingresos por venta menos costos de instalación y cosecha

# Ingresos (precio * volumen total cosechado)
ingresos = P * gp.quicksum(w[key] for key in w)

# Costos fijos de instalación
costos_fijos = gp.quicksum(cf[1] * mu[(i, 1)] for i in wood_resources) + \
               gp.quicksum(cf[2] * mu[(i, 2)] for i in wood_resources)

# Costos variables de cosecha (versión corregida)
costos_variables = gp.quicksum(cv[key] * w[key] for key in w if key[2] == 1) + \
                  gp.quicksum(cv[key] * w[key] for key in w if key[2] == 2)

model.setObjective(ingresos - costos_fijos - costos_variables, GRB.MAXIMIZE)

# === Optimizar ===
model.optimize()

# === Mostrar resultados ===
if model.status == GRB.OPTIMAL:
    print("\nSolución óptima encontrada")
    print(f"Valor objetivo: ${model.objVal:,.2f}")
    
    # Mostrar instalaciones
    print("\nInstalaciones de maquinaria:")
    for i in wood_resources:
        for k in [1, 2]:
            if mu[(i, k)].X > 0.5:
                tipo = "Skidder" if k == 1 else "Torre"
                print(f"{tipo} instalado en nodo {i}")
    
    # Mostrar cosechas significativas
    print("\nCosechas importantes:")
    for (i, j, k) in w:
        if w[(i, j, k)].X > 0:
            tipo = "Skidder" if k == 1 else "Torre"
            print(f"{tipo} en {i} cosechó {w[(i, j, k)].X:.2f} m3 de {j}")
else:
    print("No se encontró solución óptima")