from django.urls import path
from . import views

urlpatterns = [
    path('google_ads/oauth2start', views.oauth2_start, name='oauth2_start'),
    path('google_ads/oauth2callback', views.oauth2_callback, name='oauth2_callback'),
    path('google_ads/campaigns/<int:tenant_id>/', views.get_campaigns, name='get_campaigns'),
]
