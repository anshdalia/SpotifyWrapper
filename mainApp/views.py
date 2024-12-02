import json
from django.db.models import Model
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

from . import models
from .forms import InviteFriendForm
from .models import Wrap, DuoWrap_Request
from django.db import models
from django.db.models import Q

from .models import Wrap, DuoWrap, TopArtist, TopSong
from SpotifyWrapper.settings import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, REDIRECT_URI
from .util import *
from django.contrib import messages
from datetime import datetime
from .forms import SingleWrapCreationForm
from .util import get_public_playlists
from .models import Playlist


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

    duo_wraps = DuoWrap.objects.filter(
        Q(user1=user) | Q(user2=user)
    ).order_by('-created_at')

    context = {
        'user': user,
        'spotify_token': spotify_token,
        'recent_tracks': recent_tracks,
        'top_tracks': top_tracks,
        'top_artists': top_artists,
        'user_wraps': user_wraps,  # Pass the wraps to the template
        'duo_wraps': duo_wraps,
    }

    return render(request, 'main_menu.html', context)


@login_required(login_url='user:login')
def create_new_single_wrap(request):
    if request.method == 'POST':
        form = SingleWrapCreationForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            term_type = form.cleaned_data['term_type']

            # Create the wrap based on term type
            wrap = create_wrap_for_user(request.user, name, term_type)

            # Redirect to a success page or another view
            return redirect('single_wrap_view', wrap.id)
    else:
        form = SingleWrapCreationForm()

    return render(request, 'create_new_single_wrap.html', {'form': form})
@login_required(login_url='user:login')
def single_wrap_view(request, wrap_id=None):
    """
    Displays a specific wrap for the user, identified by name.

    Args:
        request (HttpRequest): The HTTP request.
        wrap_id (int, optional): ID of the wrap to be displayed.

    Returns:
        HttpResponse: Rendered wrap page with top artists and top songs.
    """
    wrap = get_object_or_404(Wrap, id=wrap_id)
    all_too_well_times = int(wrap.minutes_listened / 10)
    context = {
        'wrap': wrap,
        'top_artists': wrap.top_artists.all(),
        'top_songs': wrap.top_songs.all(),
        'all_too_well_times': all_too_well_times,
    }
    return render(request, 'single_wrap.html', context)

@login_required
def public_wraps(request):
    """
    Displays all public wraps and Spotify playlists with like functionality.
    """
    user_wraps = Wrap.objects.filter(user=request.user)
    public_wraps = Wrap.objects.filter(public=True).exclude(user=request.user)
    liked_wraps = request.user.liked_wraps.all()

    # Spotify integration
    spotify_user_id = request.GET.get('spotify_user_id', None)
    spotify_playlists = []
    liked_playlists = Playlist.objects.filter(user=request.user)  # Assuming a Playlist model

    if spotify_user_id:
        user_token = get_user_tokens(request.user).access_token  # Ensure token is valid
        spotify_playlists = get_public_playlists(user_token, spotify_user_id)

    context = {
        'user_wraps': user_wraps,
        'public_wraps': public_wraps,
        'liked_wraps': liked_wraps,
        'liked_playlists': liked_playlists,
        'spotify_playlists': spotify_playlists,
    }
    return render(request, 'public_wraps.html', context)


@login_required
def public_wraps_view(request):
    """
    Displays the public wraps page.
    """
    user_wraps = Wrap.objects.filter(user=request.user)
    public_wraps = Wrap.objects.filter(public=True).exclude(user=request.user)
    liked_wraps = request.user.liked_wraps.all()  # Assuming a ManyToMany relationship for likes.

    context = {
        'user_wraps': user_wraps,
        'public_wraps': public_wraps,
        'liked_wraps': liked_wraps
    }
    return render(request, 'public_wraps.html', context)


@login_required
@require_http_methods(["POST"])
def share_wrap(request, wrap_id):
    """
    Marks a wrap as public and returns its details for dynamic frontend updates.
    """
    try:
        wrap = Wrap.objects.get(id=wrap_id, user=request.user)
        wrap.public = True
        wrap.save()
        return JsonResponse({
            'status': 'success',
            'wrap': {
                'id': wrap.id,
                'name': wrap.name,
                'created_at': wrap.created_at.strftime('%b %d, %Y'),
                'user': wrap.user.username
            }
        })
    except Wrap.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Wrap not found'}, status=404)



