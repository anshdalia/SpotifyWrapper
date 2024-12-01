import requests
from SpotifyWrapper.settings import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET
from .models import SpotifyToken, Wrap, TopArtist, TopSong
from django.utils import timezone
from datetime import timedelta

def get_user_tokens(user):
    """
    Retrieves the Spotify token for a given user.

    Args:
        user (User): The user whose token is to be retrieved.

    Returns:
        SpotifyToken: The Spotify token associated with the user, or None if no token is found.
    """
    user_tokens = SpotifyToken.objects.filter(user=user)
    if user_tokens.exists():
        print(f"Retrieved token for user {user}: {user_tokens[0].access_token}")
        return user_tokens[0]
    print(f"No token found for user {user}")
    return None

def update_or_create_user_tokens(user, access_token, token_type, expires_in, refresh_token):
    """
    Updates or creates a Spotify token for the given user.

    Args:
        user (User): The user for whom the token is created or updated.
        access_token (str): The access token.
        token_type (str): The type of token.
        expires_in (int): Token expiry time in seconds.
        refresh_token (str): The refresh token.
    """
    tokens = get_user_tokens(user)
    expires_in = timezone.now() + timedelta(seconds=expires_in)
    print("update_or_create_user_tokens is called:")
    if tokens:
        print(f"Token exists for user {user}, updating token")
        print(f"Old Access Token: {tokens.access_token}")
        print(f"New Access Token: {access_token}")
        tokens.access_token = access_token
        tokens.refresh_token = refresh_token
        tokens.expires_in = expires_in
        tokens.token_type = token_type
        tokens.save(update_fields=['access_token', 'refresh_token', 'expires_in', 'token_type'])
    else:
        print(f"No tokens found for user {user}, creating new token for user")
        tokens = SpotifyToken(user=user, access_token=access_token, refresh_token=refresh_token, token_type=token_type, expires_in=expires_in)
        tokens.save()

def is_spotify_authenticated(request):
    """
    Checks if the Spotify token for the user associated with the request is valid.

    Args:
        request (HttpRequest): The HTTP request containing the user to be authenticated.

    Returns:
        bool: True if the user has a valid Spotify token, False otherwise.
    """
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
    """
    Refreshes the Spotify access token using the refresh token.

    Args:
        token (SpotifyToken): The Spotify token to be refreshed.
    """
    refresh_token = token.refresh_token
    print("Before refresh: token.refresh_token=" + refresh_token)
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

def make_spotify_request(user, endpoint, params):
    """
    Makes a request to the Spotify API on behalf of a user.

    Args:
        user (User): The user for whom the request is being made.
        endpoint (str): The Spotify API endpoint.
        params (dict, optional): Query parameters for the request.

    Returns:
        dict or None: The JSON response from the API, or None if the request failed.
    """
    token = get_user_tokens(user)
    headers = {
        "Authorization": f"Bearer {token.access_token}"
    }
    url = f"https://api.spotify.com/v1{endpoint}"
    print(url)
    response = requests.get(url, headers=headers, params=params)
    print(response.status_code)
    if response.status_code == 401 or response.status_code == 403 or response.status_code == 404:
        refresh_spotify_token(token)
        newToken = get_user_tokens(user)
        print(f"New access token: {newToken.access_token}")
        headers["Authorization"] = f"Bearer {newToken.access_token}"
        print(f"Authorization: {headers.get('Authorization')}")
        response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch " + str(response.status_code)) #{endpoint}: {response.json()}")
        return None


# Generates song recommendations based off of top genres for either 1 or 2 users
def get_recommendations(user1, user2):
    top_genres = fetch_top_genre(user1)

    # Will find recommendations for 2 users if a second user is specified
    if user2:
        top_genres = {top_genres, fetch_top_genre(user2)}

    print(f"fetching song recommendations with genre: " + top_genres)
    data = make_spotify_request(user1, "/recommendations", params={"limit": 10, "seed_genres": top_genres})

    if not data:
        print('song recommendations not found')
        return []

    print(data)
    song_recommendations = [
        {
            "title": song['name'],
            "artist": ", ".join([artist['name'] for artist in song['artists']]),
            "image_url": song['album']['images'][0]['url'] if song['album']['images'] else "",
            "preview_url": song.get('preview_url')  # Add preview URL for playback
        }
        for song in data['tracks']
    ]
    return song_recommendations

