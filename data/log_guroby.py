import re
import csv

def extraer_datos_log_gurobi(log_path, output_csv="gurobi_progreso.csv"):
    with open(log_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    data = []

    for line in lines:
        if line.startswith("H"):  # Heurística con incumbente
            match = re.search(r"H\s+\d+\s+\d+\s+(?P<incumbent>[\d\.eE\+\-]+)\s+(?P<bestbd>[\d\.eE\+\-]+)\s+(?P<gap>[\d\.eE\+\-%]+)\s+.*?(?P<time>\d+\.?\d*)s", line)
            if match:
                data.append({
                    'tiempo': float(match.group("time")),
                    'GAP (%)': match.group("gap").replace('%', ''),
                    'incumbente': float(match.group("incumbent")),
                    'best bound': float(match.group("bestbd")),
                })

    # Guardar CSV
    with open(output_csv, 'w', newline='') as csvfile:
        fieldnames = ['tiempo', 'GAP (%)', 'incumbente', 'best bound']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(data)

    print(f"📄 CSV guardado como: {output_csv}")

# Ejecutar
extraer_datos_log_gurobi("gurobi_log.txt")
