# serializers.py
from rest_framework import serializers

class ReseñaSerializer(serializers.Serializer):
    producto  = serializers.CharField(max_length=100)
    fecha     = serializers.DateField()               # “YYYY-MM-DD”
    valoracion = serializers.IntegerField(min_value=1, max_value=5)
    resultado  = serializers.ChoiceField(choices=["ganó", "perdió"])

class InformeRequestSerializer(serializers.Serializer):
    reseñas = ReseñaSerializer(many=True)

    # Opcional: rango de fechas, formato = pdf|csv, etc.
    formato = serializers.ChoiceField(choices=["json", "pdf"], default="json")
