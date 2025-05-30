from django.urls import path
from . import views
from django.urls import include
urlpatterns = [
    path("submit-review/", views.submit_review, name="submit_review"),
    path("feed/", views.random_feed, name="feed"),
    path("products/", views.list_products, name="list_products"),

]
from backend.api.urls_hu import urlpatterns as hu007_urls

urlpatterns = [
    path("hu007/", include((hu007_urls, "hu007"))),
]