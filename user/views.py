from django.shortcuts import render, redirect
from django.http import HttpResponse
from . forms import CreateUserForm, LoginForm


# Authentication models and functions
from django.contrib.auth.models import auth


# Create your views here.

def register(request):

    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('login')

    context = {'registerForm':form}

    return render(request, 'register.html', context)



def login(request):
    form = LoginForm()

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)

        if form.is_valid():
            # Gets data that user put into login page
            username = request.POST.get('username')
            password = request.POST.get('password')

            # Checks to see if inputted data is equal to a user
            user = auth.authenticate(request, username=username, password=password)

            # If user with that data exists, then login and go to main_menu
            if user is not None:
                auth.login(request, user)
                return redirect('main_menu')

    context = {'loginform':form}
    return render(request, 'login.html', context)


def profile(request):
    context = {
        'user': request.user,
    }
    return render(request, 'profile.html', context)

def welcome(request):
    return render(request, 'welcome.html')

def logout(request):
    auth.logout(request)
    return redirect('welcome')