"""
Vistas centrales de la API (HU-001 … HU-009)

Funciones principales
────────────────────────────────────────────────────────────────────────────
• submit_review      – crea una reseña comparativa               (HU-003)
• list_products      – catálogo completo
• random_feed        – feed público totalmente aleatorio         (HU-001)
• personalized_feed  – feed ordenado por categoría preferida     (HU-009)
• my_reviews_feed    – reseñas del usuario autenticado
• delete_my_review   – elimina una reseña propia                 (HU-008)
• whoami             – utilidad sesión
• GenerarInformeView – generación de informes                    (HU-007)
"""
import json
import logging
import random
from collections import Counter
from random import sample
from functools import wraps

from django.http import JsonResponse, FileResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import (
    require_GET,
    require_POST,
    require_http_methods,
)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from backend.reviews.models import Product, Review
from backend.api.serializers.comments_reports import ReviewPublicSerializer
from backend.api.serializers.hu007 import InformeRequestSerializer
from backend.api.services.hu007 import calcular_metricas
from backend.api.utils.pdf import build_pdf

logger = logging.getLogger(__name__)

# ───────────────────────── helper login ───────────────────────────
def api_login_required(view):
    @wraps(view)
    def _wrap(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"detail": "Autenticación requerida"}, status=401)
        return view(request, *args, **kwargs)

    return _wrap


# ─────────────────────── HU-003: publicar reseña ──────────────────
@require_POST
@csrf_exempt
@api_login_required
def submit_review(request):
    try:
        data = json.loads(request.body or "{}")
        a_id = data.get("product_a_id")
        b_id = data.get("product_b_id")
        pref = data.get("preferred_id")
        justification = data.get("justification", "").strip()

        if not all([a_id, b_id, pref]):
            return JsonResponse(
                {"status": "error", "message": "Faltan campos"}, status=400
            )
        if a_id == b_id:
            return JsonResponse(
                {"status": "error", "message": "Productos idénticos"}, status=400
            )
        if pref not in (a_id, b_id):
            return JsonResponse(
                {"status": "error", "message": "preferred_id inválido"}, status=400
            )

        prod_a = get_object_or_404(Product, id=a_id)
        prod_b = get_object_or_404(Product, id=b_id)
        if prod_a.category != prod_b.category:
            return JsonResponse(
                {"status": "error", "message": "Categorías distintas"}, status=400
            )

        preferred = prod_a if pref == a_id else prod_b
        review = Review.objects.create(
            product_a=prod_a,
            product_b=prod_b,
            preferred_product=preferred,
            user=request.user,
            justification=justification,
        )
        review.moderate_review()
        review.save(update_fields=["status"])

        return JsonResponse(
            {"status": "ok", "review_id": review.id, "moderation_status": review.status},
            status=201,
        )

    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "JSON inválido"}, status=400)
    except Exception as e:
        logger.exception("Error submit_review")
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


# ───────────────────── catálogo de productos ─────────────────────
@require_GET
def list_products(request):
    qs = Product.objects.all().values("id", "name", "elo_score", "category")
    return JsonResponse(list(qs), safe=False)


# ─────────────── HU-001: feed público totalmente aleatorio ───────
@require_GET
def random_feed(request):
    """
    Devuelve hasta 10 reseñas completamente aleatorias,
    incluido el orden de aparición.
    """
    ids = list(Review.objects.values_list("id", flat=True))
    subset = sample(ids, min(len(ids), 10))

    qs = (
        Review.objects.filter(id__in=subset)
        .select_related("product_a", "product_b", "preferred_product", "user")
        .prefetch_related("comments__user")
    )

    reviews = list(qs)
    random.shuffle(reviews)  # orden aleatorio en cada refresh

    data = ReviewPublicSerializer(reviews, many=True).data
    return JsonResponse(data, safe=False)


# ──────────────── HU-009: feed personalizado simple ──────────────
@require_GET
@api_login_required
def personalized_feed(request):
    """
    Ordena el feed colocando primero las reseñas de la(s) categoría(s)
    en la(s) que el usuario ha publicado más reseñas propias.
    - Si el usuario no tiene historial → random_feed.
    - Si existe empate total entre todas las categorías → random_feed.
    """
    user_reviews = Review.objects.filter(user=request.user)
    if not user_reviews.exists():
        return random_feed(request)

    counts = Counter(user_reviews.values_list("product_a__category", flat=True))
    max_ct = max(counts.values())
    top_cats = [c for c, n in counts.items() if n == max_ct]

    # Empate total: sin preferencia real
    if len(top_cats) == len(counts):
        return random_feed(request)

    random.shuffle(top_cats)  # desempate entre favoritas

    qs_top = (
        Review.objects.filter(product_a__category__in=top_cats)
        .select_related("product_a", "product_b", "preferred_product", "user")
        .prefetch_related("comments__user")
        .order_by("-created_at")
    )

    qs_rest = (
        Review.objects.exclude(product_a__category__in=top_cats)
        .select_related("product_a", "product_b", "preferred_product", "user")
        .prefetch_related("comments__user")
    )

    # Mezclamos el resto para que no sea cronológico estricto
    rest_list = list(qs_rest)
    random.shuffle(rest_list)

    reviews = list(qs_top[:50]) + rest_list
    data = ReviewPublicSerializer(reviews[:50], many=True).data
    return JsonResponse(data, safe=False)


# ───────────────── feed “mis reseñas” ─────────────────────────────
@require_GET
@api_login_required
def my_reviews_feed(request):
    qs = (
        Review.objects.filter(user=request.user)
        .select_related("product_a", "product_b", "preferred_product", "user")
        .prefetch_related("comments__user")
        .order_by("-created_at")[:50]
    )
    data = ReviewPublicSerializer(qs, many=True).data
    return JsonResponse(data, safe=False)


# ─────────────── eliminar reseña propia (HU-008) ──────────────────
@require_http_methods(["DELETE"])
@csrf_exempt
@api_login_required
def delete_my_review(request, pk):
    review = get_object_or_404(Review, pk=pk, user=request.user)
    review.delete()
    return JsonResponse({"detail": "Review eliminada"}, status=204)


# ───────────────────────── util debug ─────────────────────────────
@require_GET
def whoami(request):
    if request.user.is_authenticated:
        profile = getattr(request.user, "profile", None)
        return JsonResponse(
            {
                "user": request.user.username,
                "is_admin": bool(
                    request.user.is_superuser or (profile and profile.is_admin)
                ),
            }
        )
    return JsonResponse({"detail": "no auth"}, status=401)


# ───────────────────────── HU-007: informes ──────────────────────
class GenerarInformeView(APIView):
    permission_classes = []  # producción: [IsAdminUser]

    def post(self, request):
        ser = InformeRequestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        metrics = calcular_metricas(
            reseñas=data["reseñas"],
            start_date=data.get("start_date"),
            end_date=data.get("end_date"),
        )

        if data["formato"] == "pdf":
            pdf = build_pdf(metrics)
            return FileResponse(
                pdf,
                as_attachment=True,
                filename="informe_tendencias.pdf",
                content_type="application/pdf",
            )

        if data["formato"] == "csv":
            return Response(
                {"detail": "CSV no implementado"},
                status=status.HTTP_501_NOT_IMPLEMENTED,
            )

        return Response(metrics, status=status.HTTP_200_OK)
