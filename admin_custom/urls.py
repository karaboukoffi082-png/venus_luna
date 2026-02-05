from django.urls import path
from . import views

app_name = 'admin_custom'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
]