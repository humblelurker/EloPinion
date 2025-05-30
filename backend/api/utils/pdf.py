import io
import matplotlib
matplotlib.use('Agg')  # Usa un backend sin GUI
import matplotlib.pyplot as plt
import seaborn as sns
from reportlab.platypus import (
    SimpleDocTemplate, Spacer, Image, Paragraph, Table
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader


def _render_bar_chart(top_productos):
    sns.set_style("darkgrid")
    fig, ax = plt.subplots(figsize=(6, 3))

    nombres   = [p["producto"] for p in top_productos]
    promedios = [p["promedio"] for p in top_productos]

    ax.bar(nombres, promedios)
    ax.set_ylabel("Valoración promedio")
    ax.set_title("Top productos")

    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return buf


def build_pdf(metrics):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, rightMargin=36, leftMargin=36)
    styles = getSampleStyleSheet()
    flow   = []

    flow.append(Paragraph("Informe de Tendencias – EloPinion", styles["Title"]))
    flow.append(Spacer(1, 12))

    # gráfico ⇢ imagen in-memory
    chart = _render_bar_chart(metrics["top_productos"])
    flow.append(Image(chart, width=6*inch, height=3*inch))
    flow.append(Spacer(1, 12))

    # tabla mini
    tabla = [["Producto", "Promedio"]] + [
        [p["producto"], f"{p['promedio']:.2f}"]
        for p in metrics["top_productos"]
    ]
    flow.append(Table(tabla))

    doc.build(flow)
    buffer.seek(0)
    return buffer

def plot_evolution(evo_dict):
    """
    Recibe {'2025-05': 960, '2025-06': 1010, ...}
    Devuelve un BytesIO con la imagen PNG.
    """
    # Ordena por fecha
    meses = sorted(evo_dict.keys())
    valores = [evo_dict[m] for m in meses]

    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(meses, valores, marker="o", linewidth=2)
    ax.set_title("Evolución Elo promedio")
    ax.set_xlabel("Mes")
    ax.set_ylabel("Puntaje Elo")
    ax.grid(True, linestyle="--", linewidth=0.5)

    buf = BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format="png", dpi=150)
    plt.close(fig)
    buf.seek(0)
    return buf


def build_report(metrics):
    """
    metrics = {
        "top_productos": [...],
        "elo_evolution": {...}
    }
    """
    c = canvas.Canvas("reporte.pdf", pagesize=A4)
    width, height = A4

    # --- Sección 1: Top productos (ya la tienes) -------------
    #  ...

    # --- Sección 2: Evolución Elo ----------------------------
    img_buf = plot_evolution(metrics["elo_evolution"])
    img = ImageReader(img_buf)
    c.drawString(40, height - 350, "Evolución Elo promedio")
    c.drawImage(img, 40, height - 650, width=500, preserveAspectRatio=True)

    c.showPage()
    c.save()