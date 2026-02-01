import json
import logging
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import FileResponse, Http404, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
from .forms import CheckoutForm
from .utils import (
    add_to_cart, update_cart_item, clear_cart, get_cart,
    cart_items_detail, send_order_confirmation
)
from .models import Order, OrderItem, ShippingAddress, ShippingZone
from apps.products.models import Product
from .services import DemarcheAPI 

logger = logging.getLogger(__name__)

# --- WEBHOOK DÉMARCHÉ ---
@csrf_exempt
def demarche_webhook(request):
    """ Réception de la confirmation de paiement par l'API Démarché """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            order_id = data.get('external_reference')
            status = data.get('status', '').upper() 

            if order_id and status in ['SUCCESS', 'PAID']:
                order = Order.objects.get(id=order_id)
                if not order.payment_status:
                    order.status = 'paid'
                    order.payment_status = True
                    order.paygate_tx_id = data.get('transaction_id')
                    order.payment_method = data.get('network')
                    order.save() 
                    
                    try:
                        send_order_confirmation(order)
                    except Exception as e:
                        logger.error(f"Erreur envoi email : {e}")

                return HttpResponse(status=200)
        except Exception as e:
            logger.error(f"Erreur Webhook : {e}")
            return HttpResponse(status=400)
            
    return HttpResponse(status=400)

# --- PANIER ---
def cart_items_detail(request):
    from apps.products.models import Product
    cart = request.session.get("cart", {})
    items = []
    total = Decimal("0.00")

    for p_id, data in cart.items():
        try:
            product = Product.objects.get(pk=p_id)
            qty = data["quantity"] if isinstance(data, dict) else data
            qty = int(qty)
            
            sub = product.price * qty
            total += sub
            
            # On ajoute 'name' et 'price' directement dans le dictionnaire
            items.append({
                "product": product, 
                "name": product.name,    # <--- Ajouté pour {{ item.name }}
                "price": product.price,  # <--- Ajouté pour {{ item.price }}
                "quantity": qty, 
                "subtotal": sub
            })
        except (Product.DoesNotExist, KeyError, TypeError, ValueError):
            continue
            
    return items, total

def cart_add(request, product_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        add_to_cart(request, product_id, quantity)
        messages.success(request, "Produit ajouté au panier !")
    return redirect('orders:cart_detail')

def cart_update(request, product_id):
    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity', 1))
            update_cart_item(request, product_id, quantity)
            messages.success(request, "Quantité mise à jour.")
        except ValueError:
            messages.error(request, "Quantité invalide.")
    return redirect('orders:cart_detail')

def cart_remove(request, product_id):
    update_cart_item(request, product_id, 0)
    messages.info(request, "Produit retiré du panier.")
    return redirect('orders:cart_detail')

# --- TUNNEL DE COMMANDE ---
def checkout(request):
    items, total = cart_items_detail(request)
    zones = ShippingZone.objects.all() # Zones de livraison dynamiques depuis la DB
    
    if not items:
        messages.error(request, "Votre panier est vide.")
        return redirect('orders:cart_detail')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        # On récupère le prix de livraison envoyé par le select HTML
        shipping_fee = int(request.POST.get('shipping_zone', 0))

        if form.is_valid():
            # 1. Création de la commande
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                email=form.cleaned_data['email'],
                notes=form.cleaned_data.get('notes', ''),
                status='pending',
                shipping_price=shipping_fee
            )
            
            # 2. Création des articles de commande
            for it in items:
                OrderItem.objects.create(
                    order=order,
                    product=it['product'],
                    name=it['product'].name,
                    price=it['product'].price,
                    quantity=it['quantity'],
                )
            
            # 3. Calcul du total final (Produits + Livraison)
            order.recalc_total()
            
            # 4. Adresse de livraison
            ShippingAddress.objects.create(
                order=order,
                full_name=form.cleaned_data['full_name'],
                phone=form.cleaned_data.get('phone', ''),
                address=form.cleaned_data['address'],
                city=form.cleaned_data.get('city', 'Lomé'),
            )

            # 5. Lancement du paiement (Push USSD)
            phone = form.cleaned_data.get('phone', '')
            clean_phone = re.sub(r'\D', '', phone) # Nettoie le numéro (enlève les espaces)
            
            # Détection Togo : TMoney (90/91/92/93/70) vs Moov (96/97/98/99)
            network = "TMONEY" if clean_phone.startswith(('90', '91', '92', '93', '70')) else "MOOV"
            
            try:
                api = DemarcheAPI()
                result = api.collect_payment(order, clean_phone, network)

                if result.get('status') in ['success', 'pending']:
                    clear_cart(request)
                    # Redirige vers la page d'attente
                    return redirect('orders:order_confirm', order_id=order.id)
                else:
                    order.delete() # Nettoyage si l'API échoue
                    messages.error(request, f"Erreur de paiement : {result.get('message', 'Échec technique')}")
            except Exception as e:
                order.delete()
                logger.error(f"Erreur API Démarché : {e}")
                messages.error(request, "Service de paiement indisponible pour le moment.")
        else:
            messages.error(request, "Veuillez vérifier les informations saisies.")
    else:
        # GET request
        initial = {'city': 'Lomé'}
        if request.user.is_authenticated:
            initial['email'] = request.user.email
        form = CheckoutForm(initial=initial)

    return render(request, 'orders/checkout.html', {
        'form': form, 
        'items': items, 
        'total': total,
        'zones': zones # On envoie les vraies zones à la template
    })

# --- SUIVI ET PDF ---
def order_confirm(request, order_id):
    """ Page de confirmation / Page d'attente USSD """
    order = get_object_or_404(Order, pk=order_id)
    if order.payment_status:
        return render(request, 'orders/confirm.html', {'order': order})
    return render(request, 'orders/waiting_confirm.html', {'order': order})

def download_receipt(request, order_id):
    """ Téléchargement du reçu PDF """
    order = get_object_or_404(Order, pk=order_id)
    # Sécurité : Seul le propriétaire ou le staff peut voir le reçu
    if not request.user.is_staff and (not request.user.is_authenticated or order.user != request.user):
        raise Http404()
    if not order.receipt:
        raise Http404("Le reçu n'est pas encore prêt.")
    return FileResponse(order.receipt.open('rb'), content_type='application/pdf')

@login_required
def order_history(request):
    """ Historique des commandes de l'utilisateur """
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/history.html', {'orders': orders})

def cart_detail(request):
    """Affiche le Sanctuaire d'Achats (panier)"""
    # On récupère les données via notre utilitaire
    items, total = cart_items_detail(request)
    
    context = {
        'cart_items': items,
        'cart_total': total,
    }
    return render(request, 'orders/cart.html', context)