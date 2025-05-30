from django.urls import path
from . import views
from .views import GenerarInformeView
urlpatterns = [
    path("submit-review/", views.submit_review, name="submit_review"),
    path("feed/", views.random_feed, name="feed"),
    path("products/", views.list_products, name="list_products"),
    path("generar-informe/", GenerarInformeView.as_view()),
]
