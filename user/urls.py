# users/urls.py
from django.urls import path
from . import views

urlpatterns = [

    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('welcome/', views.welcome, name='welcome'),
    path('profile/', views.profile, name='profile'),
    path('logout/', views.logout, name='logout'),

]