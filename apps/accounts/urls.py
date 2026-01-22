# ...existing code...
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    
    path('mon-compte/', views.client_dashboard, name='client_dashboard'),
    path('mon-compte/modifier/', views.edit_profile, name='profile_edit'),
    # Espace Gestion Boutique (Admin)
    path('gestion-boutique/', views.admin_dashboard, name='admin_dashboard'),

]
# ...existing code...