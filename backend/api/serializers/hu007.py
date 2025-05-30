from rest_framework import serializers

class ReseñaSerializer(serializers.Serializer):
    producto   = serializers.CharField(max_length=100)
    fecha      = serializers.DateField(format="%Y-%m-%d", input_formats=["%Y-%m-%d"])
    valoracion = serializers.IntegerField(min_value=1, max_value=5)
    resultado  = serializers.ChoiceField(choices=["ganó", "perdió"])  # opcional

class InformeRequestSerializer(serializers.Serializer):
    reseñas = ReseñaSerializer(many=True)
    formato = serializers.ChoiceField(
        choices=["json", "pdf", "csv"],
        default="json"
    )
    # filtros opcionales para futuro ↴
    start_date = serializers.DateField(required=False)
    end_date   = serializers.DateField(required=False)
