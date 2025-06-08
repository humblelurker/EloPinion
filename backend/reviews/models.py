"""
Modelos principales de EloPinion.

Cambios añadidos:
- `UserProfile` con booleano `is_admin`.
- Campo `allow_comments` en Review.
- Modelo `Comment` (comentarios en reseñas).
- Modelo `Report` (reportes de reseñas).
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


# ----------------------- Configuración -----------------------
class Settings:
    """Constantes globales (por ahora, solo K-factor Elo)."""
    K_FACTOR = 32


# ----------------------- Auxiliares --------------------------
class StatusChoices(models.TextChoices):
    PENDIENTE = "Pendiente", "Pendiente"
    APROBADA  = "Aprobada",  "Aprobada"
    RECHAZADA = "Rechazada", "Rechazada"


class ReportStatus(models.TextChoices):
    PENDIENTE = "Pendiente", "Pendiente"
    APROBADA  = "Aprobada",  "Aprobada"       # el admin confirma el reporte
    RECHAZADA = "Rechazada", "Rechazada"      # el admin descarta el reporte


# ----------------------- Perfil de usuario -------------------
class UserProfile(models.Model):
    """
    Perfil extendido: sólo añade un flag de administrador.
    El booleano se puede cambiar manualmente en el admin de Django.
    """
    user      = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    is_admin  = models.BooleanField(default=False)

    def __str__(self):
        return f"Perfil de {self.user.username}"


# ----------------------- Productos ---------------------------
class Product(models.Model):
    CATEGORIES = [
        ("pelicula",   "Película"),
        ("serie",      "Serie"),
        ("videojuego", "Videojuego"),
        ("restaurante","Restaurante"),
        ("alimento",   "Alimento"),
    ]

    name       = models.CharField(max_length=255)
    category   = models.CharField(max_length=20, choices=CATEGORIES)
    elo_score  = models.IntegerField(default=1500)

    def __str__(self):
        return self.name


# ----------------------- Reseñas -----------------------------
class Review(models.Model):
    """
    El usuario compara product_a vs product_b y marca su preferido.
    """

    PROHIBITED_WORDS = {"idiota", "estúpido", "inutil", "mierda", "basura"}

    # Productos involucrados
    product_a = models.ForeignKey(Product, related_name="reviews_as_a", on_delete=models.CASCADE)
    product_b = models.ForeignKey(Product, related_name="reviews_as_b", on_delete=models.CASCADE)
    preferred_product = models.ForeignKey(Product, related_name="wins", on_delete=models.CASCADE)

    # Autor
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Contenido y estado
    justification   = models.TextField(blank=True)
    allow_comments  = models.BooleanField(default=True)          # ← nuevo
    status          = models.CharField(max_length=32, choices=StatusChoices.choices,
                                       default=StatusChoices.PENDIENTE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            # productos distintos
            models.CheckConstraint(
                check=~models.Q(product_a=models.F("product_b")),
                name="product_a_not_equal_b",
            ),
        ]

    # ---------- validaciones ----------
    def clean(self):
        if self.product_a.category != self.product_b.category:
            raise ValidationError("Ambos productos deben pertenecer a la misma categoría")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    # ---------- moderación ----------
    def moderate_review(self):
        from .services import review_services
        if self._contains_inappropriate_content():
            self.status = StatusChoices.RECHAZADA
        else:
            self.status = StatusChoices.APROBADA
            review_services.update_elo_score(self)

    def _contains_inappropriate_content(self):
        texto = self.justification.lower()
        return any(pal in texto for pal in self.PROHIBITED_WORDS)

    def __str__(self):
        loser = self.product_b if self.preferred_product == self.product_a else self.product_a
        return f"{self.user} prefirió {self.preferred_product} sobre {loser}"


# ----------------------- Comentarios -------------------------
class Comment(models.Model):
    """
    Comentario en una reseña.
    Solo se permite si `review.allow_comments` es True.
    """
    review  = models.ForeignKey(Review, related_name="comments", on_delete=models.CASCADE)
    user    = models.ForeignKey(User, on_delete=models.CASCADE)
    text    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if not self.review.allow_comments:
            raise ValidationError("El autor ha desactivado los comentarios para esta reseña.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Coment. de {self.user} en Review {self.review_id}"


# ----------------------- Reportes ----------------------------
class Report(models.Model):
    """
    Un usuario reporta una reseña.
    El administrador revisa y aprueba / rechaza.
    """
    review  = models.ForeignKey(Review, related_name="reports", on_delete=models.CASCADE)
    reporter = models.ForeignKey(User, on_delete=models.CASCADE)
    reason   = models.TextField(blank=True)
    status   = models.CharField(max_length=10, choices=ReportStatus.choices,
                                default=ReportStatus.PENDIENTE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reporte #{self.id} sobre Review {self.review_id} – {self.status}"
