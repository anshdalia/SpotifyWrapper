from django.shortcuts import render, redirect
from django.http import HttpResponse
from . forms import CreateUserForm, LoginForm


# Authentication models and functions
from django.contrib.auth.models import auth


# Create your views here.

def register(request):

    """
    Handle user registration by displaying and processing the registration form.

    If the request method is POST and the form is valid, the new user is created,
    and the user is redirected to the login page. Otherwise, an empty registration
    form is displayed.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse: Renders the registration page with the registration form.
    """

    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('user:login')

    context = {'registerForm':form}

    return render(request, 'register.html', context)



def login(request):

    """
    Handle user login by displaying and processing the login form.

    If the request method is POST and the form is valid, the user is authenticated
    and logged in, then redirected to the main menu. Otherwise, an empty login form
    is displayed.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse: Renders the login page with the login form.
    """

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
    """
    Display the user profile page.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse: Renders the profile page with the user's information.
    """
    context = {
        'user': request.user,
    }
    return render(request, 'profile.html', context)

def welcome(request):
    """
    Display the welcome page.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse: Renders the welcome page.
    """
    return render(request, 'welcome.html')

def logout(request):
    """
    Log out the current user and redirect to the welcome page.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse: Redirects to the welcome page after logging out.
    """
    auth.logout(request)
    return redirect('user:welcome')

def delete_account(request):
    """
    Delete the authenticated user's account after logging them out.

    If the user is authenticated, they are logged out, and their account is deleted,
    then redirected to the main menu. If the user is not authenticated, they are
    redirected to the login page.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse: Redirects to the main menu or login page based on authentication status.
    """
    if request.user.is_authenticated:
        user = request.user
        logout(request)  # Log the user out before deleting their account
        user.delete()  # Delete the user
        return redirect('main_menu')
    else:
        return redirect('user:login')  # Redirect to login if not authenticated