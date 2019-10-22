from django.apps import AppConfig

from django.db import connection


class ApiConfig(AppConfig):
    name = 'api'

    def ready(self):
        print("Create HSTORE")
        with connection.cursor() as cursor:
            cursor.execute("CREATE EXTENSION IF NOT EXISTS hstore")
