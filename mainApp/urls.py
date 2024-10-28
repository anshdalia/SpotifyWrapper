# mainApp/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Home route for mainApp
    path('main_menu/', views.main_menu, name='main_menu'),  # Main menu route
]
