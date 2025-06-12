"""
URL-patterns para las HU alojadas en backend.api.views_hu
• HU-003  → reseñas / feed / productos
• HU-004  → comentarios
• HU-002  → reportar y moderar reseñas
• HU-007  → informes
"""
from django.urls import path
from ..views_hu import views                       # reseñas, feed, etc.
from ..views_hu.views import GenerarInformeView     # HU-007
from ..views_hu.comments_reports import (           # HU-004 y HU-002
    create_comment,
    create_report,
    moderate_report,
)

urlpatterns = [
    # HU-003 reseñas
    path("submit-review/", views.submit_review, name="submit_review"),
    path("feed/",          views.random_feed,  name="feed"),
    path("products/",      views.list_products, name="list_products"),

    # HU-004 comentarios
    path("comments/", create_comment, name="comment-create"),

    # HU-002 reportar reseñas
    path("reports/",          create_report,   name="report-create"),
    path("reports/<int:pk>/", moderate_report, name="report-moderate"),

    # HU-007 informes
    path("hu007/report/", GenerarInformeView.as_view(), name="hu007-report"),

    # utilitario
    path("whoami/", views.whoami, name="whoami"),
]
