"""
Vistas HU-004 (comentarios) y HU-002 (reportes).

• POST   /api/comments/          – crear comentario
• POST   /api/reports/           – crear reporte
• GET    /api/reports/           – listar reportes PENDIENTES (solo admin)
• PATCH  /api/reports/<id>/      – admin aprueba / rechaza
"""
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.db.models            import Prefetch
from rest_framework.decorators   import (
    api_view, permission_classes, authentication_classes
)
from rest_framework.permissions  import IsAuthenticated
from rest_framework.response     import Response
from rest_framework              import status

from backend.api.authentication  import CsrfExemptSessionAuthentication
from backend.api.permissions.admin import IsEloAdmin
from backend.api.serializers.comments_reports import (
    CommentSerializer,
    ReportSerializer,
    ReportListSerializer,
)

from backend.reviews.models import Review, Comment, Report


# ────────────────────────── Comentarios ──────────────────────────
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([CsrfExemptSessionAuthentication])
def create_comment(request):
    """
    JSON → { "review": <id>, "text": "..." }
    """
    review = get_object_or_404(Review, id=request.data.get("review"))

    if not review.allow_comments:
        return Response(
            {"detail": "Comentarios desactivados por el autor."},
            status=status.HTTP_403_FORBIDDEN,
        )

    ser = CommentSerializer(data=request.data)
    if ser.is_valid():
        ser.save(user=request.user)
        return Response(ser.data, status=status.HTTP_201_CREATED)

    return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


# ─────────────────────────── Reportes ────────────────────────────
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([CsrfExemptSessionAuthentication])
def create_report(request):
    """
    JSON → { "review": <id>, "reason": "..." }
    """
    ser = ReportSerializer(data=request.data)
    if ser.is_valid():
        ser.save(reporter=request.user)
        return Response(ser.data, status=status.HTTP_201_CREATED)

    return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsEloAdmin])   # ← solo admins
def list_reports(request):
    """
    Devuelve SOLO los reportes con status = Pendiente
    """
    pending = (
        Report.objects
        .filter(status="Pendiente")
        .select_related(
            "review__product_a",
            "review__product_b",
            "review__preferred_product",
            "review__user",
            "reporter",
        )
        .order_by("-created_at")
    )
    data = ReportListSerializer(pending, many=True).data
    return Response(data)


@csrf_exempt
@api_view(["PATCH"])
@permission_classes([IsAuthenticated, IsEloAdmin])   # ← solo admins
@authentication_classes([CsrfExemptSessionAuthentication])
def moderate_report(request, pk):
    """
    JSON → { "status": "Aprobada" | "Rechazada" }
    """
    report = get_object_or_404(Report, pk=pk)
    new_status = request.data.get("status")

    if new_status not in {"Aprobada", "Rechazada"}:
        return Response(
            {"detail": "Estado inválido."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    report.status = new_status
    report.save(update_fields=["status"])
    return Response(
        {"detail": f"Reporte marcado como {new_status}."},
        status=status.HTTP_200_OK,
    )
