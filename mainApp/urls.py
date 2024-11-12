# users/urls.py
from django.urls import path
from . import views
from .views import spotify_callback, IsAuthenticated

urlpatterns = [
    path('get-auth-url', views.get_auth_url, name='auth_url'),  # Use the function for 'auth_url'
    path('redirect', spotify_callback),
    path('is-authenticated', IsAuthenticated.as_view()),
    path('main_menu/', views.main_menu, name='main_menu'),
    path('friend_request/', views.friend_request, name='friend_request'),
    path('duo_wrap/', views.duo_wrap, name='duo_wrap'),
    path('single_wrap/', views.single_wrap_view, name='wrap_current'),
    path('single_wrap/<int:year>/', views.single_wrap_view, name='wrap_year'),

]