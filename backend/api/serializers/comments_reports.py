"""
Serializadores: comentarios, reportes y reseñas públicas.
"""
from rest_framework import serializers
from backend.reviews.models import Comment, Report, Review


# ─────────── Comentarios & Reportes ──────────
class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model  = Comment
        fields = ["id", "review", "user", "text", "created_at"]
        read_only_fields = ["id", "user", "created_at"]


class ReportSerializer(serializers.ModelSerializer):
    reporter = serializers.StringRelatedField(read_only=True)

    class Meta:
        model  = Report
        fields = ["id", "review", "reporter", "reason",
                  "status", "created_at"]
        read_only_fields = ["id", "reporter", "status", "created_at"]


# Lista para el panel de moderación  (incluye datos de la reseña)
class ReportListSerializer(serializers.ModelSerializer):
    reviewer  = serializers.CharField(source="review.user.username")
    productoA = serializers.CharField(source="review.product_a.name")
    productoB = serializers.CharField(source="review.product_b.name")
    ganador   = serializers.CharField(source="review.preferred_product.name")
    reporter  = serializers.StringRelatedField()

    class Meta:
        model  = Report
        fields = [
            "id", "created_at",
            "reviewer", "productoA", "productoB", "ganador",
            "reporter", "reason", "status",
        ]


# ─────────── Reseñas para el feed ───────────
class ReviewPublicSerializer(serializers.ModelSerializer):
    user              = serializers.StringRelatedField()
    product_a         = serializers.StringRelatedField()
    product_b         = serializers.StringRelatedField()
    preferred_product = serializers.StringRelatedField()
    comments          = CommentSerializer(many=True, read_only=True)

    class Meta:
        model  = Review
        fields = [
            "id", "user",
            "product_a", "product_b", "preferred_product",
            "justification", "allow_comments",
            "comments",
            "created_at",
        ]
        read_only_fields = fields
