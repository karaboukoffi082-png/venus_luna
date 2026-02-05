from django.apps import AppConfig

class AdminCustomConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    # TU DOIS AVOIR CECI :
    name = 'apps.admin_custom'