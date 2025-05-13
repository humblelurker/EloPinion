from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    name = models.CharField(max_length=255)
    elo_score = models.IntegerField(default=1500)

    def __str__(self):
        return self.name

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    body = models.TextField()
    rating = models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])
    status = models.CharField(max_length=255, default='Pendiente de moderación')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Review by {self.user} on {self.product.name}'

    def moderate_review(self):
        """
        Lógica para moderar la reseña.
        Si la reseña contiene lenguaje inapropiado, será rechazada.
        Si no, será aprobada y se actualizará el puntaje Elo.
        """
        if self.body_contains_inappropriate_content():
            self.status = 'Rechazada'
        else:
            self.status = 'Aprobada'
            self.update_elo_score()

    def body_contains_inappropriate_content(self):
        """
        Verifica si la reseña contiene palabras inapropiadas.
        Este es un ejemplo simple, puedes mejorar la lógica según tus necesidades.
        """
        prohibited_words = ["idiota", "estúpido", "inútil", "mierda", "basura"]
        for word in prohibited_words:
            if word in self.body.lower():
                return True
        return False

    def update_elo_score(self):
        """
        Lógica para actualizar los puntajes Elo entre el producto y el competidor.
        """
        product = self.product
        competitor = Product.objects.exclude(id=product.id).first()  # Solo un competidor disponible para comparar

        if not competitor:
            return  # No hay competidor disponible, salir de la función

        # Compara las reseñas y actualiza Elo
        if self.rating > competitor.elo_score:
            product.elo_score += 10
            competitor.elo_score -= 10
        else:
            product.elo_score -= 10
            competitor.elo_score += 10

        # Guardar los cambios en los productos
        product.save()
        competitor.save()