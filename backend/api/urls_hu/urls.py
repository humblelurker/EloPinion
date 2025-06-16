"""
URL-patterns para las HU en backend.api.views_hu
"""
from django.urls import path
from ..views_hu.views             import (
    submit_review, random_feed, list_products,
    my_reviews_feed, delete_my_review, GenerarInformeView, whoami
)
from ..views_hu.comments_reports  import (
    create_comment, create_report,
    moderate_report, list_reports
)

urlpatterns = [
    # HU-003
    path("submit-review/", submit_review, name="submit_review"),
    path("feed/",          random_feed,  name="feed"),
    path("products/",      list_products, name="list_products"),

    # HU-004
    path("comments/", create_comment, name="comment-create"),

    # HU-002
    path("reports/",          create_report,   name="report-create"),
    path("reports/pending/",  list_reports,    name="report-list"),
    path("reports/<int:pk>/", moderate_report, name="report-moderate"),

    # HU-007
    path("hu007/report/", GenerarInformeView.as_view(), name="hu007-report"),

    # utilitarios
    path("whoami/",         whoami,             name="whoami"),
    path("my-reviews/",     my_reviews_feed,    name="my_reviews"),
    path("my-reviews/<int:pk>/", delete_my_review, name="my_review_delete"),
]