def get_recently_played_tracks(user):
    """
    Retrieves the user's recently played tracks from Spotify.

    Args:
        user (User): The user whose recently played tracks are retrieved.

    Returns:
        list: A list of recently played tracks, each containing track details.
    """
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
        #print("Failed to fetch recently played tracks:", response.json())
        return []



#NOTICE: THIS METHOD DOES NOT WORK AS INTENDED
def fetch_minutes_listened(user, time_range='medium_term'):
    """
    Estimates total minutes listened by summing up the duration of the user's top tracks.

    Args:
        user (User): The user whose minutes listened are estimated.
        time_range (str): The Spotify API's time range ('short_term', 'medium_term', 'long_term').

    Returns:
        int: The estimated total minutes listened.
    """
    data = make_spotify_request(user, "/me/top/tracks", params={"time_range": time_range, "limit": 50})
    if not data:
        return 0

    total_ms = sum([track['duration_ms'] for track in data['items']])
    total_minutes = total_ms / (1000 * 60)  # Convert milliseconds to minutes
    return int(total_minutes)



def fetch_top_genre(user, time_range='medium_term'):
    """
    Fetches the user's top genre based on the specified time range.

    Args:
        user (User): The user whose top genre is fetched.
        time_range (str): The Spotify API's time range ('short_term', 'medium_term', 'long_term').

    Returns:
        str: The user's most frequently occurring genre.
    """
    data = make_spotify_request(user, "/me/top/artists", params={"time_range": time_range, "limit": 25})
    if not data:
        return "Unknown"

    genre_count = {}
    for artist in data['items']:
        for genre in artist['genres']:
            genre_count[genre] = genre_count.get(genre, 0) + 1

    return max(genre_count, key=genre_count.get) if genre_count else "Unknown"

def fetch_top_artists(user, time_range='medium_term'):
    """
    Fetches the user's top artists based on the specified time range.

    Args:
        user (User): The user whose top artists are fetched.
        time_range (str): The Spotify API's time range ('short_term', 'medium_term', 'long_term').

    Returns:
        list: A list of top artists with names and image URLs.
    """
    data = make_spotify_request(user, "/me/top/artists", params={"time_range": time_range, "limit": 10})
    if not data:
        return []

    return [
        {
            "name": artist['name'],
            "image_url": artist['images'][0]['url'] if artist['images'] else ""
        }
        for artist in data['items']
    ]


def fetch_top_songs(user, time_range='medium_term'):
    """
    Fetches the user's top songs based on the specified time range.

    Args:
        user (User): The user whose top songs are fetched.
        time_range (str): The Spotify API's time range ('short_term', 'medium_term', 'long_term').

    Returns:
        list: A list of top songs with title, artist, image URL, and preview URL.
    """
    data = make_spotify_request(user, "/me/top/tracks", params={"time_range": time_range, "limit": 10})
    if not data:
        return []

    return [
        {
            "title": song['name'],
            "artist": ", ".join([artist['name'] for artist in song['artists']]),
            "image_url": song['album']['images'][0]['url'] if song['album']['images'] else "",
            "preview_url": song.get('preview_url')  # Add preview URL for playback
        }
        for song in data['items']
    ]

def get_top_items(user, item_type='tracks', time_range='medium_term', limit=10):
    """
    Retrieves the user's top items (tracks or artists) based on a specified time range and limit.

    Args:
        user (User): The user whose top items are fetched.
        item_type (str): Type of items to retrieve ('tracks' or 'artists').
        time_range (str): Time range for the data ('short_term', 'medium_term', 'long_term').
        limit (int): Number of items to fetch.

    Returns:
        list: A list of top items, or an empty list if the request fails.
    """
    endpoint = f"/me/top/{item_type}"
    params = {"time_range": time_range, "limit": limit}
    data = make_spotify_request(user, endpoint, params)
    return data.get("items", []) if data else []

