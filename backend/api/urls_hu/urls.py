from django.urls import path
from ..views_hu import views
from django.urls import include
from backend.api.urls_hu import urlpatterns as hu007_urls
from django.urls import path
from ...api.views_hu.views import GenerarInformeView

urlpatterns = [
    path("submit-review/", views.submit_review, name="submit_review"),
    path("feed/", views.random_feed, name="feed"),
    path("products/", views.list_products, name="list_products"),
    path("hu007/", include((hu007_urls, "hu007"))),
]

urlpatterns = [
    path("report/", GenerarInformeView.as_view(), name="hu007-report"),
]