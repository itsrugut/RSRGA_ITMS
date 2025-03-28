from django.urls import path

from RSRGA_TMS.users import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('api/token-auth/', views.CustomAuthToken.as_view(), name='api_token_auth'),
]
