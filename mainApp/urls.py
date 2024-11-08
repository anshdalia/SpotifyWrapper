# users/urls.py
from django.urls import path
from . import views
from .views import AuthURL, spotify_callback, IsAuthenticated

urlpatterns = [
    path('get-auth-url', AuthURL.as_view()),
    path('redirect', spotify_callback),
    path('is-authenticated', IsAuthenticated.as_view()),
    path('main_menu/', views.main_menu, name='main_menu'),
    path('single_wrap/', views.single_wrap, name='single_wrap'),
    path('friend_request/', views.friend_request, name='friend_request'),
    path('duo_wrap/', views.duo_wrap, name='duo_wrap'),

]