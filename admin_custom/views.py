from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from apps.orders.models import Order
from django.utils import timezone
from django.db.models import Sum, Count

@user_passes_test(lambda u: u.is_staff)
def dashboard_view(request):
    # Statistiques de base
    orders = Order.objects.all()
    total_orders = orders.count()
    total_revenue = orders.filter(payment_status=True).aggregate(Sum('total'))['total__sum'] or 0
    total_customers = orders.values('email').distinct().count()
    pending_orders = orders.filter(status='pending').count()

    # Données pour les graphiques (simulées ici, à adapter selon tes besoins)
    chart_labels = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
    chart_values = [0, 0, 0, 0, 0, 0, total_revenue] # Exemple simple
    
    pie_labels = ["Bougies", "Encens", "Cristaux"]
    pie_values = [10, 20, 30]

    context = {
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'total_customers': total_customers,
        'pending_orders': pending_orders,
        'recent_orders': orders.order_by('-created_at')[:10],
        'chart_labels': chart_labels,
        'chart_values': chart_values,
        'pie_labels': pie_labels,
        'pie_values': pie_values,
        'today': timezone.now(),
    }
    return render(request, 'admin_custom/dashboard.html', context)