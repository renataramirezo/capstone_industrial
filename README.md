# capstone_industrial

# :file_folder: data

### :target: alcance.py

La función alcance() procesa un DataFrame para generar un diccionario que define los nodos forestales accesibles para faenas de tipo skidder (radio 5x5, sin esquinas) y torre (radio 7x7, con exclusiones). Cada entrada contiene el ID del nodo, nodos alcanzables y costos asociados (variables y base). Transforma datos espaciales en reglas operativas para optimizar la cosecha, diferenciando patrones de alcance según el tipo de maquinaria.

# :file_folder: docs

### :tractor: Modelo_cosecha.pdf

Archvio en formato PDF con el modelo de cosecha completo.

# :file_folder: scripts

### :page_facing_up: demo_cosecha.py

Este modelo analiza la planificación óptima de cosecha forestal para un solo mes, determinando dónde instalar maquinaria (skidders o torres) y qué áreas cosechar para maximizar ganancias. Las variables clave son: ubicación de equipos (mu, f), asignación de cosecha (x) y volumen extraído (w).

### :page_facing_up: modelo_principal.py

Este modelo de cosecha forestal multiperiodo define variables de instalación (mu), operación (f), asignación (x), volumen (w), caminos (y, l), transporte (z) e inventario (p, q). Actualmente tiene 6 restricciones (inventario, radio de cosecha, faenas únicas y continuidad operativa), pero está incompleto. Su objetivo es maximizar ganancias netas considerando costos logísticos y operativos.