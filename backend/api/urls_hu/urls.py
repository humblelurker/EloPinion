from django.urls import path
from ..views_hu import views
from ..views_hu.views import GenerarInformeView
from ..views_hu.comments_reports import (
    CommentCreateView, ReportCreateView, ReportModerateView
)

urlpatterns = [
    # HU-003 reseñas
    path("submit-review/", views.submit_review, name="submit_review"),
    path("feed/",          views.random_feed,  name="feed"),
    path("products/",      views.list_products, name="list_products"),

    # HU-004 comentarios
    path("comments/", CommentCreateView.as_view(), name="comment-create"),

    # HU-002 reportar reseña
    path("reports/",           ReportCreateView.as_view(),   name="report-create"),
    path("reports/<int:pk>/",  ReportModerateView.as_view(), name="report-moderate"),

    # HU-007 informe
    path("hu007/report/", GenerarInformeView.as_view(), name="hu007-report"),
]
