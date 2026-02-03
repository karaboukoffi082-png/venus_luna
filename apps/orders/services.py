import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class PayPlusService:
    def __init__(self):
        self.api_key = getattr(settings, 'PAYPLUS_API_KEY', '')
        # MISE À JOUR : On retire le 'api.' si la résolution de nom échoue
        # L'URL standard actuelle est souvent celle-ci :
        self.base_url = "https://app.payplus.africa/pay/v01" 
        
        self.headers = {
            "Apikey": self.api_key, # Attention : PayPlus demande souvent Apikey en header
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def create_payment(self, order):
        # ENDPOINT MIS À JOUR : Route de redirection standard
        endpoint = f"{self.base_url}/redirect/checkout-invoice/create"
        
        # Structure attendue par PayPlus (format 'commande' > 'invoice')
        payload = {
            "commande": {
                "invoice": {
                    "items": [
                        {
                            "name": f"Commande Venus Luna #{order.id}",
                            "quantity": 1,
                            "unit_price": int(order.total),
                            "total_price": int(order.total)
                        }
                    ],
                    "total_amount": int(order.total),
                    "devise": "xof",
                    "description": f"Paiement de la commande #{order.id}"
                },
                "store": {
                    "name": "Venus Luna",
                    "website_url": settings.SITE_URL
                },
                "actions": {
                    "cancel_url": f"{settings.SITE_URL}/orders/checkout/",
                    "return_url": f"{settings.SITE_URL}/orders/confirm/{order.id}/",
                    "callback_url": getattr(settings, 'PAYPLUS_WEBHOOK_URL', f"{settings.SITE_URL}/orders/webhook/payplus/")
                }
            }
        }

        try:
            response = requests.post(endpoint, json=payload, headers=self.headers, timeout=30)
            
            # On vérifie si on a reçu du HTML au lieu de JSON (évite l'erreur char 0)
            if "text/html" in response.headers.get("Content-Type", ""):
                logger.error(f"Erreur 404/500 : Le serveur a renvoyé du HTML au lieu de JSON. URL testée: {endpoint}")
                return {"status": "error", "message": "Le service de paiement est indisponible."}

            response.raise_for_status()
            data = response.json()
            
            # PayPlus renvoie souvent le lien dans response['response_text'] ou un champ 'url'
            payment_url = data.get('payment_url') or data.get('token') # À ajuster selon le retour
            
            if payment_url:
                order.payment_url = payment_url
                order.save(update_fields=['payment_url'])
            
            return data

        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur API PayPlus : {str(e)}")
            return {"status": "error", "message": "Échec de connexion."}