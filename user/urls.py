# users/urls.py
from django.urls import path
from . import views

app_name = 'user'

urlpatterns = [

    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('welcome/', views.welcome, name='welcome'),
    path('profile/', views.profile, name='profile'),
    path('logout/', views.logout, name='logout'),
    path('delete_account/', views.delete_account, name='delete_account'),

]