from collections import defaultdict
from datetime import datetime

def calcular_metricas(reseñas):
    productos = defaultdict(list)
    elos = defaultdict(lambda: 1000)
    historia_elo = defaultdict(list)

    for r in reseñas:
        producto = r['producto']
        productos[producto].append(r['valoracion'])

        cambio = 30 if r['resultado'] == "ganó" else -30
        elos[producto] += cambio

        historia_elo[producto].append({
            "fecha": r["fecha"],
            "elo": elos[producto]
        })

    top_productos = sorted([
        {"producto": p, "promedio": sum(v) / len(v)}
        for p, v in productos.items()
    ], key=lambda x: -x["promedio"])[:3]

    return {
        "top_productos": top_productos,
        "evolucion_elo": historia_elo
    }
