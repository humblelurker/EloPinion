"""
Servicios para HU-007 · Generación de informes.

• Ya no usa “valoración 1-5”.
• Top N productos se basa en su puntaje Elo actual.
• Evolución Elo = promedio mensual del Elo de todos los productos.
"""
from collections import defaultdict
from datetime import datetime
from django.db.models import Avg
from backend.reviews.models import Product, Review


def _promedio_mensual_elo():
    """
    Devuelve {'2025-05': 1480, '2025-06': 1502, ...}
    Promedia el Elo de todos los productos al final de cada mes (último día disponible).
    """
    por_mes = defaultdict(list)

    # se toman las fechas de última actualización de cada review
    qs = Review.objects.filter(status="Aprobada").values("updated_at", "product_a__elo_score", "product_b__elo_score")
    for row in qs:
        month_key = row["updated_at"].strftime("%Y-%m")
        por_mes[month_key].append(row["product_a__elo_score"])
        por_mes[month_key].append(row["product_b__elo_score"])

    return {m: round(sum(vals) / len(vals), 2) for m, vals in sorted(por_mes.items())}


def calcular_metricas(_, start_date=None, end_date=None, top_n=5):
    """
    Genera:
        • top_products  – los N productos con mayor Elo.
        • elo_evolution – dict mes→Elo promedio (todas las categorías).
    Los parámetros start_date y end_date se dejan para futura ampliación.
    """
    top_qs = (
        Product.objects
        .order_by("-elo_score")
        .values("name", "elo_score")[:top_n]
    )
    top_products = [
        {"producto": p["name"], "elo": p["elo_score"]} for p in top_qs
    ]

    metrics = {
        "top_products": top_products,
        "elo_evolution": _promedio_mensual_elo(),
    }
    return metrics
