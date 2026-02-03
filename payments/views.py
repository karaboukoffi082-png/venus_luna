# payments/views.py
import uuid
from urllib.parse import urlencode
from django.conf import settings
from django.shortcuts import redirect
from .models import Payment

def payer_avec_bkapay(request):
    montant = 5000  # à calculer depuis le panier
    reference = f"order_{uuid.uuid4().hex}"

    payment = Payment.objects.create(
        reference=reference,
        amount=montant,
        status="pending"
    )

    params = {
        "amount": montant,
        "description": "Achat produits spirituels",
        "callback": settings.BKAPAY_CALLBACK_URL,
    }

    url = (
        f"https://bkapay.com/api-pay/{settings.BKAPAY_PUBLIC_KEY}?"
        + urlencode(params)
    )

    return redirect(url)