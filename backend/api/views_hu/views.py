"""
Este módulo contiene vistas relacionadas con la gestión de reseñas de productos.
Incluye validaciones, lógica de negocio y moderación de contenido mediante revisión del texto.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import FileResponse

from rest_framework.permissions import IsAdminUser

from backend.api.serializers.hu007 import InformeRequestSerializer
from backend.api.services.hu007 import calcular_metricas
from backend.api.utils.pdf import build_pdf
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from functools import wraps
import json
import logging
from random import sample
from backend.reviews.models import Product, Review

# Configuración del logger para registrar errores y eventos importantes
logger = logging.getLogger(__name__)

# Decorador personalizado para requerir autenticación en vistas de la API
def api_login_required(view):
    """
    Decorador que verifica si el usuario está autenticado antes de ejecutar la vista.
    Si no está autenticado, retorna un error 401 (No autorizado).
    """
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
    Vista para recibir y procesar una reseña comparativa de productos.

    Requiere autenticación del usuario y espera un cuerpo JSON con los siguientes campos:
    - product_a_id (int): ID del primer producto.
    - product_b_id (int): ID del segundo producto.
    - preferred_id (int): ID del producto preferido por el usuario.
    - justification (str, opcional): Texto justificando la elección.

    Retorna:
    - 201 Created: Si la reseña fue procesada exitosamente.
    - 400 Bad Request: Si faltan datos o el formato es inválido.
    - 404 Not Found: Si alguno de los productos no existe.
    - 500 Internal Server Error: Si ocurre un error inesperado.
    """
    try:
        # Parsear el cuerpo JSON de la petición
        data = json.loads(request.body)
        product_a_id = data.get("product_a_id")
        product_b_id = data.get("product_b_id")
        preferred_id = data.get("preferred_id")
        justification = data.get("justification", "").strip()

        # Validaciones de los datos recibidos
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
        
        # Recuperar los objetos Product desde la base de datos
        try:
            product_a = Product.objects.get(id=product_a_id)
            product_b = Product.objects.get(id=product_b_id)
        except Product.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Producto no encontrado"}, status=404)

        # Validar que ambos productos pertenezcan a la misma categoría
        if product_a.category != product_b.category:
            return JsonResponse({
                "status": "error",
                "message": "Ambos productos deben ser de la misma categoría"
            }, status=400)
        
        # Determinar cuál producto es el preferido
        preferred_product = product_a if preferred_id == product_a_id else product_b

        # Crear la reseña en la base de datos
        review = Review.objects.create(
            product_a=product_a,
            product_b=product_b,
            preferred_product=preferred_product,
            user=request.user,
            justification=justification,
        )

        # Aplicar moderación automática a la reseña
        review.moderate_review()

        # Retornar respuesta exitosa con el estado de moderación
        return JsonResponse(
            {
                "status": "ok",
                "moderation_status": review.status,
                "review_id": review.id,
            },
            status=201,
        )

    except json.JSONDecodeError:
        # Manejar errores de formato JSON
        return JsonResponse({"status": "error", "message": "JSON inválido"}, status=400)

    except Exception as e:
        # Registrar errores inesperados y retornar un error genérico
        logger.exception("Error procesando la reseña")
        return JsonResponse(
            {"status": "error", "message": "Error interno del servidor"}, status=500
        )

@require_GET
def random_feed(request):
    """
    Vista para obtener un conjunto aleatorio de hasta 10 reseñas.
    Retorna una lista de reseñas con información básica de los productos y el usuario.
    """
    # Obtener todos los IDs de las reseñas
    ids = list(Review.objects.values_list("id", flat=True))
    # Seleccionar un subconjunto aleatorio de hasta 10 IDs
    subset = sample(ids, min(len(ids), 10))
    # Consultar las reseñas seleccionadas y sus relaciones
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
    # Retornar las reseñas como una lista JSON
    return JsonResponse(list(data), safe=False)

@require_GET
def list_products(request):
    """
    Vista para listar todos los productos disponibles con información básica.
    Retorna una lista de productos con los campos:
    - id
    - name
    - elo_score
    - category
    """
    qs = Product.objects.all().values("id", "name", "elo_score", "category")
    return JsonResponse(list(qs), safe=False)

# backend/api/views_hu/hu007.py
class GenerarInformeView(APIView):
    """
    POST /api/hu007/report/
    """
    # permission_classes = [IsAdminUser]
    # SOLO DESARROLLO!!
    permission_classes = []  # En tu GenerarInformeView

    def post(self, request):
        serializer = InformeRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        metrics = calcular_metricas(
            reseñas=data["reseñas"],
            start_date=data.get("start_date"),
            end_date=data.get("end_date"),
        )

        formato = data["formato"]
        if formato == "pdf":
            pdf = build_pdf(metrics)
            return FileResponse(
                pdf,
                as_attachment=True,
                filename="informe_tendencias.pdf",
                content_type="application/pdf"
            )

        if formato == "csv":
            # 1-liner usando pandas si lo agregas ↴
            # import pandas as pd
            # csv = pd.DataFrame(metrics["top_productos"]).to_csv(index=False)
            # return Response(csv, content_type="text/csv")
            return Response(
                {"detail": "CSV aún no implementado"},
                status=status.HTTP_501_NOT_IMPLEMENTED
            )

        # default → json
        return Response(metrics, status=status.HTTP_200_OK)
