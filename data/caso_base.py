import grafos as gf
import datos as dt

cap_rodales = {}

for rodal in range(1, 20):
    volumen_rodal = 0
    for hect in dt.rodales[rodal]:
        volumen_rodal += dt.N[hect]["v"]
        cap_rodales[rodal] = volumen_rodal
#print(cap_rodales)
ordenado = sorted(cap_rodales.items(), key=lambda x: x[1], reverse=True)

# Mostrar el resultado
for k, v in ordenado:
    print(f"{k}: {v}")