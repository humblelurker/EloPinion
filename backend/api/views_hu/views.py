"""
Vistas centrales de la API (HU-001, HU-002, HU-003, HU-007).

Funciones:
• submit_review   – crea una reseña comparativa
• list_products   – catálogo completo
• random_feed     – hasta 10 reseñas aleatorias (con comentarios)
• my_reviews_feed – reseñas del usuario autenticado      ← FIX
• whoami          – utilidad sesión
• GenerarInformeView – HU-007
"""
import json, logging
from random import sample
from functools import wraps

from django.http                  import JsonResponse, FileResponse
from django.shortcuts             import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from rest_framework.views         import APIView
from rest_framework.response      import Response
from rest_framework               import status

from backend.reviews.models                import Product, Review
from backend.api.serializers.comments_reports import ReviewPublicSerializer
from backend.api.serializers.hu007         import InformeRequestSerializer
from backend.api.services.hu007            import calcular_metricas
from backend.api.utils.pdf                 import build_pdf

logger = logging.getLogger(__name__)

# ───────────────────────── helper login ───────────────────────────
def api_login_required(view):
    @wraps(view)
    def _wrap(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"detail": "Autenticación requerida"}, status=401)
        return view(request, *args, **kwargs)
    return _wrap

# ─────────────────────── HU-003: publicar reseña ───────────────────
@require_POST
@csrf_exempt
@api_login_required
def submit_review(request):
    try:
        data = json.loads(request.body)
        a_id, b_id, pref = data.get("product_a_id"), data.get("product_b_id"), data.get("preferred_id")
        justification    = data.get("justification", "").strip()
        if not all([a_id, b_id, pref]):
            return JsonResponse({"status":"error","message":"Faltan campos"}, status=400)
        if a_id == b_id:
            return JsonResponse({"status":"error","message":"Productos idénticos"}, status=400)
        if pref not in (a_id, b_id):
            return JsonResponse({"status":"error","message":"preferred_id inválido"}, status=400)

        prod_a = get_object_or_404(Product, id=a_id)
        prod_b = get_object_or_404(Product, id=b_id)
        if prod_a.category != prod_b.category:
            return JsonResponse({"status":"error","message":"Categorías distintas"}, status=400)

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

        return JsonResponse({"status":"ok","review_id":review.id,"moderation_status":review.status}, status=201)

    except json.JSONDecodeError:
        return JsonResponse({"status":"error","message":"JSON inválido"}, status=400)
    except Exception as e:
        logger.exception("Error submit_review")
        return JsonResponse({"status":"error","message":str(e)}, status=500)

# ───────────────────── catálogo de productos ──────────────────────
@require_GET
def list_products(request):
    qs = Product.objects.all().values("id", "name", "elo_score", "category")
    return JsonResponse(list(qs), safe=False)

# ─────────────────────── HU-001: feed público ─────────────────────
@require_GET
def random_feed(request):
    ids = list(Review.objects.values_list("id", flat=True))
    subset = sample(ids, min(len(ids), 10))
    qs = (Review.objects
          .filter(id__in=subset)
          .select_related("product_a", "product_b", "preferred_product", "user")
          .prefetch_related("comments__user")
          .order_by("-created_at"))
    data = ReviewPublicSerializer(qs, many=True).data
    return JsonResponse(data, safe=False)

# ──────────────────── NUEVO: feed “mis reseñas” ───────────────────
@require_GET
@api_login_required
def my_reviews_feed(request):
    """
    GET /api/my-reviews/ – devuelve hasta 50 reseñas creadas por el usuario.
    El formato es idéntico al random_feed para que el componente <Feed/>
    pueda reutilizarse sin cambios.
    """
    qs = (Review.objects
          .filter(user=request.user)
          .select_related("product_a", "product_b", "preferred_product", "user")
          .prefetch_related("comments__user")
          .order_by("-created_at")[:50])
    data = ReviewPublicSerializer(qs, many=True).data
    return JsonResponse(data, safe=False)

# ───────────────────────── util debug ─────────────────────────────
@require_GET
def whoami(request):
    if request.user.is_authenticated:
        return JsonResponse({"user": request.user.username})
    return JsonResponse({"detail":"no auth"}, status=401)

# ─────────────────────── HU-007: informes ─────────────────────────
class GenerarInformeView(APIView):
    permission_classes = []   # producción: [IsAdminUser]

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
            return FileResponse(pdf, as_attachment=True,
                                filename="informe_tendencias.pdf",
                                content_type="application/pdf")
        if data["formato"] == "csv":
            return Response({"detail":"CSV no implementado"}, status=status.HTTP_501_NOT_IMPLEMENTED)
        return Response(metrics, status=status.HTTP_200_OK)
