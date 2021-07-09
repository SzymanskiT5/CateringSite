from django.apps import AppConfig
from django.core import signals


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self) -> signals:
        import users.signals