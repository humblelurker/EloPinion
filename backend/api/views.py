"""
Este módulo contiene vistas relacionadas con la gestión de reseñas de productos.
Incluye validaciones, lógica de negocio y moderación de contenido mediante revisión del texto.
"""

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
import json
import logging
from functools import wraps
from backend.reviews.models import Product, Review
from django.db.models import Count
from random import sample
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)

def api_login_required(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse(
                {"detail": "Autenticación requerida"}, status=401
            )
        return view(request, *args, **kwargs)
    return wrapper

@require_POST
@api_login_required
@csrf_exempt
def submit_review(request):
    """
    Recibe una reseña comparativa desde el frontend, valida los datos, guarda la reseña
    y aplica moderación automática.

    Requiere autenticación del usuario.

    Espera un cuerpo JSON con:
    - product_a_id (int): ID del primer producto.
    - product_b_id (int): ID del segundo producto.
    - preferred_id (int): ID del producto que el usuario prefiere.
    - justification (str, opcional): texto que justifica la elección.

    Retorna:
    - 201 Created y estado de moderación si se procesó exitosamente.
    - 400 Bad Request si faltan datos o el formato es inválido.
    - 404 Not Found si alguno de los productos no existe.
    - 500 Internal Server Error ante errores inesperados.
    """
    try:
        # Parsear el cuerpo JSON de la petición
        data = json.loads(request.body)
        product_a_id = data.get("product_a_id")
        product_b_id = data.get("product_b_id")
        preferred_id = data.get("preferred_id")
        justification = data.get("justification", "").strip()

        # -------- Validaciones ----------------------
        if not all([product_a_id, product_b_id, preferred_id]):
            return JsonResponse(
                {"status": "error", "message": "Faltan campos obligatorios"},
                status=400,
            )

        if product_a_id == product_b_id:
            return JsonResponse(
                {"status": "error", "message": "Los productos deben ser distintos"},
                status=400,
            )

        if preferred_id not in (product_a_id, product_b_id):
            return JsonResponse(
                {"status": "error", "message": "preferred_id debe ser A o B"},
                status=400,
            )
        
        # Recupera los objetos Product
        try:
            product_a = Product.objects.get(id=product_a_id)
            product_b = Product.objects.get(id=product_b_id)
        except Product.DoesNotExist:
            return JsonResponse({"status":"error","message":"Producto no encontrado"}, status=404)

        # Comprueba que estén en la misma categoría
        if product_a.category != product_b.category:
            return JsonResponse({
                "status":"error",
                "message":"Ambos productos deben ser de la misma categoría"
            }, status=400)
        

        preferred_product = product_a if preferred_id == product_a_id else product_b

        # -------- Crear la reseña -------------------
        review = Review.objects.create(
            product_a=product_a,
            product_b=product_b,
            preferred_product=preferred_product,
            user=request.user,
            justification=justification,
        )

        # -------- Moderación automática -------------
        review.moderate_review()

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
        logger.exception("Error procesando la reseña")
        return JsonResponse(
            {"status": "error", "message": "Error interno del servidor"}, status=500
        )
    
@require_GET
def random_feed(request):
    # trae hasta 10 reseñas al azar
    ids = list(Review.objects.values_list("id", flat=True))
    subset = sample(ids, min(len(ids), 10))
    data = (
        Review.objects.filter(id__in=subset)
        .select_related("product_a", "product_b", "preferred_product", "user")
        .values(
            "id",
            "product_a__name",
            "product_b__name",
            "preferred_product__name",
            "user__username",
            "justification",
            "created_at",
        )
    )
    return JsonResponse(list(data), safe=False)

@require_GET
def list_products(request):
    """
    Devuelve todos los productos con sus campos básicos.
    """
    qs = Product.objects.all().values("id", "name", "elo_score", "category")
    return JsonResponse(list(qs), safe=False)
