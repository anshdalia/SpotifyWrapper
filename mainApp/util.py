from requests import post

from SpotifyWrapper.settings import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, REDIRECT_URI
from .models import SpotifyToken
from django.utils import timezone
from datetime import timedelta

# Returns Spotify_Token object associated with a specific user if one exists
def get_user_tokens(user):
    user_tokens = SpotifyToken.objects.filter(user=user)
    if user_tokens.exists():
        return user_tokens[0]
    else:
        return None

# Updates a Spotify_Token object with new fields or creates a new one if it does not already exist
def update_or_create_user_tokens(user, access_token, token_type, expires_in, refresh_token):
    tokens = get_user_tokens(user)

    expires_in = timezone.now() + timedelta(seconds=expires_in) # sets expires_in into an actual datetime value

    if tokens:
        tokens.access_token = access_token
        tokens.refresh_token = refresh_token
        tokens.expires_in = expires_in
        tokens.token_type = token_type
        tokens.save(update_fields=['access_token', 'refresh_token', 'expires_in', 'token_type'])
    else:
        tokens = SpotifyToken(user=user, access_token=access_token, refresh_token=refresh_token, token_type=token_type, expires_in=expires_in)
        tokens.save()

# Returns True if the current Spotify_Token object does not have an expired access_token
def is_spotify_authenticated(request):
    token = get_user_tokens(request.user)
    if token:
        expiry = token.expires_in
        if expiry <= timezone.now():
            refresh_spotify_token(token)

        return True

    return False

# Makes a call to Spotify API to get a new, valid access_token and updates the Spotify_Token
def refresh_spotify_token(token):
    refresh_token = token.refresh_token

    response = post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': SPOTIFY_CLIENT_ID,
        'client_secret': SPOTIFY_CLIENT_SECRET,
    }).json()

    access_token = response.get('access_token')
    token_type = response.get('token_type')
    expires_in = response.get('expires_in')
    if response.get('refresh_token') is not None:
        refresh_token = response.get('refresh_token')

    update_or_create_user_tokens(token.user, access_token, token_type, expires_in, refresh_token)

