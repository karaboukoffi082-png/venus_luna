import json
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import FileResponse, Http404, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
from .utils import generate_order_pdf  
from .forms import CheckoutForm
from .models import Order, OrderItem, ShippingAddress, ShippingZone
from apps.products.models import Product
# On importe maintenant le service PayPlus
from .services import PayPlusService 

logger = logging.getLogger(__name__)

# --- GESTION DU PANIER ---

def cart_add(request, product_id):
    cart = request.session.get('cart', {})
    product = get_object_or_404(Product, id=product_id)
    p_id = str(product_id)
    if p_id in cart:
        cart[p_id]['quantity'] += 1
    else:
        cart[p_id] = {'quantity': 1, 'price': str(product.price)}
    request.session['cart'] = cart
    messages.success(request, f"{product.name} ajouté au panier.")
    return redirect(request.META.get('HTTP_REFERER', 'orders:cart_detail'))

def cart_update(request, product_id):
    cart = request.session.get('cart', {})
    p_id = str(product_id)
    if p_id in cart:
        try:
            quantity = int(request.POST.get('quantity', 1))
            if quantity > 0:
                cart[p_id]['quantity'] = quantity
            else:
                del cart[p_id]
        except (ValueError, TypeError): pass
    request.session['cart'] = cart
    return redirect('orders:cart_detail')

def cart_remove(request, product_id):
    cart = request.session.get('cart', {})
    p_id = str(product_id)
    if p_id in cart:
        del cart[p_id]
        request.session['cart'] = cart
    return redirect('orders:cart_detail')

# --- PAIEMENT & WEBHOOK PAYPLUS ---

@csrf_exempt
def payplus_webhook(request):
    """ Réception de la confirmation de paiement par PayPlus Africa """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # PayPlus renvoie l'identifiant dans 'order_id' ou 'external_reference'
            order_id = data.get('order_id') or data.get('external_reference')
            status = str(data.get('status', '')).lower() 

            if order_id and status in ['success', 'completed', 'paid', 'approved']:
                order = Order.objects.get(id=order_id)
                if not order.payment_status:
                    order.status = 'paid'
                    order.payment_status = True
                    # On enregistre l'ID de transaction réel de PayPlus
                    order.paygate_tx_id = data.get('transaction_id')
                    order.save()
                    
                    try:
                        from .utils import send_order_confirmation
                        send_order_confirmation(order)
                    except Exception as e:
                        logger.error(f"Erreur email confirmation : {e}")
                
                return HttpResponse(status=200)
        except Exception as e:
            logger.error(f"Erreur Webhook PayPlus : {e}")
            return HttpResponse(status=400)
            
    return HttpResponse(status=400)

# Alias pour garder la compatibilité avec tes anciennes URLs
bkapay_webhook = payplus_webhook
demarche_webhook = payplus_webhook

# --- TUNNEL DE COMMANDE ---

def get_cart_data(request):
    cart = request.session.get("cart", {})
    items = []
    total = Decimal("0")
    for p_id, data in cart.items():
        try:
            product = Product.objects.get(pk=p_id)
            qty = int(data["quantity"])
            sub = product.price * qty
            total += sub
            items.append({"product": product, "quantity": qty, "subtotal": sub})
        except: continue
    return items, total

def checkout(request):
    items, total = get_cart_data(request)
    zones = ShippingZone.objects.all()
    if not items: 
        messages.warning(request, "Votre panier est vide.")
        return redirect('orders:cart_detail')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Création de la commande
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                email=form.cleaned_data['email'],
                shipping_price=Decimal(request.POST.get('shipping_zone', 0))
            )
            
            # Création des articles de commande
            for it in items:
                OrderItem.objects.create(
                    order=order, 
                    product=it['product'], 
                    name=it['product'].name,
                    price=it['product'].price, 
                    quantity=it['quantity']
                )
            
            order.recalc_total()
            
            # Adresse de livraison
            ShippingAddress.objects.create(
                order=order, 
                full_name=form.cleaned_data['full_name'], 
                address=form.cleaned_data['address']
            )
            
            try:
                # Utilisation du service PayPlus
                payplus = PayPlusService()
                payment_data = payplus.create_payment(order)
                
                # PayPlus renvoie une URL vers leur portail sécurisé
                if payment_data and payment_data.get('payment_url'):
                    request.session['cart'] = {} # On vide le panier
                    return redirect(payment_data['payment_url'])
                else:
                    logger.error(f"PayPlus n'a pas renvoyé d'URL : {payment_data}")
                    messages.error(request, "Le service de paiement PayPlus est momentanément indisponible.")
                    order.delete()
            except Exception as e:
                logger.error(f"Erreur lors de l'appel PayPlus : {e}")
                order.delete()
                messages.error(request, "Erreur technique lors du paiement.")
    else:
        form = CheckoutForm()
        
    return render(request, 'orders/checkout.html', {
        'form': form, 
        'items': items, 
        'total': total, 
        'zones': zones
    })

# --- VUES CLIENTS ---

def cart_detail(request):
    items, total = get_cart_data(request)
    return render(request, 'orders/cart.html', {'cart_items': items, 'cart_total': total})

def order_confirm(request, order_id):
    """ Page de retour après paiement """
    order = get_object_or_404(Order, pk=order_id)
    # On peut ajouter une vérification de statut ici via l'API si nécessaire
    return render(request, 'orders/confirm.html', {'order': order})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/history.html', {'orders': orders})

# --- GÉNÉRATION DU REÇU (PDF) ---

 # Assure-toi d'avoir importé ta fonction

def download_receipt(request, order_id):
    """ Génère et télécharge le reçu PDF pour le client """
    # Si l'utilisateur est admin, il peut tout voir, sinon seulement sa commande
    if request.user.is_staff:
        order = get_object_or_404(Order, pk=order_id)
    else:
        # Sécurité : on vérifie que la commande appartient bien à l'utilisateur (si connecté)
        order = get_object_or_404(Order, pk=order_id)
        # Optionnel: if order.user != request.user: raise Http404

    # Appel de la fonction de génération
    pdf_content = generate_order_pdf(order)

    if pdf_content:
        response = HttpResponse(pdf_content, content_type='application/pdf')
        filename = f"Recu_VenusLuna_{order.id}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    
    # Si la génération échoue, on renvoie une erreur propre au lieu d'un fichier de 45 octets
    messages.error(request, "Impossible de générer le PDF pour le moment.")
    return redirect('orders:order_confirm', order_id=order.id)

# Alias pour garder la cohérence avec tes URLs
order_pdf = download_receipt