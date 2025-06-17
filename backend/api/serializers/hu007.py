"""
Serializadores HU-007 (informes).
Se eliminaron campos de valoración 1-5; se usa Elo.
"""
from rest_framework import serializers
# TODO: Importar los modelos necesarios si se usan en el futuro

class ReseñaSerializer(serializers.Serializer):
    producto   = serializers.CharField(max_length=100)
    fecha      = serializers.DateField(format="%Y-%m-%d", input_formats=["%Y-%m-%d"])
    valoracion = serializers.IntegerField(min_value=1, max_value=5)
    resultado  = serializers.ChoiceField(choices=["ganó", "perdió"])  # opcional


class InformeRequestSerializer(serializers.Serializer):
    # reseñas    = ReviewSimpleSerializer(many=True)
    formato    = serializers.ChoiceField(choices=["json", "pdf", "csv"],
                                         default="json")
    start_date = serializers.DateField(required=False)
    end_date   = serializers.DateField(required=False)


# (Opcional) Un serializador público muy ligero para feeds
class ReviewPublicSerializer(serializers.ModelSerializer):
    user              = serializers.StringRelatedField()
    product_a         = serializers.StringRelatedField()
    product_b         = serializers.StringRelatedField()
    preferred_product = serializers.StringRelatedField()

    class Meta:
        # model  = Review
        fields = [
            "id", "user", "product_a", "product_b",
            "preferred_product", "justification",
            "allow_comments", "status", "created_at",
        ]
        read_only_fields = fields   # ←  corregido (antes faltaba el “= fields”)
