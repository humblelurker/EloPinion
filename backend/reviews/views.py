import json
from django.http import JsonResponse
from .models import Product, Review
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def submit_review(request):
    if request.method == 'POST':
        try:
            # Leer el cuerpo del request y mostrar los datos recibidos
            data = json.loads(request.body)
            print("Datos recibidos en el backend:", data)

            product_id = data.get('product_id')
            compare_product_id = data.get('compare_product_id')
            review_text = data.get('review_text')
            rating = data.get('rating')

            # Validar que todos los datos estén presentes
            if not product_id or not compare_product_id or not review_text or not rating:
                return JsonResponse({'status': 'error', 'message': 'Faltan datos en la solicitud'}, status=400)

            # Obtener productos desde la base de datos
            try:
                product = Product.objects.get(id=product_id)
                compare_product = Product.objects.get(id=compare_product_id)
            except Product.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)

            # Crear la reseña
            review = Review.objects.create(
                product=product,
                user=request.user,
                title="Reseña comparativa",
                body=review_text,
                rating=rating
            )

            # Moderar la reseña y actualizar Elo
            review.moderate_review()

            return JsonResponse({'status': 'reseña procesada'}, status=200)

        except Exception as e:
            print(f"Error en backend: {e}")  # Log de error general
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)