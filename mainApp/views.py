from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from SpotifyWrapper.settings import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, REDIRECT_URI
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from requests import Request, post

from user.models import UserProfile
from .util import *


# Create your views here.

#Creates URL for Spotify Authorization
class AuthURL(APIView):
    def get(self, request, format=None):
        scopes = 'user-read-private user-top-read user-read-playback-state user-read-currently-playing' # TODO change scopes to what we need
        print("AuthURL is initialized")
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
    },
    headers={
        'Content-Type': 'application/x-www-form-urlencoded'
    }
                    ).json()

    access_token = response.get('access_token')
    token_type = response.get('token_type')
    refresh_token = response.get('refresh_token')
    expires_in = response.get('expires_in')
    error = response.get('error')


    update_or_create_user_tokens(request.user, access_token, token_type, expires_in, refresh_token)

    return redirect('main_menu')

# Checks if user is logged in and authenticated with spotify
class IsAuthenticated(APIView):
    def get(self, request, format=None):
        if request.user.is_authenticated:
            is_authenticated = is_spotify_authenticated(request)

            return JsonResponse({'status': is_authenticated}, status=status.HTTP_200_OK)
        else:
            return Response({'status': False, 'message': 'User not logged in'}, status=status.HTTP_401_UNAUTHORIZED)


@login_required(login_url='user:login')
def main_menu(request):
    user = request.user
    spotify_token = get_user_tokens(user)

    context = {
        'user': user,
        'spotify_token': spotify_token,
    }
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


