from django.db import models
from django.contrib.auth.models import User
from math import pow

K_FACTOR = 32  # Constante para ajustar la sensibilidad con la que cambian los puntajes ELO

class Product(models.Model):
    name = models.CharField(max_length=255)
    elo_score = models.FloatField(default=1500)

    def __str__(self):
        return self.name


class Review(models.Model):
<<<<<<< HEAD
    product_a = models.ForeignKey(
        Product, related_name="reviews_as_a", on_delete=models.CASCADE
    )
    product_b = models.ForeignKey(
        Product, related_name="reviews_as_b", on_delete=models.CASCADE
    )

    # Ganador de la “partida”
    preferred_product = models.ForeignKey(
        Product, related_name="wins", on_delete=models.CASCADE
    )

=======
    PROHIBITED_WORDS = {"idiota", "estúpido", "inútil", "mierda", "basura"}

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
>>>>>>> 69f7651 (Cleanup: remove unused files and optimize review submission logic)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    justification = models.TextField(blank=True)
    status = models.CharField(
        max_length=32,
        choices=[("Pendiente", "Pendiente"), ("Aprobada", "Aprobada"), ("Rechazada", "Rechazada")],
        default="Pendiente",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            # impide que los dos productos sean iguales
            models.CheckConstraint(
                check=~models.Q(product_a=models.F("product_b")),
                name="product_a_not_equal_b",
            )
        ]

    def __str__(self):
        return f"{self.user} prefirió {self.preferred_product} sobre otro producto"

    # ----------------------- Moderación -----------------------

    def moderate_review(self):
<<<<<<< HEAD
        """Aprueba o rechaza la reseña y, si procede, actualiza Elo."""
        if self.body_contains_inappropriate_content():
            self.status = "Rechazada"
=======
        if self._contains_inappropriate_content():
            self.status = 'Rechazada'
>>>>>>> 69f7651 (Cleanup: remove unused files and optimize review submission logic)
        else:
            self.status = "Aprobada"
            self.update_elo_score()

<<<<<<< HEAD
    def body_contains_inappropriate_content(self):
        bad_words = {"idiota", "estúpido", "inútil", "mierda", "basura"}
        return any(w in self.justification.lower() for w in bad_words)

    # ----------------------- Elo -----------------------

    def update_elo_score(self):
        """Aplica fórmula Elo entre los dos productos."""
        winner = self.preferred_product
        loser = self.product_b if winner == self.product_a else self.product_a

        expected_w = 1 / (1 + pow(10, (loser.elo_score - winner.elo_score) / 400))
        expected_l = 1 - expected_w

        winner.elo_score += K_FACTOR * (1 - expected_w)
        loser.elo_score += K_FACTOR * (0 - expected_l)

        winner.save(update_fields=["elo_score"])
        loser.save(update_fields=["elo_score"])
=======
    def _contains_inappropriate_content(self):
        text = self.body.lower()
        return any(word in text for word in self.PROHIBITED_WORDS)

    def update_elo_score(self):
        product = self.product
        competitor = Product.objects.exclude(id=product.id).first()

        if not competitor:
            return

        if self.rating > competitor.elo_score:
            product.elo_score += 10
            competitor.elo_score -= 10
        else:
            product.elo_score -= 10
            competitor.elo_score += 10

        product.save()
        competitor.save()
>>>>>>> 69f7651 (Cleanup: remove unused files and optimize review submission logic)
