from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

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
