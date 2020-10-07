from django.urls import include, path

from . import views

from django_modelapiview.views import LoginView, URLsView

urlpatterns = [
    path("", include("django_routeview")),
]
