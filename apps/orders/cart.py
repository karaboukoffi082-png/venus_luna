# filepath: apps/orders/cart.py
from decimal import Decimal
from apps.products.models import Product

CART_SESSION_ID = 'cart'

def get_cart(request):
    """
    Récupère le panier depuis la session.
    """
    return request.session.get(CART_SESSION_ID, {})

def save_cart(request, cart):
    """
    Sauvegarde le panier dans la session.
    """
    request.session[CART_SESSION_ID] = cart
    request.session.modified = True

def add_to_cart(request, product_id, quantity=1):
    """
    Ajoute un produit au panier ou incrémente sa quantité.
    """
    cart = get_cart(request)
    product_id_str = str(product_id)
    if product_id_str in cart:
        cart[product_id_str]['quantity'] += quantity
    else:
        product = Product.objects.get(id=product_id)
        cart[product_id_str] = {
            'name': product.name,
            'price': str(product.price),
            'quantity': quantity,
        }
    save_cart(request, cart)

def update_cart_item(request, product_id, quantity):
    """
    Met à jour la quantité d'un produit dans le panier.
    """
    cart = get_cart(request)
    product_id_str = str(product_id)
    if product_id_str in cart:
        if quantity > 0:
            cart[product_id_str]['quantity'] = quantity
        else:
            cart.pop(product_id_str)
        save_cart(request, cart)

def clear_cart(request):
    """
    Vide le panier.
    """
    save_cart(request, {})

def cart_items_detail(request):
    """
    Retourne la liste des items avec prix total pour affichage.
    """
    cart = get_cart(request)
    items = []
    total = Decimal('0.00')
    for product_id_str, item in cart.items():
        product = Product.objects.filter(id=int(product_id_str)).first()
        price = Decimal(item['price'])
        quantity = item['quantity']
        line_total = price * quantity
        total += line_total
        items.append({
            'product': product,
            'name': item['name'],
            'price': price,
            'quantity': quantity,
            'line_total': line_total,
        })
    return items, total
