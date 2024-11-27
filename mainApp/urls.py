from django.urls import path
from . import views
from .views import spotify_callback, IsAuthenticated

urlpatterns = [
    path('get-auth-url', views.get_auth_url, name='auth_url'),
    path('redirect', spotify_callback),
    path('is-authenticated', IsAuthenticated.as_view()),
    path('main_menu/', views.main_menu, name='main_menu'),
    path('friend_request/', views.friend_request, name='friend_request'),
    path('duo_wrap/<int:duo_wrap_id>/', views.duo_wrap_view, name='duo_wrap'),
    path('create_new_single_wrap', views.create_new_single_wrap, name='create_new_single_wrap'),
    path('single_wrap/<int:wrap_id>/', views.single_wrap_view, name='single_wrap_view'),
    path('single_wrap/', views.single_wrap_view, name='wrap_current'),  # updated to ensure wrap_current is present
    path('single_wrap/<int:wrap_id>/', views.single_wrap_view, name='wrap_detail'),  # viewing a specific wrap
    path('wrap/<int:wrap_id>/delete/', views.delete_wrap, name='wrap_delete'),
    path('contact/', views.contact_view, name='contact'),  # New contact page URL
    path('act_on_friend_request/<int:invite_id>/<str:accepted>/', views.act_on_friend_request, name='act_on_friend_request'),
]
