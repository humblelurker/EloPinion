from math import pow
from ..models import Settings, Product  # Product se usa para type-hints y claridad


def update_elo_score(review):
    """
    Actualiza los puntajes Elo de los dos productos involucrados en la reseña.

    El producto marcado como preferred_product se considera ganador.
    Se aplica la fórmula Elo clásica con el K-factor definido en Settings.
    """
    winner = review.preferred_product
    loser  = review.product_b if winner == review.product_a else review.product_a

    k = Settings.get_k_factor()

    expected_w = 1 / (1 + pow(10, (loser.elo_score - winner.elo_score) / 400))
    expected_l = 1 - expected_w

    winner.elo_score += round(k * (1 - expected_w))
    loser.elo_score  += round(k * (0 - expected_l))

    winner.save(update_fields=["elo_score"])
    loser.save(update_fields=["elo_score"])
