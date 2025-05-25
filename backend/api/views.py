"""
Este módulo contiene vistas relacionadas con la gestión de reseñas de productos.
Incluye validaciones, lógica de negocio y moderación de contenido mediante revisión del texto.
"""

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
import json
import logging
from backend.reviews.models import Product, Review

logger = logging.getLogger(__name__)


@require_POST
@login_required
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

        # -------- Obtener productos -----------------
        try:
            product_a = Product.objects.get(id=product_a_id)
            product_b = Product.objects.get(id=product_b_id)
        except Product.DoesNotExist:
            return JsonResponse(
                {"status": "error", "message": "Producto no encontrado"}, status=404
            )

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
