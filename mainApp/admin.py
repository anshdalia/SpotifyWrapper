from django.contrib import admin

# Register your models here.
from .models import SpotifyToken

# Register the SpotifyToken model to make it accessible in Django admin
admin.site.register(SpotifyToken)