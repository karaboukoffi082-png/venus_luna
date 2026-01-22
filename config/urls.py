from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static



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
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Optionnel mais conseillé pour le CSS/JS en local :
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)