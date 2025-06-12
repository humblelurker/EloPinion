from rest_framework.authentication import SessionAuthentication

class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
    Igual que SessionAuthentication, pero salta la comprobación CSRF
    (útil cuando el frontend ya se protege con CORS y sólo queremos
    cookies de sesión durante desarrollo).
    """
    def enforce_csrf(self, request):
        return  # ← no hace nada
