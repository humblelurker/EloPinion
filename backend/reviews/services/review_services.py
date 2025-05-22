def update_elo_score(review):
    # Importación local para evitar ciclos de dependencias
    # Esto es importante en proyectos Django donde los modelos pueden referenciarse mutuamente
    # Al importar dentro de la función, la importación ocurre solo cuando se llama a la función,
    # evitando así problemas de importación circular al cargar módulos.
    from ..models import Product 

    # Obtenemos el producto asociado a la reseña recibida
    product = review.product

    # Seleccionamos un competidor para comparar el puntaje Elo.
    # Aquí simplemente tomamos el primer producto distinto al actual.
    # En escenarios reales, esto podría ser más complejo, seleccionando múltiples competidores o basándose en criterios específicos.
    competitor = Product.objects.exclude(id=product.id).first()

    # Si no hay competidor, no podemos actualizar el puntaje Elo
    if not competitor:
        return

    # Algoritmo básico de actualización de puntaje Elo:
    # Si la calificación de la reseña es mayor que el puntaje Elo del competidor,
    # incrementamos el puntaje del producto y decrementamos el del competidor.
    # De lo contrario, hacemos lo contrario.
    #
    # Nota: Este es un modelo simplificado. El sistema Elo tradicional usa probabilidades y un factor K para ajustar los cambios.
    # Aquí se usa un valor fijo de 10 para simplificar.
    if getattr(review, "rating", 0) > competitor.elo_score:
        product.elo_score += 10
        competitor.elo_score -= 10
    else:
        product.elo_score -= 10
        competitor.elo_score += 10

    # Guardamos los cambios en la base de datos
    product.save()
    competitor.save()

    # -------------------------
    # Sugerencias para escalabilidad y mantenimiento:
    #
    # 1. Separar en capas:
    #    - Capa de estrategia: definir diferentes algoritmos de ranking (Elo clásico, Glicko, etc.)
    #    - Capa de reglas de negocio: lógica que decide cuándo y cómo actualizar los puntajes.
    #    - Capa de persistencia: acceso y modificación de la base de datos.
    #
    # 2. Parámetros dinámicos:
    #    - Introducir un factor K configurable para ajustar la sensibilidad del puntaje.
    #    - Permitir comparar contra múltiples competidores para un ranking más robusto.
    #
    # 3. Modularidad:
    #    - Extraer la lógica de cálculo Elo a una clase o módulo independiente.
    #    - Facilitar pruebas unitarias y mantenimiento.
    #
    # 4. Manejo de casos especiales:
    #    - Validar que las puntuaciones no caigan por debajo de un mínimo.
    #    - Considerar la antigüedad de las reseñas o productos para ponderar resultados.
    #
    # Estas mejoras permitirán que el sistema de ranking sea más flexible, escalable y mantenible a medida que crece la aplicación.