@login_required
@require_http_methods(["POST"])
def like_wrap(request, wrap_id):
    """
    Adds a like to a wrap and returns its details for dynamic frontend updates.
    """
    try:
        wrap = Wrap.objects.get(id=wrap_id)
        wrap.likes.add(request.user)
        return JsonResponse({
            'status': 'success',
            'wrap': {
                'id': wrap.id,
                'name': wrap.name,
                'user': wrap.user.username,
                'created_at': wrap.created_at.strftime('%b %d, %Y')
            }
        })
    except Wrap.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Wrap not found'}, status=404)

@login_required
@require_http_methods(["POST"])
def unlike_wrap(request, wrap_id):
    """
    Removes a like from a wrap and returns its ID for frontend updates.
    """
    try:
        wrap = Wrap.objects.get(id=wrap_id)
        wrap.likes.remove(request.user)
        return JsonResponse({'status': 'success', 'wrap_id': wrap.id})
    except Wrap.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Wrap not found'}, status=404)


@login_required
@require_http_methods(["POST"])
def like_playlist(request):
    """
    Handles liking a Spotify playlist and returns playlist details.
    """
    try:
        data = json.loads(request.body)
        playlist_id = data.get("playlist_id")
        playlist_name = data.get("playlist_name")
        playlist_url = data.get("playlist_url")

        if not playlist_id or not playlist_name or not playlist_url:
            return JsonResponse({"status": "error", "message": "Incomplete playlist data"}, status=400)

        # Create or get the playlist for the current user
        Playlist.objects.get_or_create(
            user=request.user,
            spotify_id=playlist_id,
            defaults={'name': playlist_name, 'url': playlist_url}
        )

        return JsonResponse({
            "status": "success",
            "playlist": {
                "name": playlist_name,
                "url": playlist_url,
            },
        })
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)




@login_required
@require_http_methods(["POST"])
def unshare_wrap(request, wrap_id):
    """
    Unshare a wrap by removing its public status.
    """
    try:
        wrap = Wrap.objects.get(id=wrap_id, user=request.user)
        wrap.public = False
        wrap.save()
        return JsonResponse({'status': 'success'})
    except Wrap.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Wrap not found'}, status=404)

@login_required
def liked_items_view(request):
    """
    Display wraps and Spotify playlists liked by the user.
    """
    liked_wraps = request.user.liked_wraps.all()
    liked_playlists = Playlist.objects.filter(user=request.user)

    context = {
        'liked_wraps': liked_wraps,
        'liked_playlists': liked_playlists,
    }
    return render(request, 'liked_items.html', context)


############ OLD VIEW ############

# @login_required(login_url='user:login')
# def single_wrap_view(request, wrap_id=None):
#     """
#     Displays a specific year's wrap for the user, or creates one for the current year if not specified.
#
#     Args:
#         request (HttpRequest): The HTTP request.
#         wrap_id (int, optional): ID of the wrap to be displayed.
#
#     Returns:
#         HttpResponse: Rendered wrap page with top artists and top songs for the year.
#     """
#     user = request.user
#     current_year = timezone.now().year
#     current_day = timezone.now().date()
#
#
#
#     # If no specific wrap_id is provided, look for or create the current year's wrap
#     if wrap_id is None:
#         # Attempt to get or create the current year's wrap with meaningful data
#         wrap, created = Wrap.objects.get_or_create(user=user, year=current_year, defaults={
#             'minutes_listened': 0,  # Temporary default value
#             'top_genre': 'Unknown'  # Temporary default value
#         })
#
#         # If it was created with defaults, fetch actual data
#         if created:
#             wrap = create_wrap_for_user(user)  # Populate with actual data
#
#     else:
#         wrap = get_object_or_404(Wrap, id=wrap_id, user=user)
#
#     top_artists = wrap.top_artists.all()
#     top_songs = wrap.top_songs.all()
#
#     context = {
#         'wrap': wrap,
#         'top_artists': top_artists,
#         'top_songs': top_songs,
#     }
#     return render(request, 'single_wrap.html', context)



