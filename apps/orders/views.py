from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from .forms import CheckoutForm
from .utils import add_to_cart, update_cart_item, clear_cart, cart_items_detail, get_cart, send_order_confirmation
from .models import Order, OrderItem, ShippingAddress
from apps.products.models import Product

def cart_detail(request):
    """ Affiche le contenu du panier """
    items, total = cart_items_detail(request)
    return render(request, 'orders/cart.html', {
        'cart_items': items,
        'total_price': total,
        'total': total # Pour la compatibilité avec tes templates
    })

def cart_add(request, product_id):
    """ Action d'ajout au panier via POST """
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        add_to_cart(request, product_id, quantity)
        messages.success(request, "Produit ajouté au panier !")
    return redirect('orders:cart_detail')

def cart_remove(request, product_id):
    """ Supprime un produit du panier """
    update_cart_item(request, product_id, 0)
    messages.info(request, "Produit retiré du panier.")
    return redirect('orders:cart_detail')

def cart_update(request, product_id):
    """ Met à jour la quantité depuis la page panier """
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        update_cart_item(request, product_id, quantity)
        messages.success(request, "Quantité mise à jour.")
    return redirect('orders:cart_detail')

def checkout(request):
    """ Gestion du tunnel d'achat """
    items, total = cart_items_detail(request)
    
    if not items:
        messages.error(request, "Votre panier est vide.")
        return redirect('orders:cart_detail')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Création de la commande
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                email=form.cleaned_data['email'],
                notes=form.cleaned_data.get('notes', ''),
            )
            
            # Création des lignes de commande
            for it in items:
                OrderItem.objects.create(
                    order=order,
                    product=it['product'],
                    name=it['name'],
                    price=it['price'],
                    quantity=it['quantity'],
                )
            
            order.recalc_total()
            
            # Adresse de livraison
            ShippingAddress.objects.create(
                order=order,
                full_name=form.cleaned_data['full_name'],
                phone=form.cleaned_data.get('phone', ''),
                address=form.cleaned_data['address'],
                city=form.cleaned_data.get('city', ''),
            )
            
            # Nettoyage et email
            clear_cart(request)
            try:
                send_order_confirmation(order)
            except:
                pass
                
            messages.success(request, f"Commande #{order.id} validée.")
            return redirect('orders:order_confirm', order_id=order.id)
    else:
        initial = {}
        if request.user.is_authenticated:
            initial['email'] = request.user.email
        form = CheckoutForm(initial=initial)

    return render(request, 'orders/checkout.html', {
        'form': form, 
        'items': items, 
        'total': total,
        'zones': [
            {'name': 'Lomé (Centre)', 'price': 1000},
            {'name': 'Agoè / Adidogomé', 'price': 1500},
            {'name': 'Baguidah / Aneho', 'price': 2500},
        ]
    })

def order_confirm(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    return render(request, 'orders/confirm.html', {'order': order})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/history.html', {'orders': orders})