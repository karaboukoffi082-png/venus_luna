from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

handler404 = 'apps.core.views.custom_404'

urlpatterns = [
    # 1. L'ADMINISTRATION (Une seule fois !)
    path('admin/', admin.site.urls),
    
    # 2. TES APPLICATIONS
    path('', include('apps.core.urls', namespace='core')),
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('products/', include('apps.products.urls', namespace='products')),
    path('orders/', include('apps.orders.urls', namespace='orders')),
    path('blog/', include('apps.blog.urls', namespace='blog')),
    path('contact/', include('apps.contact.urls', namespace='contact')),
    path('admin/', admin.site.urls), # L'admin Django classique
    path('', include('apps.core.urls', namespace='core')),
    
    # config/urls.py
    path('dashboard-admin/', include('admin_custom.urls')),
    # Note : Évite de mettre "/admin" dans l'URL pour ne pas créer de conflit
    
]

# Gestion des fichiers média et statiques
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)