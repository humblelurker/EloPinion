from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from backend.reviews.models import Review, Comment, Report
from backend.api.serializers import CommentSerializer, ReportSerializer
from backend.api.permissions import IsEloAdmin


# ----------------------- Comentarios ---------------------------
class CommentCreateView(APIView):
    """
    POST /api/comments/
    { "review": 17, "text": "Buen punto..." }
    """
    def post(self, request):
        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        review = Review.objects.get(id=serializer.validated_data["review"].id)
        if not review.allow_comments:
            return Response(
                {"detail": "Comentarios desactivados para esta reseña."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        Comment.objects.create(
            review=review,
            user=request.user,
            text=serializer.validated_data["text"],
        )
        return Response({"detail": "comentario publicado"}, status=status.HTTP_201_CREATED)


# ------------------------- Reportar ----------------------------
class ReportCreateView(APIView):
    """
    POST /api/reports/
    { "review": 17, "reason": "Spam" }
    """
    def post(self, request):
        serializer = ReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        Report.objects.create(
            review   = serializer.validated_data["review"],
            reporter = request.user,
            reason   = serializer.validated_data.get("reason", ""),
        )
        return Response({"detail": "reporte enviado"}, status=status.HTTP_201_CREATED)


# --------------- Moderar reportes (solo admin) -----------------
class ReportModerateView(APIView):
    """
    PATCH /api/reports/<id>/
    { "status": "Aprobada" | "Rechazada" }
    """
    permission_classes = [IsEloAdmin]

    def patch(self, request, pk):
        try:
            report = Report.objects.get(id=pk)
        except Report.DoesNotExist:
            return Response({"detail": "Reporte no existe"}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get("status")
        if new_status not in ("Aprobada", "Rechazada"):
            return Response({"detail": "status inválido"}, status=status.HTTP_400_BAD_REQUEST)

        report.status = new_status
        report.save(update_fields=["status"])
        return Response({"detail": f"reporte {new_status.lower()}."})
