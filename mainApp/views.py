from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from SpotifyWrapper.settings import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, REDIRECT_URI
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from requests import Request, post

from user.models import UserProfile
from .util import update_or_create_user_tokens, is_spotify_authenticated


# Create your views here.

#Creates URL for Spotify Authorization
class AuthURL(APIView):
    def get(self, request, format=None):
        scopes = 'user-modify-playback-state user-read-playback-state user-read-currently-playing' # TODO change these

        url = Request('GET', 'https://accounts.spotify.com/authorize', params={
            'scope':scopes,
            'response_type': 'code',
            'redirect_uri': REDIRECT_URI,
            'client_id': SPOTIFY_CLIENT_ID,
        }).prepare().url

        return Response({'url':url}, status=status.HTTP_200_OK)

def spotify_callback(request, format=None):
    code=request.GET.get('code')
    error=request.GET.get('error') # Use this variable to see error message

    response = post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': SPOTIFY_CLIENT_ID,
        'client_secret': SPOTIFY_CLIENT_SECRET,
    }).json()

    access_token = response.get('access_token')
    token_type = response.get('token_type')
    refresh_token = response.get('refresh_token')
    expires_in = response.get('expires_in')
    error = response.get('error')

    if not request.session.exists(request.session.session_key):
        request.session.create()

    update_or_create_user_tokens(request.session.session_key, access_token, token_type, expires_in, refresh_token)

    return redirect('user:main_menu')


class IsAuthenticated(APIView):
    def get(self, request, format=None):
        is_authenticated = is_spotify_authenticated(self.request.session.session_key)
        return Response({'status': is_authenticated}, status=status.HTTP_200_OK)


@login_required(login_url='login')
def main_menu(request):
    user = request.user

    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        # If no profile exists, create a new one
        profile = UserProfile.objects.create(user=request.user)

    context = {
        'user': user,
        'user_profile': profile,
    }
    return render(request, 'main_menu.html', context)

@login_required(login_url='login')
def single_wrap(request):
    return render(request, 'single_wrap.html')

@login_required(login_url='login')
def friend_request(request):
    return render(request, 'friend_requesting.html')

@login_required(login_url='login')
def duo_wrap(request):
    return render(request, 'duo_wrap.html')