def create_wrap_for_user(user, name, term_type):
    # Ensure the Wrap includes term_type as part of the unique combination
    wrap, created = Wrap.objects.get_or_create(user=user, name=name, term_type=term_type)

    # Fetch Spotify data based on the term type
    time_range = 'short_term' if term_type == 'short' else 'medium_term' if term_type == 'medium' else 'long_term'

    top_genre = fetch_top_genre(user, time_range)
    top_artists = fetch_top_artists(user, time_range)
    top_songs = fetch_top_songs(user, time_range)
    minutes_listened = fetch_minutes_listened(user, time_range)

    # Save fetched data to the Wrap instance
    wrap.top_genre = top_genre
    wrap.top_artistsJSON = top_artists
    wrap.top_songsJSON = top_songs
    wrap.minutes_listened = minutes_listened
    wrap.save()

    return wrap


def fetch_duo_wrap_data(user):
    """
    Fetches fresh Spotify data for a user to populate a Duo Wrap.

    Args:
        user (User): The user whose data is fetched.

    Returns:
        dict: A dictionary containing the user's top genre, top artists, top songs, and minutes listened.
    """
    return {
        'top_genre': fetch_top_genre(user),
        'top_artists': fetch_top_artists(user),
        'top_songs': fetch_top_songs(user),
        'minutes_listened': fetch_minutes_listened(user)
    }
def get_public_playlists(user_token, user_id):
    """
    Fetches public playlists for a specific Spotify user.

    Args:
        user_token (str): The Spotify access token.
        user_id (str): The Spotify user ID.

    Returns:
        list: A list of public playlists, or an empty list if no playlists are found.
    """
    url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
    headers = {
        "Authorization": f"Bearer {user_token}"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors

        data = response.json()
        if "items" in data and data["items"] is not None:
            return data["items"]  # Return the playlists
        else:
            return []  # Return an empty list if no items are found

    except requests.exceptions.RequestException as e:
        print(f"Error fetching public playlists: {e}")
        return []  # Return an empty list in case of an error


############ OLD CREATE WRAP METHOD ############
# def create_wrap_for_user(user):
#     """
#     Creates or updates a user's yearly wrap with their Spotify data.
#
#     Args:
#         user (User): The user for whom the wrap is created or updated.
#
#     Returns:
#         Wrap: The user's wrap instance containing music statistics.
#     """
#     current_year = timezone.now().year
#
#     # Try to get the existing wrap for the year, or create a new one if it doesn’t exist
#     wrap, created = Wrap.objects.get_or_create(user=user, year=current_year)
#
#     # Fetch data
#     minutes_listened = fetch_minutes_listened(user)
#     top_genre = fetch_top_genre(user)
#     top_artists = fetch_top_artists(user)
#     top_songs = fetch_top_songs(user)
#
#     print(f"{'Creating' if created else 'Updating'} wrap for {user} - Year: {current_year}")
#     print(f"Minutes Listened: {minutes_listened}, Top Genre: {top_genre}")
#     print(f"Top Artists: {top_artists}")
#     print(f"Top Songs: {top_songs}")
#
#     # Update wrap data
#     wrap.minutes_listened = minutes_listened
#     wrap.top_genre = top_genre
#     wrap.save()
#     print("wrap top genre: " + wrap.top_genre)
#     # Clear previous TopArtist and TopSong records for this wrap if updating
#     if not created:
#         wrap.top_artists.all().delete()
#         wrap.top_songs.all().delete()
#
#     # Create TopArtist entries
#     for rank, artist in enumerate(top_artists, start=1):
#         print(f"Saving artist {artist['name']} at rank {rank}")
#         TopArtist.objects.create(
#             wrap=wrap,
#             name=artist['name'],
#             rank=rank,
#             image_url=artist.get('image_url', '')
#         )
#
#     # Create TopSong entries
#     for rank, song in enumerate(top_songs, start=1):
#         print(f"Saving song {song['title']} by {song['artist']} at rank {rank}")
#         TopSong.objects.create(
#             wrap=wrap,
#             title=song['title'],
#             artist=song['artist'],
#             rank=rank,
#             image_url=song.get('image_url', '')
#         )
#
#     return wrap
