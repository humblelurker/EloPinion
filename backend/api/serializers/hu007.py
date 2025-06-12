"""
Serializadores HU-007 (informes).
Se eliminaron campos de valoración 1-5; se usa Elo.
"""
from rest_framework import serializers
from backend.reviews.models import Review


# ---------- HU-007: informe ---------- #
class ReviewSimpleSerializer(serializers.Serializer):
    producto_a = serializers.CharField(max_length=100)
    producto_b = serializers.CharField(max_length=100)
    preferido  = serializers.CharField(max_length=100)
    fecha      = serializers.DateField(format="%Y-%m-%d",
                                       input_formats=["%Y-%m-%d"])


class InformeRequestSerializer(serializers.Serializer):
    reseñas    = ReviewSimpleSerializer(many=True)
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
        model  = Review
        fields = [
            "id", "user", "product_a", "product_b",
            "preferred_product", "justification",
            "allow_comments", "status", "created_at",
        ]
        read_only_fields = fields   # ←  corregido (antes faltaba el “= fields”)
