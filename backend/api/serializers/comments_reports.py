"""
Serializadores: comentarios, reportes y reseñas públicas.
"""
from rest_framework import serializers
from backend.reviews.models import Comment, Report, Review


# ------------ Comentarios & Reportes -------------------------
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


# ------------ Reseñas para el feed ---------------------------
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
            "comments",                 # ← lista embebida
            "created_at",
        ]
        read_only_fields = fields
