from django.db import models
from django.contrib.auth.models import User
from math import pow
from django.core.exceptions import ValidationError


# ----------------------- Configuración -----------------------
class Settings:
    """
    Configuraciones globales del sistema. De momento solo contiene
    el K-factor usado en el cálculo Elo.
    """
    K_FACTOR = 32

    @staticmethod
    def get_k_factor():
        return Settings.K_FACTOR


class StatusChoices(models.TextChoices):
    """
    Opciones de estado para una reseña.
    """
    PENDIENTE = "Pendiente", "Pendiente"
    APROBADA  = "Aprobada",  "Aprobada"
    RECHAZADA = "Rechazada", "Rechazada"


# ----------------------- Modelos -----------------------
class Product(models.Model):
    """
    Producto categorizado que se puede comparar en EloPinion
    """
    CATEGORIES = [
        ('pelicula',    'Película'),
        ('serie',    'Serie'),
        ('videojuego',  'Videojuego'),
        ('restaurante', 'Restaurante'),
        ('alimento', 'Alimento'),
    ]

    name     = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=CATEGORIES, default='Película')
    elo_score = models.IntegerField(default=1500)


class Review(models.Model):
    """
    Reseña comparativa entre dos productos.

    El usuario elige product_a y product_b y marca uno de ellos como
    preferred_product. Esto se interpreta como una “partida” donde
    el preferido es el ganador a efectos del sistema Elo.
    """
    settings = Settings()
    PROHIBITED_WORDS = {"idiota", "estúpido", "inutil", "mierda", "basura"}

    # --- productos involucrados ---
    product_a = models.ForeignKey(
        Product, related_name="reviews_as_a", on_delete=models.CASCADE
    )
    product_b = models.ForeignKey(
        Product, related_name="reviews_as_b", on_delete=models.CASCADE
    )
    preferred_product = models.ForeignKey(
        Product, related_name="wins", on_delete=models.CASCADE
    )

    # --- datos del autor ---
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # --- contenido y estado ---
    justification = models.TextField(blank=True)
    status = models.CharField(
        max_length=32,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDIENTE,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            # Impide que los dos productos sean idénticos
            models.CheckConstraint(
                check=~models.Q(product_a=models.F("product_b")),
                name="product_a_not_equal_b",
            ),
        ]

    # ------------------ representaciones ------------------
    def __str__(self):
        return (
            f"{self.user} prefirió {self.preferred_product} "
            f"sobre {self.product_b if self.preferred_product == self.product_a else self.product_a}"
        )

    # ------------------ Moderación ------------------
    def moderate_review(self):
        """
        Aprueba o rechaza la reseña y, si procede, actualiza Elo.
        """
        from .services import review_services

        if self._contains_inappropriate_content():
            self.status = StatusChoices.RECHAZADA
        else:
            self.status = StatusChoices.APROBADA
            review_services.update_elo_score(self)

    def _contains_inappropriate_content(self):
        """
        Retorna True si la justificación contiene alguna palabra prohibida.
        """
        text = self.justification.lower()
        return any(word in text for word in self.PROHIBITED_WORDS)
    
    def clean(self):
        # Asegura que product_a y product_b tengan la misma categoría
        if self.product_a.category != self.product_b.category:
            raise ValidationError(
                "Ambos productos deben pertenecer a la misma categoría"
            )

    def save(self, *args, **kwargs):
        # Llama a full_clean() para ejecutar clean() antes de guardar
        self.full_clean()
        super().save(*args, **kwargs)
