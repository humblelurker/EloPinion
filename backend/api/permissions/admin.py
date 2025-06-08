from rest_framework.permissions import BasePermission

class IsEloAdmin(BasePermission):
    """
    Permite acceso solo si request.user.profile.is_admin == True
    (o si el superusuario de Django no tiene perfil).
    """
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        # superusers siempre pasan
        if user.is_superuser:
            return True
        # perfil podría no existir aún
        profile = getattr(user, "profile", None)
        return bool(profile and profile.is_admin)