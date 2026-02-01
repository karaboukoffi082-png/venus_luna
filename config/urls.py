from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView


handler404 = 'apps.core.views.custom_404'
urlpatterns = [
    path('admin/', admin.site.urls),
    # AJOUT DES NAMESPACES ICI :
    path('', include('apps.core.urls', namespace='core')),
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('products/', include('apps.products.urls', namespace='products')),
    path('orders/', include('apps.orders.urls', namespace='orders')),
    path('blog/', include('apps.blog.urls', namespace='blog')),
    path('contact/', include('apps.contact.urls', namespace='contact')),
    path('admin_custom/admin/', admin.site.urls), # L'interface admin réelle
    
    # Votre dashboard personnalisé à l'adresse /admin_custom/
    path('admin_custom/', TemplateView.as_view(template_name='admin_custom/dashboard.html'), name='custom_dashboard'),
    
    # Si vous voulez que la page d'accueil soit aussi le dashboard
    path('', TemplateView.as_view(template_name='admin_custom/dashboard.html'), name='home'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Optionnel mais conseillé pour le CSS/JS en local :
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)