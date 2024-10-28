# mainApp/views.py
from django.shortcuts import render

def home(request):
    # Placeholder for main app's homepage, if separate from main menu
    return render(request, 'mainApp/home.html')

def main_menu(request):
    # This will render the main menu page with a profile icon, listening history, and top 5 artists
    # Currently, no Spotify API integration; just sets up the template for later use
    context = {
        'profile_icon': 'path/to/default/icon.png',  # Placeholder path for profile icon
        'listening_history': [],  # Placeholder, will be filled with minutes listened
        'top_artists': []  # Placeholder, will be filled with top 5 artists
    }
    return render(request, 'mainApp/main_menu.html', context)
