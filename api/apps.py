from django.apps import AppConfig
from django.db.models.signals import post_save
from django.urls import path


class ApiConfig(AppConfig):
    name = "api"
    verbose_name = "API"

    def ready(self):
        from .models import User
        from .urls import urlpatterns
        from .classviews import APIView
        from . import views
        for view in views.__dict__.values():
            if isinstance(object, type(view)) and issubclass(view, APIView):
                if view.route:
                    urlpatterns.append(path(view.route, view.as_view(), name=view.name or view.__name__))
        post_save.connect(User.add_default_permissions, sender=User)
