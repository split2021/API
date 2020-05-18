from django.apps import AppConfig
from django.db.models.signals import post_save


class ApiConfig(AppConfig):
    name = "api"
    verbose_name = "API"

    def ready(self):
        from .models import User
        post_save.connect(User.add_default_permissions, sender=User)
