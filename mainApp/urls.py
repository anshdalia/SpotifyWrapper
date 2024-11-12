# users/urls.py
from django.urls import path
from . import views

urlpatterns = [

    path('main_menu/', views.main_menu, name='main_menu'),
    path('friend_request/', views.friend_request, name='friend_request'),
    path('duo_wrap/', views.duo_wrap, name='duo_wrap'),
    path('single_wrap/', views.single_wrap_view, name='wrap_current'),
    path('single_wrap/<int:year>/', views.single_wrap_view, name='wrap_year'),

]