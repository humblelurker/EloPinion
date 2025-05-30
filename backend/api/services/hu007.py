
from collections import defaultdict
from statistics import mean
from datetime import datetime
# ---- MÉTRICAS “dummy” para maqueta ---------------------------------
def _filtrar_rango(reseñas, start=None, end=None):
    if not start and not end:
        return reseñas
    out = []
    for r in reseñas:
        date = r["fecha"]
        if start and date < start:
            continue
        if end and date > end:
            continue
        out.append(r)
    return out


def calcular_metricas(reseñas, start_date=None, end_date=None, top_n=5):
    """
    Agrega mini-métricas solicitadas:
        • top productos por valoración media
        • evolución promedio Elo mensual (MAQUETA)
    """
    reseñas = _filtrar_rango(reseñas, start_date, end_date)

    # --- top productos ------------------------------------------------
    por_producto = defaultdict(list)
    for r in reseñas:
        por_producto[r["producto"]].append(r["valoracion"])

    
    promedios = [
        {"producto": p, "promedio": mean(vals)}
        for p, vals in por_producto.items()
    ]
    top_productos = sorted(promedios, key=lambda x: x["promedio"], reverse=True)[:top_n]

    # --- evolución Elo (fake, a partir de valoraciones promedio) ------
    por_mes = defaultdict(list)
    for r in reseñas:
        month_key = r["fecha"].strftime("%Y-%m")
        por_mes[month_key].append(r["valoracion"])

    elo_evolution = {
        m: round(mean(vals), 2) * 240  # factor *240 → rango 0-1200 aprox.
        for m, vals in sorted(por_mes.items())
        
    }

    return {
        "top_productos": top_productos,
        "elo_evolution": elo_evolution,
    }
