import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Product, Review

@csrf_exempt
def submit_review(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)

    try:
        data = json.loads(request.body)
        print("Backend >>>", data)

        a_id  = data.get('product_a_id')
        b_id  = data.get('product_b_id')
        pref  = data.get('preferred_id')
        just  = data.get('justification', '')

        # --- validaciones básicas ---
        if not (a_id and b_id and pref):
            return JsonResponse({'status': 'error', 'message': 'Faltan datos'}, status=400)
        if a_id == b_id:
            return JsonResponse({'status': 'error', 'message': 'Los productos deben ser distintos'}, status=400)
        if pref not in (a_id, b_id):
            return JsonResponse({'status': 'error', 'message': 'preferred_id debe ser uno de los dos productos'}, status=400)

        # --- recuperar productos ---
        try:
            product_a = Product.objects.get(id=a_id)
            product_b = Product.objects.get(id=b_id)
        except Product.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)

        # --- crear reseña ---
        review = Review.objects.create(
            product_a        = product_a,
            product_b        = product_b,
            preferred_product= Product.objects.get(id=pref),
            user             = request.user,
            justification    = just
        )

        review.update_elo_score()
        return JsonResponse({'status': 'ok'}, status=201)

    except Exception as e:
        print("ERROR backend:", e)
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
