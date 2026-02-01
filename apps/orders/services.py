import requests
from django.conf import settings

class DemarcheAPI:
    def __init__(self):
        # On récupère la clé depuis les settings
        self.api_key = settings.DEMARCHE_API_KEY
        self.base_url = settings.DEMARCHE_API_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def collect_payment(self, order, phone, network):
        """
        Déclenche le Push USSD sur le téléphone du client
        network: 'TMONEY' ou 'MOOV'
        """
        endpoint = f"{self.base_url}/payments/collect"
        
        # Formatage du numéro pour le Togo (sans le +)
        clean_phone = phone.replace("+", "").replace(" ", "")
        if not clean_phone.startswith("228"):
            clean_phone = f"228{clean_phone}"

        payload = {
            "amount": int(order.total), # FCFA sans décimales
            "currency": "FCF",
            "phone": clean_phone,
            "network": network.upper(),
            "description": f"Commande #{order.id} - Site Spirituel",
            "external_reference": str(order.id),
            # L'URL que Démarché appellera une fois le paiement validé
            "callback_url": "https://ton-domaine.com/orders/webhook/demarche/"
        }

        try:
            response = requests.post(endpoint, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": str(e)}