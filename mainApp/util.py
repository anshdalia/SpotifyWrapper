import requests
from SpotifyWrapper.settings import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET
from .models import SpotifyToken
from django.utils import timezone
from datetime import timedelta

def get_user_tokens(user):
    user_tokens = SpotifyToken.objects.filter(user=user)
    if user_tokens.exists():
        print(f"Retrieved token for user {user}: {user_tokens[0].access_token}")
        return user_tokens[0]
    print(f"No token found for user {user}")
    return None

def update_or_create_user_tokens(user, access_token, token_type, expires_in, refresh_token):
    tokens = get_user_tokens(user)
    expires_in = timezone.now() + timedelta(seconds=expires_in)

    if tokens:
        tokens.access_token = access_token
        tokens.refresh_token = refresh_token
        tokens.expires_in = expires_in
        tokens.token_type = token_type
        tokens.save(update_fields=['access_token', 'refresh_token', 'expires_in', 'token_type'])
    else:
        tokens = SpotifyToken(user=user, access_token=access_token, refresh_token=refresh_token, token_type=token_type, expires_in=expires_in)
        tokens.save()

def is_spotify_authenticated(request):
    token = get_user_tokens(request.user)
    if token:
        expiry = token.expires_in
        if expiry <= timezone.now():
            print("Token expired; attempting to refresh...")
            refresh_spotify_token(token)
            token = get_user_tokens(request.user)

        if token.expires_in > timezone.now():
            print("User is authenticated with a valid token.")
            return True
    print("User not authenticated with Spotify or token expired.")
    return False

def refresh_spotify_token(token):
    refresh_token = token.refresh_token
    response = requests.post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': SPOTIFY_CLIENT_ID,
        'client_secret': SPOTIFY_CLIENT_SECRET,
    }).json()

    access_token = response.get('access_token')
    token_type = response.get('token_type')
    expires_in = response.get('expires_in')
    if access_token:
        print(f"New access token: {access_token}")
        update_or_create_user_tokens(token.user, access_token, token_type, expires_in, refresh_token)
    else:
        print("Failed to refresh token:", response)

def get_recently_played_tracks(user):
    token = get_user_tokens(user)
    if not token:
        print("No token available for user.")
        return []

    headers = {"Authorization": f"Bearer {token.access_token}"}
    params = {"limit": 50}
    response = requests.get("https://api.spotify.com/v1/me/player/recently-played", headers=headers, params=params)

    print("Request URL:", response.url)
    print("Status Code:", response.status_code)
    if response.status_code == 200:
        return response.json().get('items', [])
    print("Failed to fetch recently played tracks:", response.json())
    return []

def get_top_items(user, item_type='tracks', time_range='medium_term', limit=10):
    token = get_user_tokens(user)
    headers = {"Authorization": f"Bearer {token.access_token}"}
    params = {"time_range": time_range, "limit": limit}
    response = requests.get(f"https://api.spotify.com/v1/me/top/{item_type}", headers=headers, params=params)

    if response.status_code == 200:
        return response.json().get('items', [])
    print(f"Failed to fetch top {item_type}:", response.json())
    return []
