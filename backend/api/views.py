from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Product, Review

@csrf_exempt
def submit_review(request):
    """
    Esta vista recibe una reseña desde el frontend, la valida y llama a la lógica de moderación.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            review_text = data.get("review_text", "")
            product_id = data.get("product_id")
            compare_product_id = data.get("compare_product_id")
            rating = data.get("rating")

            # Validación: no permitir reseñas vacías
            if not review_text.strip():
                return JsonResponse({"status": "error", "message": "Reseña vacía"}, status=400)

            # Validación de lenguaje inapropiado
            if contains_inappropriate_content(review_text):
                return JsonResponse({"status": "rechazada", "message": "La reseña contiene lenguaje inapropiado"}, status=400)

            # Obtener el producto y el producto de comparación
            product = Product.objects.get(id=product_id)
            compare_product = Product.objects.get(id=compare_product_id)

            # Crear la reseña
            review = Review.objects.create(
                product=product,
                user=request.user,
                title="Reseña comparativa",
                body=review_text,
                rating=rating
            )

            # Llamar al método de moderación
            review.moderate_review()

            return JsonResponse({'status': 'reseña procesada'})
        
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({'status': 'error'}, status=400)

def contains_inappropriate_content(text):
    """
    Función para verificar si una reseña contiene palabras inapropiadas.
    """
    prohibited_words = ['idiota', 'estúpido', 'inútil', 'mierda', 'basura']
    text = text.lower()
    return any(word in text for word in prohibited_words)