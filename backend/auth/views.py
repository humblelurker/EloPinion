from django.contrib.auth import authenticate, login, logout, get_user_model
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from backend.reviews.models import UserProfile 

User = get_user_model()

@csrf_exempt
def register(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Método no permitido"}, status=405)

    data = json.loads(request.body)
    email, password = data.get("email"), data.get("password")

    if not (email and password):
        return JsonResponse({"detail": "Email y password requeridos"}, status=400)
    if User.objects.filter(username=email).exists():
        return JsonResponse({"detail": "Ya existe usuario"}, status=400)

    user = User.objects.create_user(username=email, email=email, password=password)
    UserProfile.objects.create(user=user)          # ← crea perfil por defecto
    return JsonResponse({"detail": "usuario creado", "id": user.id}, status=201)


@csrf_exempt
def login_view(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Método no permitido"}, status=405)

    data = json.loads(request.body)
    email, password = data.get("email"), data.get("password")
    user = authenticate(request, username=email, password=password)
    if user is None:
        return JsonResponse({"detail": "Credenciales incorrectas"}, status=401)

    login(request, user)  # crea sesión
    return JsonResponse({"detail": "ok", "user": user.username})


def logout_view(request):
    logout(request)
    return JsonResponse({"detail": "sesión cerrada"})
