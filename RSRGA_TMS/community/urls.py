from django.urls import path

from RSRGA_TMS.community import views

urlpatterns = [
    path('Community_Engagement/', views.community_engagement, name='community_engagement'),
    path('feedback/', views.feedback_list_view, name='feedback'),
]