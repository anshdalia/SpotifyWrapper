from django.urls import path
from . import views
from .views import spotify_callback, IsAuthenticated

urlpatterns = [
    # Spotify authentication URLs
    path('get-auth-url', views.get_auth_url, name='auth_url'),
    path('redirect', spotify_callback),
    path('is-authenticated', IsAuthenticated.as_view(), name='is_authenticated'),

    # Main menu and wrap-related URLs
    path('main_menu/', views.main_menu, name='main_menu'),
    path('friend_request/', views.friend_request, name='friend_request'),
    path('act_on_friend_request/<int:invite_id>/<str:accepted>/', views.act_on_friend_request, name='act_on_friend_request'),
    path('create_new_single_wrap/', views.create_new_single_wrap, name='create_new_single_wrap'),

    # Single wrap viewing and management
    path('wrap/<int:wrap_id>/view/', views.single_wrap_view, name='wrap_view'),
    path('single_wrap/<int:wrap_id>/', views.single_wrap_view, name='single_wrap_view'),
    path('single_wrap/current/', views.single_wrap_view, name='wrap_current'),  # View the current wrap
    path('wrap/<int:wrap_id>/delete/', views.delete_wrap, name='wrap_delete'),  # Delete a single wrap

    # Duo wrap-related URLs
    path('duo_wrap/<int:duo_wrap_id>/', views.duo_wrap_view, name='duo_wrap'),
    path('duo_wrap/delete/<int:duo_wrap_id>/', views.delete_duo_wrap, name='duo_wrap_delete'),

    # Public and liked wraps
    path('public_wraps/', views.public_wraps, name='public_wraps'),
    path('liked_items/', views.liked_items_view, name='liked_items'),

    # Sharing, liking, and unliking wraps
    path('wrap/<int:wrap_id>/share/', views.share_wrap, name='share_wrap'),
    path('wrap/<int:wrap_id>/unshare/', views.unshare_wrap, name='unshare_wrap'),
    path('wrap/<int:wrap_id>/like/', views.like_wrap, name='like_wrap'),
    path('wrap/<int:wrap_id>/unlike/', views.unlike_wrap, name='unlike_wrap'),

    # Spotify playlist-related URLs
    path('spotify/like_playlist/', views.like_playlist, name='like_playlist'),

    # Contact page
    path('contact/', views.contact_view, name='contact'),
    ]
