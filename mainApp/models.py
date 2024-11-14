from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User


class Wrap(models.Model):
    """
    Main wrap model to store a user's yearly music statistics.
    
    Attributes:
        user (ForeignKey): Reference to the user associated with the wrap.
        year (IntegerField): The year of the wrap.
        minutes_listened (IntegerField): Total minutes the user listened in the wrap year.
        top_genre (CharField): User's top genre for the year.
        created_at (DateTimeField): Timestamp for when the wrap was created.
    """
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='wraps')
    year = models.IntegerField()
    minutes_listened = models.IntegerField()
    top_genre = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'year']
        ordering = ['-year']

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
    Model to store a wrap comparison between two users for a specific year.
    
    Attributes:
        user1 (ForeignKey): First user in the comparison.
        user2 (ForeignKey): Second user in the comparison.
        year (IntegerField): The year of the duo wrap.
        top_artists_comparison (TextField): Comparison of top artists between the two users.
        top_songs_comparison (TextField): Comparison of top songs between the two users.
        top_genre_comparison (TextField): Comparison of top genres between the two users.
        minutes_listened_comparison (IntegerField): Comparison of total minutes listened between the two users.
        created_at (DateTimeField): Timestamp for when the duo wrap was created.
        updated_at (DateTimeField): Timestamp for when the duo wrap was last updated.
    """
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user2')
    year = models.IntegerField()
    top_artists_comparison = models.TextField()
    top_songs_comparison = models.TextField()
    top_genre_comparison = models.TextField()
    minutes_listened_comparison = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)