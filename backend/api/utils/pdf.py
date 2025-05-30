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
