from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import FileResponse

from rest_framework.permissions import IsAdminUser

from backend.api.serializers.hu007 import InformeRequestSerializer
from backend.api.services.hu007 import calcular_metricas
from backend.api.utils.pdf import build_pdf
class GenerarInformeView(APIView):
    """
    POST /api/hu007/report/
    """
    # permission_classes = [IsAdminUser]
    # SOLO DESARROLLO!!
    permission_classes = []  # En tu GenerarInformeView

    def post(self, request):
        serializer = InformeRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        metrics = calcular_metricas(
            reseñas=data["reseñas"],
            start_date=data.get("start_date"),
            end_date=data.get("end_date"),
        )

        formato = data["formato"]
        if formato == "pdf":
            pdf = build_pdf(metrics)
            return FileResponse(
                pdf,
                as_attachment=True,
                filename="informe_tendencias.pdf",
                content_type="application/pdf"
            )

        if formato == "csv":
            # 1-liner usando pandas si lo agregas ↴
            # import pandas as pd
            # csv = pd.DataFrame(metrics["top_productos"]).to_csv(index=False)
            # return Response(csv, content_type="text/csv")
            return Response(
                {"detail": "CSV aún no implementado"},
                status=status.HTTP_501_NOT_IMPLEMENTED
            )

        # default → json
        return Response(metrics, status=status.HTTP_200_OK)
