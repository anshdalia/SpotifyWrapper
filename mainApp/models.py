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
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='wraps')
    name = models.CharField(max_length=100)
    top_artistsJSON = models.JSONField(null=True, blank=True, default=dict)
    top_songsJSON = models.JSONField(null=True, blank=True, default=dict)
    song_recommendationsJSON = models.JSONField(null=True, blank=True, default=dict)
    top_genre = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default='default')

    def __str__(self):
        return f"{self.user.username}'s {self.year} Wrap"


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
    """
    Enhanced model to store a wrap comparison between two users for a specific year.

    Attributes:
        user1 (ForeignKey): First user in the comparison.
        user2 (ForeignKey): Second user in the comparison.
        year (IntegerField): The year of the duo wrap.
        created_at (DateTimeField): Timestamp for when the duo wrap was created.
    """
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='duo_wrap_user1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='duo_wrap_user2')
    year = models.IntegerField(default=timezone.now().year)
    created_at = models.DateTimeField(auto_now_add=True)
    top_artists_comparison = models.JSONField(null=True, blank=True, default=dict)
    top_songs_comparison = models.JSONField(null=True, blank=True, default=dict)
    top_genre_comparison = models.JSONField(null=True, blank=True, default=dict)
    minutes_listened_comparison = models.JSONField(null=True, blank=True, default=dict)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        unique_together = ['user1', 'user2', 'year']

    def __str__(self):
        return f"Duo Wrap: {self.user1.username} & {self.user2.username} ({self.year})"

    def get_top_artists_comparison(self):
        """
        Retrieve and compare top artists for both users.

        Returns:
            list: List of dictionaries containing artist comparison details.
        """
        user1_wrap = Wrap.objects.get(user=self.user1, year=self.year)
        user2_wrap = Wrap.objects.get(user=self.user2, year=self.year)

        user1_artists = user1_wrap.top_artists.all()
        user2_artists = user2_wrap.top_artists.all()

        return {
            'user1_top_artists': [
                {
                    'name': artist.name,
                    'rank': artist.rank,
                    'image_url': artist.image_url
                } for artist in user1_artists
            ],
            'user2_top_artists': [
                {
                    'name': artist.name,
                    'rank': artist.rank,
                    'image_url': artist.image_url
                } for artist in user2_artists
            ]
        }

    def get_top_songs_comparison(self):
        """
        Retrieve and compare top songs for both users.

        Returns:
            list: List of dictionaries containing song comparison details.
        """
        user1_wrap = Wrap.objects.get(user=self.user1, year=self.year)
        user2_wrap = Wrap.objects.get(user=self.user2, year=self.year)

        user1_songs = user1_wrap.top_songs.all()
        user2_songs = user2_wrap.top_songs.all()

        return {
            'user1_top_songs': [
                {
                    'title': song.title,
                    'artist': song.artist,
                    'rank': song.rank,
                    'image_url': song.image_url
                } for song in user1_songs
            ],
            'user2_top_songs': [
                {
                    'title': song.title,
                    'artist': song.artist,
                    'rank': song.rank,
                    'image_url': song.image_url
                } for song in user2_songs
            ]
        }

    def get_details(self):
        """
        Retrieve comprehensive details for the duo wrap.

        Returns:
            dict: Dictionary containing all comparison details.
        """
        user1_wrap = Wrap.objects.get(user=self.user1, year=self.year)
        user2_wrap = Wrap.objects.get(user=self.user2, year=self.year)

        return {
            'user1': self.user1,
            'user2': self.user2,
            'year': self.year,
            'user1_minutes_listened': user1_wrap.minutes_listened,
            'user2_minutes_listened': user2_wrap.minutes_listened,
            'user1_top_genre': user1_wrap.top_genre,
            'user2_top_genre': user2_wrap.top_genre,
            **self.get_top_artists_comparison(),
            **self.get_top_songs_comparison()
        }


class DuoWrap_Request(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver')
    wrap_name = models.CharField(max_length=100)
    time_sent = models.DateTimeField(auto_now_add=True)
    request_accepted = models.BooleanField(default=False) #True if receiver accepts request
    request_denied = models.BooleanField(default=False) #True if receiver denies request