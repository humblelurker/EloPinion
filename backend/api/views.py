"""
Este módulo contiene vistas relacionadas con la gestión de reseñas de productos.
Incluye validaciones, lógica de negocio y moderación de contenido mediante revisión del texto.
"""

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
import json
import logging
from .models import Product, Review

logger = logging.getLogger(__name__)

@require_POST
@login_required
def submit_review(request):
    """
    Recibe una reseña desde el frontend, valida los datos, guarda la reseña y aplica moderación automática.

    Requiere autenticación del usuario.

    Espera un cuerpo JSON con:
    - review_text (str): contenido de la reseña.
    - product_id (int): ID del producto reseñado.
    - compare_product_id (int): ID del producto con el que se compara.
    - rating (int): evaluación del producto (1 a 5).

    Retorna:
    - 200 OK con estado de moderación si se procesó exitosamente.
    - 400 Bad Request si faltan datos o el formato es inválido.
    - 404 Not Found si alguno de los productos no existe.
    - 500 Internal Server Error ante errores inesperados.
    """
    try:
        # Parsear el cuerpo JSON de la petición
        data = json.loads(request.body)
        review_text = data.get("review_text", "").strip()
        product_id = data.get("product_id")
        compare_product_id = data.get("compare_product_id")
        rating = data.get("rating")

        # Validar que la reseña no esté vacía
        if not review_text:
            return JsonResponse({"status": "error", "message": "Reseña vacía"}, status=400)

        # Validar que los campos obligatorios estén presentes
        if not all([product_id, compare_product_id, rating]):
            return JsonResponse({"status": "error", "message": "Faltan campos obligatorios"}, status=400)

        # Validar que el rating sea un entero entre 1 y 5
        if not isinstance(rating, int) or not (1 <= rating <= 5):
            return JsonResponse({"status": "error", "message": "Rating inválido"}, status=400)

        # Obtener los productos involucrados en la reseña
        product = Product.objects.get(id=product_id)
        compare_product = Product.objects.get(id=compare_product_id)

        # Crear la reseña en la base de datos
        review = Review.objects.create(
            product=product,
            user=request.user,
            title="Reseña comparativa",
            body=review_text,
            rating=rating
        )

        # Aplicar moderación automática a la reseña creada
        review.moderate_review()

        # Retornar respuesta exitosa con el estado de moderación
        return JsonResponse({'status': 'reseña procesada', 'moderation_status': review.status})

    except Product.DoesNotExist:
        # Manejar caso donde alguno de los productos no existe
        return JsonResponse({"status": "error", "message": "Producto no encontrado"}, status=404)
    except json.JSONDecodeError:
        # Manejar error en el parseo del JSON
        return JsonResponse({"status": "error", "message": "JSON inválido"}, status=400)
    except Exception as e:
        # Registrar y manejar errores inesperados
        logger.exception("Error procesando la reseña")
        return JsonResponse({"status": "error", "message": "Error interno del servidor"}, status=500)