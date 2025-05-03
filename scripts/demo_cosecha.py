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
wood_price = 35000  # Precio por m3
skidder_install_cost = 10000  # Costo instalación skidder
tower_install_cost = 50000    # Costo instalación torre

# Costos de cosecha diferenciados
skidder_cost = {
    'same_cell': 10000,    # Misma celda
    'adjacent': 10000,     # Arriba, abajo, izquierda, derecha (distancia 1)
    'square': 10000,       # Diagonales (distancia sqrt(2))
    'beyond': 14000        # Más allá del cuadrado 3x3
}
tower_cost = 16000  # Costo fijo por m3 para torres

# Capacidades de cosecha
skidder_capacity = 4000  # m3 por faena
tower_capacity = 5500    # m3 por faena

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
    directions = [(-1,0),(1,0),(0,-1),(0,1)]
    
    for node in wood_resources:
        queue = [(node, 0)]
        visited = set([node])
        harvestable = set()
        
        while queue:
            current, dist = queue.pop(0)
            harvestable.add(current)
            
            if dist >= max_distance:
                continue
                
            for dx, dy in directions:
                ni, nj = current[0]+dx, current[1]+dy
                if 0 <= ni <7 and 0<= nj <7:
                    neighbor = grid_7x7[ni][nj]
                    if (neighbor and neighbor not in blocked_set and 
                        neighbor not in visited):
                        visited.add(neighbor)
                        queue.append((neighbor, dist+1))
        
        areas[node] = harvestable
    return areas


# Áreas para cada tipo de máquina
skidder_areas = calculate_harvest_areas('skidder', 3)
tower_areas = calculate_harvest_areas('tower', 4)  

print(skidder_areas)

# === Función para calcular costos de cosecha por skidder ===
def calculate_skidder_cost(faena, node):
    di = abs(faena[0] - node[0])
    dj = abs(faena[1] - node[1])
    distance = max(di, dj)  # Distancia de Chebyshev (para cuadrado)
    
    if distance == 0:
        return skidder_cost['same_cell']
    elif distance == 1:
        return skidder_cost['adjacent']
    elif distance == 2:
        return skidder_cost['square']
    else:
        return skidder_cost['beyond']

# === Crear modelo de optimización ===
model = gp.Model("CosechaOptima")

# === Variables de decisión ===
z_skidder = {}  # 1 si se instala skidder en el nodo
z_tower = {}    # 1 si se instala torre en el nodo
x = {}          # 1 si el nodo es cosechado
y = {}          # Faena que cosecha el nodo (para exclusividad)

for node in wood_resources:
    z_skidder[node] = model.addVar(vtype=GRB.BINARY, name=f"skidder_{node[0]}_{node[1]}")
    z_tower[node] = model.addVar(vtype=GRB.BINARY, name=f"tower_{node[0]}_{node[1]}")
    x[node] = model.addVar(vtype=GRB.BINARY, name=f"cosecha_{node[0]}_{node[1]}")
    
    # Variable para controlar qué faena cosecha cada nodo
    possible_faenas = []
    for faena in wood_resources:
        if node in skidder_areas[faena]:
            possible_faenas.append((faena, 'skidder'))
        if node in tower_areas[faena]:
            possible_faenas.append((faena, 'tower'))
    
    y[node] = {
        (faena, tipo): model.addVar(vtype=GRB.BINARY, 
                                   name=f"asign_{node[0]}_{node[1]}_to_{faena}_{tipo}")
        for (faena, tipo) in possible_faenas
    }

model.update()

# === Restricciones ===

# 1. Cada nodo puede tener como máximo un tipo de faena
for node in wood_resources:
    model.addConstr(z_skidder[node] + z_tower[node] <= 1)

# 2. Un nodo solo puede ser cosechado si está asignado a una faena activa
for node in wood_resources:
    model.addConstr(x[node] == gp.quicksum(
        y[node].get((faena, tipo), 0)
        for faena in wood_resources
        for tipo in ['skidder', 'tower']
        if (faena, tipo) in y[node]
    ))

# 3. Solo se puede asignar a faenas instaladas
for node in wood_resources:
    for (faena, tipo), var in y[node].items():
        if tipo == 'skidder':
            model.addConstr(var <= z_skidder[faena])
        else:
            model.addConstr(var <= z_tower[faena])

# 4. Cada nodo solo puede ser cosechado por una faena
for node in wood_resources:
    model.addConstr(gp.quicksum(
        y[node].get((faena, tipo), 0)
        for faena in wood_resources
        for tipo in ['skidder', 'tower']
        if (faena, tipo) in y[node]
    ) <= 1)

# 5. Restricciones de capacidad
for faena in wood_resources:
    # Capacidad skidder
    skidder_total = gp.quicksum(
        wood_resources[node] * y[node].get((faena, 'skidder'), 0)
        for node in wood_resources
        if (faena, 'skidder') in y[node]
    )
    model.addConstr(skidder_total <= skidder_capacity * z_skidder[faena])
    
    # Capacidad torre
    tower_total = gp.quicksum(
        wood_resources[node] * y[node].get((faena, 'tower'), 0)
        for node in wood_resources
        if (faena, 'tower') in y[node]
    )
    model.addConstr(tower_total <= tower_capacity * z_tower[faena])

