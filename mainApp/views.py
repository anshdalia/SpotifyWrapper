from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from requests import Request, post

from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from .models import Wrap

from .models import Wrap, DuoWrap, TopArtist, TopSong
from SpotifyWrapper.settings import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, REDIRECT_URI
from .util import *
from django.contrib import messages
from datetime import datetime


# Spotify Authorization URL creation function
def get_auth_url(request):
    """
    Generates the Spotify authorization URL with required scopes and redirects the user to Spotify login.

    Args:
        request (HttpRequest): The HTTP request.

    Returns:
        HttpResponseRedirect: Redirects to the Spotify authorization page.
    """
    scopes = 'user-read-private user-top-read user-read-playback-state user-read-currently-playing user-read-recently-played'
    url = Request('GET', 'https://accounts.spotify.com/authorize', params={
        'scope': scopes,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'client_id': SPOTIFY_CLIENT_ID,
    }).prepare().url
    return redirect(url)

@login_required(login_url='user:login')
def spotify_callback(request, format=None):
    """
    Handles the Spotify authorization callback, retrieves access and refresh tokens, and saves them.

    Args:
        request (HttpRequest): The HTTP request with authorization code.

    Returns:
        HttpResponseRedirect: Redirects to the main menu after successful token retrieval.
    """
    code = request.GET.get('code')
    response = post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': SPOTIFY_CLIENT_ID,
        'client_secret': SPOTIFY_CLIENT_SECRET,
    }, headers={'Content-Type': 'application/x-www-form-urlencoded'}).json()

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
    """
    API view to check if the user is authenticated with Spotify.
    """
    def get(self, request, format=None):
        """
        Checks if the user is authenticated and has a valid Spotify token.

        Args:
            request (HttpRequest): The HTTP request.

        Returns:
            JsonResponse: JSON response indicating authentication status.
        """
        if request.user.is_authenticated: #Checks if user is logged in
            is_authenticated = is_spotify_authenticated(request)
            return JsonResponse({'status': is_authenticated}, status=status.HTTP_200_OK)
        return Response({'status': False, 'message': 'User not logged in'}, status=status.HTTP_401_UNAUTHORIZED)

@login_required(login_url='user:login')
def main_menu(request):
    """
    Renders the main menu, displaying user's Spotify data including recent tracks, top tracks, and top artists.

    Args:
        request (HttpRequest): The HTTP request.

    Returns:
        HttpResponse: Rendered main menu page with user data.
    """
    user = request.user

    # Check if authenticated and, if not, redirect to auth URL
    if not is_spotify_authenticated(request):
        return redirect('auth_url')

    spotify_token = get_user_tokens(user)

    # Fetch data from Spotify API
    recent_tracks = get_recently_played_tracks(user)
    top_tracks = get_top_items(user, item_type='tracks')
    top_artists = get_top_items(user, item_type='artists')

    # Fetch all wraps for the user
    user_wraps = Wrap.objects.filter(user=user).order_by('-created_at')

    context = {
        'user': user,
        'spotify_token': spotify_token,
        'recent_tracks': recent_tracks,
        'top_tracks': top_tracks,
        'top_artists': top_artists,
        'user_wraps': user_wraps,  # Pass the wraps to the template
    }

    return render(request, 'main_menu.html', context)

@login_required(login_url='user:login')
def single_wrap_view(request, wrap_id=None):
    """
    Displays a specific year's wrap for the user, or creates one for the current year if not specified.

    Args:
        request (HttpRequest): The HTTP request.
        wrap_id (int, optional): ID of the wrap to be displayed.

    Returns:
        HttpResponse: Rendered wrap page with top artists and top songs for the year.
    """
    user = request.user
    current_year = timezone.now().year

    # If no specific wrap_id is provided, look for or create the current year's wrap
    if wrap_id is None:
        # Attempt to get or create the current year's wrap with meaningful data
        wrap, created = Wrap.objects.get_or_create(user=user, year=current_year, defaults={
            'minutes_listened': 0,  # Temporary default value
            'top_genre': 'Unknown'  # Temporary default value
        })
        
        # If it was created with defaults, fetch actual data
        if created:
            create_wrap_for_user(user)  # Populate with actual data

    else:
        wrap = get_object_or_404(Wrap, id=wrap_id, user=user)

    top_artists = wrap.top_artists.all()
    top_songs = wrap.top_songs.all()

    context = {
        'wrap': wrap,
        'top_artists': top_artists,
        'top_songs': top_songs,
    }
    return render(request, 'single_wrap.html', context)




@login_required(login_url='user:login')
def friend_request(request):
    """
    Renders the friend request page for creating a duo wrap.

    Args:
        request (HttpRequest): The HTTP request.

    Returns:
        HttpResponse: Rendered friend request page.
    """
    return render(request, 'friend_requesting.html')

@login_required(login_url='user:login')
def duo_wrap(request):
    """
    Creates a new wrap for the user and redirects to the main menu.

    Args:
        request (HttpRequest): The HTTP request.

    Returns:
        HttpResponseRedirect: Redirects to the main menu.
    """

    # Logic to create a new wrap every time this endpoint is hit
    create_wrap_for_user(request.user)  # create new wrap on each request
    return redirect('main_menu')

@login_required
@require_http_methods(["DELETE"])
def delete_wrap(request, wrap_id):
    """
    Deletes a specified wrap for the logged-in user.

    Args:
        request (HttpRequest): The HTTP request.
        wrap_id (int): The ID of the wrap to delete.

    Returns:
        JsonResponse: JSON response indicating success or failure of deletion.
    """
    try:
        wrap = Wrap.objects.get(id=wrap_id, user=request.user)
        wrap.delete()
        return JsonResponse({'status': 'success'}, status=200)
    except Wrap.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Wrap not found'}, status=404)
    

@login_required
def contact_view(request):
    if request.method == 'POST':
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        email_from = request.user.email  # Use the logged-in user's email

        if subject and message:
            # Instead of sending an email, just print the details in the terminal
            print("Subject:", subject)
            print("Message:", message)
            print("From:", email_from)

            messages.success(request, 'Your message has been "sent" successfully.')
        else:
            messages.error(request, 'Please fill in all fields.')
    return render(request, 'contact.html')