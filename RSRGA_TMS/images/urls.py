from django.urls import path

from RSRGA_TMS.images import views

urlpatterns = [
    path('gallery/', views.gallery, name='gallery'),
    path('drone_campaigns/', views.drone_campaigns, name='drone_campaigns'),
]