# === Función objetivo ===
revenue = gp.quicksum(
    wood_resources[node] * wood_price * x[node]
    for node in wood_resources
)

harvest_expenses = gp.LinExpr()
for node in wood_resources:
    for faena in wood_resources:
        # Si es skidder y cubre este nodo
        if (faena, 'skidder') in y[node]:
            cost = calculate_skidder_cost(faena, node)
            harvest_expenses += wood_resources[node] * cost * y[node][(faena, 'skidder')]
        
        # Si es torre y cubre este nodo
        if (faena, 'tower') in y[node]:
            harvest_expenses += wood_resources[node] * tower_cost * y[node][(faena, 'tower')]

installation_expenses = gp.quicksum(
    skidder_install_cost * z_skidder[node] + tower_install_cost * z_tower[node]
    for node in wood_resources
)

model.setObjective(revenue - harvest_expenses - installation_expenses, GRB.MAXIMIZE)

# === Resolver el modelo ===
model.optimize()

# === Resultados ===
if model.status == GRB.OPTIMAL:
    print("\n=== RESULTADOS ÓPTIMOS ===")
    
    # Crear grid de visualización
    visual_grid = [["·" for _ in range(7)] for _ in range(7)]
    faena_grid = [[" " for _ in range(7)] for _ in range(7)]
    
    # Marcar nodos no disponibles
    for i in range(7):
        for j in range(7):
            if grid_7x7[i][j] is None:
                visual_grid[i][j] = " "
                faena_grid[i][j] = " "
            elif (i,j) in blocked_set:
                visual_grid[i][j] = "█"
                faena_grid[i][j] = "█"
    
    # Procesar faenas instaladas
    faenas_instaladas = []
    for node in wood_resources:
        if z_skidder[node].X > 0.5:
            visual_grid[node[0]][node[1]] = "S"
            faena_grid[node[0]][node[1]] = "S"
            faenas_instaladas.append((node, 'skidder'))
        elif z_tower[node].X > 0.5:
            visual_grid[node[0]][node[1]] = "T"
            faena_grid[node[0]][node[1]] = "T"
            faenas_instaladas.append((node, 'tower'))
    
    # Procesar nodos cosechados y sus asignaciones
    asignaciones = defaultdict(list)
    costos_por_faena = defaultdict(float)
    
    for node in wood_resources:
        if x[node].X > 0.5:
            visual_grid[node[0]][node[1]] = "C"
            
            # Encontrar qué faena lo cosechó
            for (faena, tipo), var in y[node].items():
                if var.X > 0.5:
                    asignaciones[faena].append(node)
                    if tipo == 'skidder':
                        costo = calculate_skidder_cost(faena, node)
                    else:
                        costo = tower_cost
                    costos_por_faena[faena] += wood_resources[node] * costo
                    break
    
    # Imprimir mapas
    print("\nMapa de Faenas (S=Skidder, T=Torre, █=Bloqueado):")
    print("  0 1 2 3 4 5 6")
    for i in range(7):
        print(f"{i} " + " ".join(faena_grid[i]))
    
    print("\nMapa de Cosecha (C=Cosechado, S/T=Faena, █=Bloqueado):")
    print("  0 1 2 3 4 5 6")
    for i in range(7):
        print(f"{i} " + " ".join(visual_grid[i]))
    
    # Información detallada
    print("\nDetalles de operación:")
    for faena, tipo in faenas_instaladas:
        nodos_cosechados = asignaciones[faena]
        m3_total = sum(wood_resources[n] for n in nodos_cosechados)
        costo_total = costos_por_faena[faena]
        print(f"\n{tipo.upper()} en {faena}:")
        print(f"- Nodos cosechados: {len(nodos_cosechados)}")
        print(f"- Volumen total: {m3_total} m³")
        print(f"- Costo cosecha: ${costo_total:,.0f}")
        print(f"- Ingresos: ${m3_total * wood_price:,.0f}")
        
        # Detalle de costos por distancia (solo para skidders)
        if tipo == 'skidder':
            costos_por_distancia = defaultdict(list)
            for node in nodos_cosechados:
                distancia = max(abs(faena[0]-node[0]), abs(faena[1]-node[1]))
                costos_por_distancia[distancia].append(node)
            
            print("\n  Detalle por distancia:")
            for distancia, nodos in sorted(costos_por_distancia.items()):
                costo = calculate_skidder_cost(faena, nodos[0])
                print(f"  - Distancia {distancia}: {len(nodos)} nodos a ${costo}/m³")
    
    print(f"\nUtilidad total: ${model.ObjVal:,.0f}")
    print(f"Detalle financiero:")
    print(f"- Ingresos totales: ${revenue.getValue():,.0f}")
    print(f"- Costos cosecha: ${harvest_expenses.getValue():,.0f}")
    print(f"- Costos instalación: ${installation_expenses.getValue():,.0f}")

else:
    print("No se encontró solución óptima")