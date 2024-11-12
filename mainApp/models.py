from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User


class Wrap(models.Model):
    """Main wrap model to store user's yearly music statistics"""
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
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    refresh_token = models.CharField(max_length=150)
    access_token = models.CharField(max_length=150)
    expires_in = models.DateTimeField()
    token_type = models.CharField(max_length=50)

class TopArtist(models.Model):
    """Store top artists for each wrap"""
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
    """Store top songs for each wrap"""
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
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user2')
    year = models.IntegerField()
    top_artists_comparison = models.TextField()
    top_songs_comparison = models.TextField()
    top_genre_comparison = models.TextField()
    minutes_listened_comparison = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)