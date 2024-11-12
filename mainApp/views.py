from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Wrap, TopArtist, TopSong
from django.utils import timezone
from .models import DuoWrap

# Create your views here.

@login_required(login_url='login')
def main_menu(request):
    # This will render the main menu page with a profile icon, listening history, and top 5 artists
    # Currently, no Spotify API integration; just sets up the template for later use
    context = {
        'profile_icon': 'path/to/default/icon.png',  # Placeholder path for profile icon
        'listening_history': [],  # Placeholder, will be filled with minutes listened
        'top_artists': []  # Placeholder, will be filled with top 5 artists
    }
    return render(request, 'main_menu.html', context)

@login_required(login_url='login')
def single_wrap(request):
    return render(request, 'single_wrap.html')

@login_required(login_url='login')
def friend_request(request):
    return render(request, 'friend_requesting.html')

@login_required(login_url='login')
def duo_wrap(request):
    return render(request, 'duo_wrap.html')


@login_required
def single_wrap_view(request, year=None):
    # If no year specified, get the most recent wrap or default to current year
    if year is None:
        year = timezone.now().year

    # Get the wrap for the specified year, or 404 if not found
    wrap = get_object_or_404(Wrap, user=request.user, year=year)

    # Get related top artists and songs (already ordered by rank due to Meta ordering)
    top_artists = wrap.top_artists.all()
    top_songs = wrap.top_songs.all()

    context = {
        'wrap': wrap,
        'top_artists': top_artists,
        'top_songs': top_songs,
    }

    return render(request, 'single_wrap.html', context)

@login_required
def duo_wrap_view(request, duo_wrap_id):
    duo_wrap = DuoWrap.objects.get(id=duo_wrap_id)
    context = {
        'duo_wrap': duo_wrap,
        'user1_top_artists': duo_wrap.user1_top_artists,
        'user2_top_artists': duo_wrap.user2_top_artists,
        'user1_top_songs': duo_wrap.user1_top_songs,
        'user2_top_songs': duo_wrap.user2_top_songs,
        'user1_top_genre': duo_wrap.user1_top_genre,
        'user2_top_genre': duo_wrap.user2_top_genre,
        'user1_minutes_listened': duo_wrap.user1_minutes_listened,
        'user2_minutes_listened': duo_wrap.user2_minutes_listened,
    }
    return render(request, 'duo_wrap.html', context)

