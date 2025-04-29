from datos import A, A1 

A1_tuplas = {tuple(sorted(arco)) for arco in A1}
A_normalizado = {tuple(sorted(arco)) for arco in A}


#Arcos en A1 que no están en A (sobrantes)
sobrantes = A1_tuplas - A_normalizado

# Arcos en A que no están en A1 (faltantes)
faltantes = A_normalizado - A1_tuplas

print(f"Arcos sobrantes en tu versión (total: {len(sobrantes)}):")
print(sobrantes)