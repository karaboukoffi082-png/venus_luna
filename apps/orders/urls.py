from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # --- Gestion du Panier ---
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('cart/update/<int:product_id>/', views.cart_update, name='cart_update'),

    # --- Tunnel de Commande & Confirmation ---
    path('checkout/', views.checkout, name='checkout'),
    path('confirm/<int:order_id>/', views.order_confirm, name='order_confirm'),
    path('history/', views.order_history, name='order_history'),

    # --- Webhooks (Réception des paiements) ---
    # La route principale pour PayPlus
    path('webhook/payplus/', views.payplus_webhook, name='payplus_webhook'),
    
    # Conservation des alias pour la compatibilité (Démarché & Bkapay)
    path('webhook/demarche/', views.demarche_webhook, name='demarche_webhook'),
    path('webhook/bkapay/', views.bkapay_webhook, name='bkapay_webhook'),

    # --- Documents ---
    path('receipt/<int:order_id>/', views.download_receipt, name='download_receipt'),
    # Alias pour le nom utilisé dans certains fichiers (order_pdf)
    path('order/<int:order_id>/pdf/', views.order_pdf, name='order_pdf'),
]