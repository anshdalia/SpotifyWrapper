from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django import forms
from django.forms.widgets import TextInput, PasswordInput, EmailInput


class CreateUserForm(UserCreationForm):

    """
    A form for creating new users. Extends Django's UserCreationForm to include fields 
    for first name, last name, username, email, and password with custom form controls.

    Fields:
        - first_name: Required field for user's first name.
        - last_name: Required field for user's last name.
        - username: Required field for unique username.
        - email: Required field for user's email address.
        - password1: Required field for user's password.
        - password2: Required field for confirming user's password.

    Meta:
        model: Specifies the User model associated with this form.
        fields: Lists the fields to include in the form, namely first name, last name, 
                username, email, password1, and password2.
    """
    first_name = forms.CharField(
        required=True,
        widget=TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        required=True,
        widget=TextInput(attrs={'class': 'form-control'})
    )
    username = forms.CharField(
        required=True,
        widget=TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        required=True,
        widget=EmailInput(attrs={'class': 'form-control'})
    )
    password1 = forms.CharField(
        required=True,
        widget=PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        required=True,
        widget=PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2')


class LoginForm(AuthenticationForm):

    """
    A form for authenticating users. Extends Django's AuthenticationForm to include 
    username and password fields with custom form controls.

    Fields:
        - username: Required field for user's username, displayed as a text input with custom styling.
        - password: Required field for user's password, displayed as a password input with custom styling.
    """
    username = forms.CharField(widget=TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=PasswordInput(attrs={'class': 'form-control'}))