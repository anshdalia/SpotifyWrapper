from django.contrib import admin
from .models import Wrap, SpotifyToken, TopArtist, TopSong, DuoWrap

# Register the models so they appear in the Django Admin
"""
Registers the following models with the Django admin interface:

- Wrap: Represents a user's annual wrapped data, such as listening history.
- SpotifyToken: Stores access tokens for authenticating with the Spotify API.
- TopArtist: Represents a top artist in a user's wrapped data.
- TopSong: Represents a top song in a user's wrapped data.
- DuoWrap: Represents a wrap created between two users for comparison.

This registration allows the models to be viewed, added, edited, and deleted in the Django admin interface.
"""

admin.site.register(Wrap)
admin.site.register(SpotifyToken)
admin.site.register(TopArtist)
admin.site.register(TopSong)
admin.site.register(DuoWrap)
