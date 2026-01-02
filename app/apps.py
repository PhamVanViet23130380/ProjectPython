from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'

    def ready(self):
        # Import signals to ensure post_save handlers are registered
        try:
            # payment signal receiver moved into views.payment_views
            from .views import payment_views  # noqa: F401
        except Exception:
            pass
