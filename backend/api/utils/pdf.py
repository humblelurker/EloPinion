"""
Utilidades para PDF sin ratings 1-5.
Gráficos basados en Elo.
"""
import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Spacer, Image, Paragraph, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader


# ------------------------------------------------------------------ #
def _render_bar_chart(top_products):
    """
    top_products = [{"producto": "...", "elo": 1520}, ...]
    """
    nombres = [p["producto"] for p in top_products]
    elos    = [p["elo"]      for p in top_products]

    fig, ax = plt.subplots(figsize=(6, 3))
    ax.bar(nombres, elos, color="#4f6af5")
    ax.set_ylabel("Puntaje Elo")
    ax.set_title("Top productos por Elo")
    ax.tick_params(axis="x", rotation=15)

    buf = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format="png", dpi=150)
    plt.close(fig)
    buf.seek(0)
    return buf


def plot_evolution(evo_dict):
    """
    evo_dict = {'2025-05': 1480, '2025-06': 1502, ...}
    """
    meses   = sorted(evo_dict.keys())
    valores = [evo_dict[m] for m in meses]

    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(meses, valores, marker="o", linewidth=2, color="#4f6af5")
    ax.set_title("Evolución Elo promedio")
    ax.set_xlabel("Mes")
    ax.set_ylabel("Elo")
    ax.grid(True, linestyle="--", linewidth=0.5)

    buf = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format="png", dpi=150)
    plt.close(fig)
    buf.seek(0)
    return buf


# ------------------------------------------------------------------ #
def build_pdf(metrics):
    """
    Construye PDF con reportlab (una sola página).
    """
    buffer = io.BytesIO()
    doc    = SimpleDocTemplate(buffer, rightMargin=36, leftMargin=36)
    styles = getSampleStyleSheet()
    flow   = []

    flow.append(Paragraph("Informe de Tendencias – EloPinion", styles["Title"]))
    flow.append(Spacer(1, 12))

    # Gráfico Top N
    chart = _render_bar_chart(metrics["top_products"])
    flow.append(Image(chart, width=6 * inch, height=3 * inch))
    flow.append(Spacer(1, 12))

    # Tabla Top N
    table = [["Producto", "Elo"]] + [
        [p["producto"], p["elo"]] for p in metrics["top_products"]
    ]
    flow.append(Table(table))
    flow.append(Spacer(1, 24))

    # Evolución Elo
    evo_img = ImageReader(plot_evolution(metrics["elo_evolution"]))
    flow.append(Paragraph("Evolución Elo promedio", styles["Heading2"]))
    flow.append(Image(evo_img, width=6 * inch, height=3 * inch))

    doc.build(flow)
    buffer.seek(0)
    return buffer
