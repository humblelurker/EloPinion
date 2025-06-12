"""
Vistas centrales de la API (HU-001, HU-002, HU-003, HU-007).

Funciones:
• submit_review  – crea una reseña comparativa
• list_products  – catálogo completo
• random_feed    – hasta 10 reseñas aleatorias (con comentarios)
• whoami         – usuario autenticado (debug)
• GenerarInformeView – HU-007 (sin cambios de lógica)
"""
import json
import logging
from random import sample

from django.http import JsonResponse, FileResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from functools import wraps

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny

from backend.reviews.models import Product, Review
from backend.api.serializers.comments_reports import ReviewPublicSerializer
from backend.api.serializers.hu007 import InformeRequestSerializer
from backend.api.services.hu007 import calcular_metricas
from backend.api.utils.pdf import build_pdf

logger = logging.getLogger(__name__)


# ────────────────────────────────────────────────────────────────────
# Helper – requerir login con vistas “función”
def api_login_required(view):
    @wraps(view)
    def _wrap(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"detail": "Autenticación requerida"}, status=401)
        return view(request, *args, **kwargs)

    return _wrap


# ─────────────────────────── HU-003  (Publicar reseña) ─────────────
@require_POST
@csrf_exempt
@api_login_required
def submit_review(request):
    """
    POST /api/submit-review/
    JSON:
    {
      "product_a_id": 1,
      "product_b_id": 2,
      "preferred_id": 1,
      "justification": "..."
    }
    """
    try:
        data = json.loads(request.body)
        a_id = data.get("product_a_id")
        b_id = data.get("product_b_id")
        pref = data.get("preferred_id")
        justification = data.get("justification", "").strip()

        # ― validaciones básicas ―
        if not all([a_id, b_id, pref]):
            return JsonResponse(
                {"status": "error", "message": "Faltan campos obligatorios"}, status=400
            )
        if a_id == b_id:
            return JsonResponse(
                {"status": "error", "message": "Los productos deben ser distintos"},
                status=400,
            )
        if pref not in (a_id, b_id):
            return JsonResponse(
                {"status": "error", "message": "preferred_id inválido"}, status=400
            )

        product_a = get_object_or_404(Product, id=a_id)
        product_b = get_object_or_404(Product, id=b_id)

        if product_a.category != product_b.category:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Ambos productos deben ser de la misma categoría",
                },
                status=400,
            )

        preferred = product_a if pref == a_id else product_b

        review = Review.objects.create(
            product_a=product_a,
            product_b=product_b,
            preferred_product=preferred,
            user=request.user,
            justification=justification,
        )
        review.moderate_review()
        review.save(update_fields=["status"])  # guarda cambio de estado

        return JsonResponse(
            {
                "status": "ok",
                "moderation_status": review.status,
                "review_id": review.id,
            },
            status=201,
        )

    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "JSON inválido"}, status=400)
    except Exception as e:
        logger.exception("Error submit_review")
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


# ───────────────────────────  Catálogo  ────────────────────────────
@require_GET
def list_products(request):
    qs = Product.objects.all().values("id", "name", "elo_score", "category")
    return JsonResponse(list(qs), safe=False)


# ─────────────────────────── HU-001  (Feed) ────────────────────────
@require_GET
def random_feed(request):
    """
    GET /api/feed/   → Máx 10 reseñas con comentarios.
    """
    ids = list(Review.objects.values_list("id", flat=True))
    subset = sample(ids, min(len(ids), 10))

    qs = (
        Review.objects.filter(id__in=subset)
        .select_related("product_a", "product_b", "preferred_product", "user")
        .prefetch_related("comments__user")
        .order_by("-created_at")
    )

    data = ReviewPublicSerializer(qs, many=True).data
    return JsonResponse(data, safe=False)


# ───────────────────────────  Debug  ───────────────────────────────
@require_GET
def whoami(request):
    if request.user.is_authenticated:
        return JsonResponse({"user": request.user.username})
    return JsonResponse({"detail": "no auth"}, status=401)


# ─────────────────────────── HU-007  (Informe) ─────────────────────
class GenerarInformeView(APIView):
    # Durante desarrollo no limitamos a admin:
    permission_classes = []  # production: [IsAdminUser]

    def post(self, request):
        ser = InformeRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        metrics = calcular_metricas(
            reseñas=data["reseñas"],
            start_date=data.get("start_date"),
            end_date=data.get("end_date"),
        )

        fmt = data["formato"]
        if fmt == "pdf":
            pdf = build_pdf(metrics)
            return FileResponse(
                pdf,
                as_attachment=True,
                filename="informe_tendencias.pdf",
                content_type="application/pdf",
            )
        if fmt == "csv":
            return Response(
                {"detail": "CSV aún no implementado"},
                status=status.HTTP_501_NOT_IMPLEMENTED,
            )
        return Response(metrics, status=status.HTTP_200_OK)
