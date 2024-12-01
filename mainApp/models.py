from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.utils import timezone


class Wrap(models.Model):
    THEME_CHOICES = [
        ('default', 'Default'),
        ('halloween', 'Halloween'),
        ('christmas', 'Christmas'),
    ]

    TERM_CHOICES = [
        ('short', 'Short-Term'),
        ('medium', 'Medium-Term'),
        ('long', 'Long-Term'),
    ]

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='wraps')
    name = models.CharField(max_length=100)
    term_type = models.CharField(max_length=10, choices=TERM_CHOICES, default='short')  # Added for term distinction
    top_artistsJSON = models.JSONField(null=True, blank=True, default=dict)
    top_songsJSON = models.JSONField(null=True, blank=True, default=dict)
    minutes_listened = models.IntegerField(default=0)
    top_genre = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default='default')

    # New fields
    public = models.BooleanField(default=False)  # For sharing wraps
    likes = models.ManyToManyField(User, related_name='liked_wraps', blank=True)  # For tracking likes

    class Meta:
        unique_together = ('user', 'name', 'term_type')  # Updated to include term type

    def __str__(self):
        return f"{self.user.username}'s Wrap: {self.name} ({self.term_type}) (Created: {self.created_at.strftime('%Y-%m-%d')})"


class SpotifyToken(models.Model):
    """
    Model to store Spotify API tokens for a user.
    
    Attributes:
        user (OneToOneField): Reference to the user associated with the token.
        created_at (DateTimeField): Timestamp for when the token was created.
        refresh_token (CharField): Token used to refresh the access token.
        access_token (CharField): Token used to access Spotify API on behalf of the user.
        expires_in (DateTimeField): Expiration date and time of the access token.
        token_type (CharField): Type of token (e.g., Bearer).
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    refresh_token = models.CharField(max_length=150)
    access_token = models.CharField(max_length=150)
    expires_in = models.DateTimeField()
    token_type = models.CharField(max_length=50)



# Not needed for single wraps anymore
class TopArtist(models.Model):
    """
    Model to store the top artists for each wrap.

    Attributes:
        wrap (ForeignKey): Reference to the associated wrap.
        name (CharField): Name of the artist.
        rank (PositiveIntegerField): Ranking of the artist.
        image_url (URLField): URL to an image of the artist.
    """
    wrap = models.ForeignKey(Wrap, on_delete=models.CASCADE, related_name='top_artists')
    name = models.CharField(max_length=200)
    rank = models.PositiveIntegerField()
    image_url = models.URLField(blank=True)

    class Meta:
        ordering = ['rank']
        unique_together = ['wrap', 'rank']

    def __str__(self):
        return f"{self.name} (Rank {self.rank})"

# Not needed for single wraps anymore
class TopSong(models.Model):
    """"
    Model to store the top songs for each wrap.

    Attributes:
        wrap (ForeignKey): Reference to the associated wrap.
        title (CharField): Title of the song.
        artist (CharField): Name of the song's artist.
        rank (PositiveIntegerField): Ranking of the song.
        image_url (URLField): URL to an image of the song cover.
    """
    wrap = models.ForeignKey(Wrap, on_delete=models.CASCADE, related_name='top_songs')
    title = models.CharField(max_length=200)
    artist = models.CharField(max_length=200)
    rank = models.PositiveIntegerField()
    image_url = models.URLField(blank=True)

    class Meta:
        ordering = ['rank']
        unique_together = ['wrap', 'rank']

    def __str__(self):
        return f"{self.title} by {self.artist} (Rank {self.rank})"


class DuoWrap(models.Model):
    user1 = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name='duo_wrap_user1'
    )
    user2 = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name='duo_wrap_user2'
    )
    wrap_name = models.CharField(max_length=100, default="Default Wrap")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    top_artists_comparison = models.JSONField(null=True, blank=True, default=dict)
    top_songs_comparison = models.JSONField(null=True, blank=True, default=dict)
    top_genre_comparison = models.JSONField(null=True, blank=True, default=dict)
    minutes_listened_comparison = models.JSONField(null=True, blank=True, default=dict)

    class Meta:
        unique_together = ('user1', 'user2', 'wrap_name')

    def __str__(self):
        return f"Duo Wrap: {self.user1.username} & {self.user2.username} ({self.wrap_name})"

    def get_top_artists_comparison(self):
        """
        Retrieve and compare top artists for both users.

        Returns:
            dict: Dictionaries containing artist comparison details.
        """
        user1_wrap = Wrap.objects.get(user=self.user1, name=self.wrap_name)
        user2_wrap = Wrap.objects.get(user=self.user2, name=self.wrap_name)

        user1_artists = user1_wrap.top_artists.all()
        user2_artists = user2_wrap.top_artists.all()

        return {
            'user1_top_artists': [
                {'name': artist.name, 'rank': artist.rank, 'image_url': artist.image_url}
                for artist in user1_artists
            ],
            'user2_top_artists': [
                {'name': artist.name, 'rank': artist.rank, 'image_url': artist.image_url}
                for artist in user2_artists
            ],
        }

    def get_top_songs_comparison(self):
        """
        Retrieve and compare top songs for both users.

        Returns:
            dict: Dictionaries containing song comparison details.
        """
        user1_wrap = Wrap.objects.get(user=self.user1, name=self.wrap_name)
        user2_wrap = Wrap.objects.get(user=self.user2, name=self.wrap_name)

        user1_songs = user1_wrap.top_songs.all()
        user2_songs = user2_wrap.top_songs.all()

        return {
            'user1_top_songs': [
                {'title': song.title, 'artist': song.artist, 'rank': song.rank, 'image_url': song.image_url}
                for song in user1_songs
            ],
            'user2_top_songs': [
                {'title': song.title, 'artist': song.artist, 'rank': song.rank, 'image_url': song.image_url}
                for song in user2_songs
            ],
        }

    def get_details(self):
        """
        Retrieve comprehensive details for the duo wrap.

        Returns:
            dict: Dictionary containing all comparison details.
        """
        return {
            'user1': self.user1,
            'user2': self.user2,
            'user1_top_artists': self.top_artists_comparison.get('user1', []),
            'user2_top_artists': self.top_artists_comparison.get('user2', []),
            'user1_top_songs': self.top_songs_comparison.get('user1', []),
            'user2_top_songs': self.top_songs_comparison.get('user2', []),
            'user1_top_genre': self.top_genre_comparison.get('user1', 'Unknown'),
            'user2_top_genre': self.top_genre_comparison.get('user2', 'Unknown'),
            'user1_minutes_listened': self.minutes_listened_comparison.get('user1', 0),
            'user2_minutes_listened': self.minutes_listened_comparison.get('user2', 0),
        }


class DuoWrap_Request(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver')
    wrap_name = models.CharField(max_length=100)
    time_sent = models.DateTimeField(auto_now_add=True)
    request_accepted = models.BooleanField(default=False) #True if receiver accepts request
    request_denied = models.BooleanField(default=False) #True if receiver denies request

class Playlist(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="liked_playlists")
    spotify_id = models.CharField(max_length=50, unique=True)  # Spotify playlist ID
    name = models.CharField(max_length=255)  # Playlist name
    url = models.URLField()  # Spotify playlist URL

    def __str__(self):
        return f"{self.name} (by {self.user.username})"