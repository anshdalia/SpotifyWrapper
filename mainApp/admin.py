from django.contrib import admin
from .models import Wrap, SpotifyToken, TopArtist, TopSong, DuoWrap

# Register the models so they appear in the Django Admin
admin.site.register(Wrap)
admin.site.register(SpotifyToken)
admin.site.register(TopArtist)
admin.site.register(TopSong)
admin.site.register(DuoWrap)
