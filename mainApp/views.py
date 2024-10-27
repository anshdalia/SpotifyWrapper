from django.shortcuts import render
# In views.py of your main app

# mainApp/views.py
from django.http import HttpResponse

def home(request):
    return HttpResponse("Welcome to the main app home page!")
