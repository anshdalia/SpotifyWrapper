import requests
from SpotifyWrapper.settings import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET
from .models import SpotifyToken, Wrap, TopArtist, TopSong
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

def make_spotify_request(user, endpoint, params=None):
    token = get_user_tokens(user)
    headers = {
        "Authorization": f"Bearer {token.access_token}"
    }
    url = f"https://api.spotify.com/v1{endpoint}"
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 401:
        refresh_spotify_token(token)
        token = get_user_tokens(user)
        headers["Authorization"] = f"Bearer {token.access_token}"
        response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch {endpoint}: {response.json()}")
        return None

def get_recently_played_tracks(user):
    token = get_user_tokens(user)
    if not token:
        print("No token available for user.")
        return []

    headers = {"Authorization": f"Bearer {token.access_token}"}
    params = {"limit": 10}  # Limit to 10 recent tracks if you'd like

    response = requests.get("https://api.spotify.com/v1/me/player/recently-played", headers=headers, params=params)
    
    if response.status_code == 200:
        items = response.json().get('items', [])
        recent_tracks = [
            {
                "track": {
                    "name": item['track']['name'],
                    "artists": [{"name": artist['name']} for artist in item['track']['artists']]
                }
            }
            for item in items
        ]
        return recent_tracks
    else:
        print("Failed to fetch recently played tracks:", response.json())
        return []


def fetch_minutes_listened(user):
    data = make_spotify_request(user, "/me/player/recently-played", params={"limit": 50})

    if not data:
        return 0

    total_ms = sum([item['track']['duration_ms'] for item in data['items']])
    total_minutes = total_ms / (1000 * 60)
    return int(total_minutes)

def fetch_top_genre(user):
    data = make_spotify_request(user, "/me/top/artists", params={"time_range": "medium_term", "limit": 50})

    if not data:
        return "Unknown"

    genre_count = {}
    for artist in data['items']:
        for genre in artist['genres']:
            genre_count[genre] = genre_count.get(genre, 0) + 1

    top_genre = max(genre_count, key=genre_count.get)
    return top_genre

def fetch_top_artists(user):
    data = make_spotify_request(user, "/me/top/artists", params={"time_range": "medium_term", "limit": 10})

    if not data:
        return []

    top_artists = [
        {
            "name": artist['name'],
            "image_url": artist['images'][0]['url'] if artist['images'] else ""
        }
        for artist in data['items']
    ]
    return top_artists

def fetch_top_songs(user):
    data = make_spotify_request(user, "/me/top/tracks", params={"time_range": "medium_term", "limit": 10})

    if not data:
        return []

    top_songs = [
        {
            "title": song['name'],
            "artist": ", ".join([artist['name'] for artist in song['artists']]),
            "image_url": song['album']['images'][0]['url'] if song['album']['images'] else ""
        }
        for song in data['items']
    ]
    return top_songs

def get_top_items(user, item_type='tracks', time_range='medium_term', limit=10):
    endpoint = f"/me/top/{item_type}"
    params = {"time_range": time_range, "limit": limit}
    data = make_spotify_request(user, endpoint, params)
    return data.get("items", []) if data else []

def create_wrap_for_user(user):
    current_year = timezone.now().year

    if Wrap.objects.filter(user=user, year=current_year).exists():
        return

    minutes_listened = fetch_minutes_listened(user)
    top_genre = fetch_top_genre(user)
    top_artists = fetch_top_artists(user)
    top_songs = fetch_top_songs(user)

    wrap = Wrap.objects.create(
        user=user,
        year=current_year,
        minutes_listened=minutes_listened,
        top_genre=top_genre,
    )

    for rank, artist in enumerate(top_artists, start=1):
        TopArtist.objects.create(
            wrap=wrap,
            name=artist['name'],
            rank=rank,
            image_url=artist.get('image_url', '')
        )

    for rank, song in enumerate(top_songs, start=1):
        TopSong.objects.create(
            wrap=wrap,
            title=song['title'],
            artist=song['artist'],
            rank=rank,
            image_url=song.get('image_url', '')
        )

    return wrap
