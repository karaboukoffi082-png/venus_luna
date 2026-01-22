# ...existing code...
from django.apps import AppConfig

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.accounts'
    verbose_name = "Comptes"

    def ready(self):
        # Import des signals (ou fallback sur models) pour s'assurer qu'ils sont enregistrés
        try:
            import apps.accounts.signals  # noqa: F401
        except ImportError:
            import apps.accounts.models  # noqa: F401
# ...existing code...