@login_required(login_url='user:login')
def friend_request(request):
    """
    Renders the friend request page for creating a duo wrap.

    Args:
        request (HttpRequest): The HTTP request.

    Returns:
        HttpResponse: Rendered friend request page.
    """
    # Check to see if current user has any pending Duowrap_requests
    if request.method == 'POST':
        form = InviteFriendForm(request.POST)
        if form.is_valid():

            form.save(user=request.user)
            print(form.cleaned_data)
    else:
        form = InviteFriendForm()

    test = DuoWrap_Request.objects.filter(sender=request.user)
    #print(test[0].wrap_name)
    #print(test[1].wrap_name)
    #print(test[2].wrap_name)
    #print(test.last().wrap_name)
    invite_set = DuoWrap_Request.objects.filter(receiver=request.user).all()
    #print("wrap name: " + invite_set.first().wrap_name)
    context = {
        'form': form,
        'invite_set': invite_set,
    }
    return render(request, 'friend_requesting.html', context=context)

@login_required(login_url='user:login')
def act_on_friend_request(request, invite_id, accepted):
    """
    Handle friend request acceptance and create DuoWrap if accepted.
    """
    invite = get_object_or_404(DuoWrap_Request, id=invite_id, receiver=request.user)

    if accepted == 'true':
        try:
            # Use the wrap name from the invite to create the DuoWrap
            wrap_name = invite.wrap_name

            # Create or retrieve the DuoWrap
            duo_wrap, created = DuoWrap.objects.get_or_create(
                user1=invite.sender,
                user2=invite.receiver,
                wrap_name=wrap_name,
                defaults={
                    'top_artists_comparison': {},
                    'top_songs_comparison': {},
                    'top_genre_comparison': {},
                    'minutes_listened_comparison': {},
                }
            )

            if created:
                # Fetch Spotify data for both users
                sender_data = fetch_duo_wrap_data(invite.sender)
                receiver_data = fetch_duo_wrap_data(invite.receiver)

                # Populate the DuoWrap fields
                duo_wrap.top_artists_comparison = {
                    'user1': sender_data['top_artists'],
                    'user2': receiver_data['top_artists'],
                }
                duo_wrap.top_songs_comparison = {
                    'user1': sender_data['top_songs'],
                    'user2': receiver_data['top_songs'],
                }
                duo_wrap.top_genre_comparison = {
                    'user1': sender_data['top_genre'],
                    'user2': receiver_data['top_genre'],
                }
                duo_wrap.minutes_listened_comparison = {
                    'user1': sender_data['minutes_listened'],
                    'user2': receiver_data['minutes_listened'],
                }

                # Save the populated DuoWrap
                duo_wrap.save()
                messages.success(request, f"Duo Wrap '{wrap_name}' created with {invite.sender.username}!")
                return redirect('duo_wrap', duo_wrap.id)
        except Exception as e:
            messages.error(request, f"Error creating Duo Wrap: {str(e)}")
            return redirect('friend_request')

    # Delete the invite regardless of acceptance or denial
    DuoWrap_Request.objects.filter(sender=invite.sender, receiver=request.user).delete()
    return redirect('friend_request')


@login_required(login_url='user:login')
def duo_wrap_view(request, duo_wrap_id):
    """
    Display the details of a specific Duo Wrap.
    """
    duo_wrap = get_object_or_404(
        DuoWrap,
        Q(id=duo_wrap_id) & (Q(user1=request.user) | Q(user2=request.user))
    )

    context = {
        'duo_wrap': duo_wrap,
        'details': duo_wrap.get_details(),
    }
    return render(request, 'duo_wrap.html', context)

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
@require_http_methods(["DELETE"])
def delete_duo_wrap(request, duo_wrap_id):
    """
    Deletes a specified Duo Wrap for the logged-in user.

    Args:
        request (HttpRequest): The HTTP request.
        duo_wrap_id (int): The ID of the Duo Wrap to delete.

    Returns:
        JsonResponse: JSON response indicating success or failure of deletion.
    """
    try:
        # Fetch the Duo Wrap, ensuring the user is one of the participants
        duo_wrap = get_object_or_404(
            DuoWrap,
            Q(id=duo_wrap_id) & (Q(user1=request.user) | Q(user2=request.user))
        )

        # Delete the Duo Wrap
        duo_wrap.delete()
        return JsonResponse({'status': 'success'}, status=200)
    except DuoWrap.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Duo Wrap not found or not authorized to delete.'}, status=404)

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
