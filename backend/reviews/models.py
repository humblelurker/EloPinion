from django.db import models
from django.contrib.auth.models import User
from math import pow


# ----------------------- Configuración -----------------------
class Settings:
    """
    Esta clase contiene configuraciones globales para el sistema.
    Aquí definimos constantes como el K_FACTOR, que es un valor utilizado
    en el cálculo del puntaje Elo para los productos. 

    K_FACTOR es un parámetro que controla la sensibilidad del sistema Elo:
    un valor más alto significa que los puntajes cambian más rápido tras cada comparación.
    """
    K_FACTOR = 32

    @staticmethod
    def get_k_factor():
        """
        Método estático para obtener el valor de K_FACTOR.
        Se usa un método en lugar de acceder directamente a la variable para 
        facilitar cambios futuros, por ejemplo, si queremos cargarlo desde una configuración externa.
        """
        return Settings.K_FACTOR


class StatusChoices(models.TextChoices):
    """
    Esta clase define las opciones disponibles para el estado de una reseña (review).
    Usamos models.TextChoices, que es una forma elegante y recomendada en Django para 
    definir conjuntos de opciones para un campo CharField.

    Cada opción tiene dos valores:
    - El valor almacenado en la base de datos (ej: "Pendiente")
    - La etiqueta legible que se mostrará en interfaces o formularios (ej: "Pendiente")

    Esto ayuda a mantener el código limpio y evita errores por usar cadenas "mágicas".
    """
    PENDIENTE = "Pendiente", "Pendiente"  # La reseña está pendiente de moderación.
    APROBADA = "Aprobada", "Aprobada"    # La reseña fue aprobada y es visible.
    RECHAZADA = "Rechazada", "Rechazada" # La reseña fue rechazada por contenido inapropiado.


# ----------------------- Modelos -----------------------
class Product(models.Model):
    """
    Modelo que representa un producto que puede recibir reseñas.

    Campos:
    - name: nombre descriptivo del producto.
    - elo_score: puntaje basado en el sistema Elo que refleja la calidad o popularidad del producto.
      Este puntaje se actualiza dinámicamente según las reseñas comparativas.
    
    La clase hereda de models.Model, que es la base para todos los modelos en Django,
    permitiendo mapear esta clase a una tabla en la base de datos.
    """
    name = models.CharField(max_length=255)
    # CharField es un campo para texto corto, max_length define la longitud máxima.
    elo_score = models.IntegerField(default=1500)  
    # IntegerField para números enteros, con valor inicial estándar de 1500 en Elo.

    def __str__(self):
        """
        Método especial que define cómo se representa este objeto como cadena.
        Esto es útil para el admin de Django y para debugging,
        mostrando el nombre del producto en lugar de un objeto genérico.
        """
        return self.name


class Review(models.Model):
    """
    Modelo que representa una reseña escrita por un usuario sobre un producto.

    Campos:
    - product: ForeignKey a Product, indica a qué producto pertenece esta reseña.
      ForeignKey crea una relación de muchos a uno; muchas reseñas pueden estar asociadas a un producto.
      on_delete=models.CASCADE significa que si el producto es eliminado, sus reseñas también lo serán.
    - user: ForeignKey a User, indica quién escribió la reseña.
    - justification: texto libre donde el usuario explica su opinión.
    - status: estado actual de la reseña (pendiente, aprobada, rechazada).
    - created_at: fecha y hora en que se creó la reseña; auto_now_add=True asigna esta fecha automáticamente al crear el registro.
    - updated_at: fecha y hora de la última actualización; auto_now=True actualiza esta fecha cada vez que se guarda el objeto.

    Además, contiene lógica para moderar el contenido y actualizar el puntaje Elo del producto.
    """
    settings = Settings()
    PROHIBITED_WORDS = {"idiota", "estúpido", "inutil", "mierda", "basura"}
    # Conjunto de palabras consideradas inapropiadas para detectar contenido ofensivo.

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    justification = models.TextField(blank=True)
    # TextField para texto largo, blank=True permite que el campo quede vacío.

    status = models.CharField(
        max_length=32,
        choices= StatusChoices.choices,
        default= StatusChoices.PENDIENTE,
    )
    # CharField con opciones limitadas a StatusChoices, para controlar los estados válidos.

    created_at = models.DateTimeField(auto_now_add=True)
    # auto_now_add asigna la fecha actual al momento de crear la instancia.

    updated_at = models.DateTimeField(auto_now=True)
    # auto_now actualiza la fecha cada vez que se guarda el objeto.

    class Meta:
        # Meta es una clase interna para configurar opciones del modelo.
        # Aquí está vacía, pero podríamos agregar ordenamiento, permisos, etc.
        pass

    def __str__(self):
        """
        Representación en cadena de la reseña.
        Muestra qué usuario opinó sobre qué producto, facilitando lectura en el admin o depuración.
        """
        return f"{self.user} opinó sobre {self.product}"

    # ----------------------- Moderación -----------------------

    def moderate_review(self):
        """
        Método para moderar el contenido de la reseña.

        Este método se llama para decidir si la reseña debe ser aprobada o rechazada,
        basándose en si contiene palabras prohibidas.

        Si el contenido es inapropiado, cambia el estado a RECHAZADA.
        Si está limpio, cambia a APROBADA y actualiza el puntaje Elo del producto
        usando un servicio externo (review_services).
        """
        from .services import review_services
        if self._contains_inappropriate_content():
            self.status = StatusChoices.RECHAZADA
        else:
            self.status = StatusChoices.APROBADA
            review_services.update_elo_score(self)

    def _contains_inappropriate_content(self):
        """
        Método interno (indicado por el guion bajo inicial) que verifica si la justificación
        contiene alguna palabra prohibida.

        Convierte el texto a minúsculas para hacer la búsqueda insensible a mayúsculas/minúsculas,
        y retorna True si encuentra alguna palabra prohibida.

        Esta función es crucial para la moderación automática.
        """
        text = self.justification.lower()
        return any(word in text for word in self.PROHIBITED_WORDS)
