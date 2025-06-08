"""
Serializadores para HU-007 (informes).
Se eliminaron campos de “valoración 1-5”.
El informe ahora se basa en puntaje Elo.
"""
from rest_framework import serializers
from backend.reviews.models import Comment, Report, Review

class ReviewSimpleSerializer(serializers.Serializer):
    """
    Representación mínima de una reseña
    (solo para filtrar en el generador de informes).
    """
    producto_a  = serializers.CharField(max_length=100)
    producto_b  = serializers.CharField(max_length=100)
    preferido   = serializers.CharField(max_length=100)
    fecha       = serializers.DateField(format="%Y-%m-%d",
                                        input_formats=["%Y-%m-%d"])


class InformeRequestSerializer(serializers.Serializer):
    reseñas     = ReviewSimpleSerializer(many=True)
    formato     = serializers.ChoiceField(choices=["json", "pdf", "csv"],
                                          default="json")
    start_date  = serializers.DateField(required=False)
    end_date    = serializers.DateField(required=False)

class CommentSerializer(serializers.ModelSerializer):
    user   = serializers.StringRelatedField(read_only=True)

    class Meta:
        model  = Comment
        fields = ["id", "review", "user", "text", "created_at"]
        read_only_fields = ["id", "user", "created_at"]


class ReportSerializer(serializers.ModelSerializer):
    reporter = serializers.StringRelatedField(read_only=True)

    class Meta:
        model  = Report
        fields = ["id", "review", "reporter", "reason", "status", "created_at"]
        read_only_fields = ["id", "reporter", "status", "created_at"]


class ReviewPublicSerializer(serializers.ModelSerializer):
    """
    Versión ligera para feeds o listados.
    """
    user              = serializers.StringRelatedField()
    product_a         = serializers.StringRelatedField()
    product_b         = serializers.StringRelatedField()
    preferred_product = serializers.StringRelatedField()

    class Meta:
        model  = Review
        fields = [
            "id", "user", "product_a", "product_b",
            "preferred_product", "justification",
            "allow_comments", "status", "created_at"
        ]
        read_only_fields = fields
