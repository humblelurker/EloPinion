from django.contrib.auth import authenticate, login, logout, get_user_model
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.validators import validate_email
from django.core.exceptions import ValidationError as DjangoValidationError
import json

from backend.reviews.models import UserProfile

User = get_user_model()


# ──────────────────────── Registro ───────────────────────────
@csrf_exempt
def register(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Método no permitido."}, status=405)

    try:
        data = json.loads(request.body or "{}")
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return JsonResponse({"detail": "Se requieren email y contraseña."}, status=400)

        try:
            validate_email(email)
        except DjangoValidationError:
            return JsonResponse({"detail": "Formato de email inválido."}, status=400)

        if User.objects.filter(username=email).exists():
            return JsonResponse({"detail": "El usuario ya existe."}, status=400)

        user = User.objects.create_user(username=email, email=email, password=password)
        UserProfile.objects.create(user=user)

        return JsonResponse({
            "detail": "Usuario registrado exitosamente.",
            "user": {
                "id": user.id,
                "email": user.email
            }
        }, status=201)

    except Exception as e:
        return JsonResponse({"detail": "Error inesperado al registrar usuario.", "error": str(e)}, status=500)


# ───────────────────────── Login ─────────────────────────────
@csrf_exempt
def login_view(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Método no permitido."}, status=405)

    data = json.loads(request.body or "{}")
    email, password = data.get("email"), data.get("password")

    user = authenticate(request, username=email, password=password)
    if user is None:
        return JsonResponse({"detail": "Credenciales inválidas."}, status=401)

    login(request, user)
    return JsonResponse({"detail": "Inicio de sesión exitoso.", "user": user.username})


# ───────────────────────── Logout ────────────────────────────
def logout_view(request):
    logout(request)
    return JsonResponse({"detail": "Sesión cerrada correctamente."})
