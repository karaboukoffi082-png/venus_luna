from django.apps import AppConfig

class OrdersConfig(AppConfig):
    # Définit le type d'ID par défaut pour les modèles de cette application
    default_auto_field = 'django.db.models.BigAutoField'
    
    # Le nom technique de l'application (chemin vers le dossier)
    name = 'apps.orders'
    
    # Le nom affiché dans l'interface d'administration Django
    verbose_name = "Gestion des Commandes"

    def ready(self):
        """
        Cette méthode est appelée quand Django démarre. 
        Elle permet de charger les signaux (signals) de l'application.
        """
        try:
            import apps.orders.signals  # noqa: F401
        except ImportError:
            # Si vous n'avez pas encore créé le fichier signals.py, 
            # Django ne bloquera pas au démarrage.
            pass