"""
URL configuration for the Smart House Planner
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('result/', views.result, name='result'),
    path('api/chat/', views.chat_with_ai, name='chat_with_ai'),
    path('api/generate-3d/', views.generate_3d_model, name='generate_3d_model'),
    path('api/suggestions/', views.get_house_suggestions, name='get_house_suggestions'),
    path('api/status/', views.api_status, name='api_status'),
    path('download/report/<str:report_type>/<str:project_id>/', views.download_report, name='download_report'),
    path('download/3d/<str:project_id>/', views.download_3d_model, name='download_3d_model'),
]