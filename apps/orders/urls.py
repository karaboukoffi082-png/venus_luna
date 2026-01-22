from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Affichage du panier
    path('cart/', views.cart_detail, name='cart_detail'),
    
    # Actions sur le panier
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/update/<int:product_id>/', views.cart_update, name='cart_update'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    
    # Tunnel de commande
    path('checkout/', views.checkout, name='checkout'),
    path('confirm/<int:order_id>/', views.order_confirm, name='order_confirm'),
    path('history/', views.order_history, name='order_history'),
]