from ..models import Product, Settings

def update_elo_score(review):
    """
    Calcula y actualiza el puntaje Elo de los dos productos
    según la reseña recibida.
    """
    product_a = review.product_a
    product_b = review.product_b
    winner    = review.preferred_product

    # --- probabilidad de victoria -------------------------
    def prob(r1, r2):
        return 1 / (1 + 10 ** ((r2 - r1) / 400))

    pa = prob(product_a.elo_score, product_b.elo_score)
    pb = 1 - pa

    k = Settings.K_FACTOR       # ← ya no se llama get_k_factor

    # resultado real (1 = gana, 0 = pierde)
    sa = 1 if winner == product_a else 0
    sb = 1 - sa

    # nuevas puntuaciones
    product_a.elo_score += round(k * (sa - pa))
    product_b.elo_score += round(k * (sb - pb))

    product_a.save(update_fields=["elo_score"])
    product_b.save(update_fields=["elo_score"])
