from django.apps import AppConfig
from django.db.models.signals import pre_init


def create_hstore(sender, **kwargs):
    cursor = connection.cursor()
    cursor.execute("CREATE EXTENSION IF NOT EXISTS hstore")

class ApiConfig(AppConfig):
    name = 'api'

    def ready(self):
        pre_init.connect(create_hstore, sender=self)
