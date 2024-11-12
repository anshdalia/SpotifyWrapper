from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Wrap, TopArtist, TopSong
from django.utils import timezone
from .models import DuoWrap
from SpotifyWrapper.settings import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, REDIRECT_URI
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from requests import Request, post

from user.models import UserProfile
from .util import *


# Spotify Authorization URL creation function
def get_auth_url(request):
    scopes = 'user-read-private user-top-read user-read-playback-state user-read-currently-playing user-read-recently-played'
    url = Request('GET', 'https://accounts.spotify.com/authorize', params={
        'scope': scopes,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'client_id': SPOTIFY_CLIENT_ID,
    }).prepare().url

    # Redirect user to the Spotify authorization URL
    return redirect(url)


@login_required(login_url='user:login')
def spotify_callback(request, format=None):
    code = request.GET.get('code')
    response = post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': SPOTIFY_CLIENT_ID,
        'client_secret': SPOTIFY_CLIENT_SECRET,
    },
    headers={'Content-Type': 'application/x-www-form-urlencoded'}).json()

    access_token = response.get('access_token')
    token_type = response.get('token_type')
    refresh_token = response.get('refresh_token')
    expires_in = response.get('expires_in')
    error = response.get('error')

    if error:
        return JsonResponse({'error': error}, status=status.HTTP_400_BAD_REQUEST)

    update_or_create_user_tokens(request.user, access_token, token_type, expires_in, refresh_token)
    return redirect('main_menu')


class IsAuthenticated(APIView):
    def get(self, request, format=None):
        if request.user.is_authenticated:
            is_authenticated = is_spotify_authenticated(request)
            return JsonResponse({'status': is_authenticated}, status=status.HTTP_200_OK)
        return Response({'status': False, 'message': 'User not logged in'}, status=status.HTTP_401_UNAUTHORIZED)


@login_required(login_url='user:login')
def main_menu(request):
    user = request.user

    # Check if authenticated and, if not, redirect to auth URL
    if not is_spotify_authenticated(request):
        return redirect('auth_url')

    spotify_token = get_user_tokens(user)
    print(f"Access token in main_menu for user {user}: {spotify_token.access_token if spotify_token else 'No token'}")

    # Fetch data from Spotify API
    recent_tracks = get_recently_played_tracks(user)
    top_tracks = get_top_items(user, item_type='tracks')
    top_artists = get_top_items(user, item_type='artists')

    context = {
        'user': user,
        'spotify_token': spotify_token,
        'recent_tracks': recent_tracks,
        'top_tracks': top_tracks,
        'top_artists': top_artists,
    }

    print("Recent Tracks:", recent_tracks)
    return render(request, 'main_menu.html', context)


@login_required(login_url='user:login')
def single_wrap(request):
    return render(request, 'single_wrap.html')


@login_required(login_url='user:login')
def friend_request(request):
    return render(request, 'friend_requesting.html')


@login_required(login_url='user:login')
def duo_wrap(request):
    return render(request, 'duo_wrap.html')


@login_required
def single_wrap_view(request, year=None):
    # If no year specified, get the most recent wrap or default to current year
    if year is None:
        year = timezone.now().year

    # Get the wrap for the specified year, or 404 if not found
    wrap = get_object_or_404(Wrap, user=request.user, year=year)

    # Get related top artists and songs (already ordered by rank due to Meta ordering)
    top_artists = wrap.top_artists.all()
    top_songs = wrap.top_songs.all()

    context = {
        'wrap': wrap,
        'top_artists': top_artists,
        'top_songs': top_songs,
    }

    return render(request, 'single_wrap.html', context)

@login_required
def duo_wrap_view(request, duo_wrap_id):
    duo_wrap = DuoWrap.objects.get(id=duo_wrap_id)
    context = {
        'duo_wrap': duo_wrap,
        'user1_top_artists': duo_wrap.user1_top_artists,
        'user2_top_artists': duo_wrap.user2_top_artists,
        'user1_top_songs': duo_wrap.user1_top_songs,
        'user2_top_songs': duo_wrap.user2_top_songs,
        'user1_top_genre': duo_wrap.user1_top_genre,
        'user2_top_genre': duo_wrap.user2_top_genre,
        'user1_minutes_listened': duo_wrap.user1_minutes_listened,
        'user2_minutes_listened': duo_wrap.user2_minutes_listened,
    }
    return render(request, 'duo_wrap.html', context)

