from django.urls import path
from ...api.views_hu.hu007 import GenerarInformeView

urlpatterns = [
    path("report/", GenerarInformeView.as_view(), name="hu007-report"),
]