from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django import forms
from django.forms.widgets import TextInput, PasswordInput, EmailInput


class CreateUserForm(UserCreationForm):
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

    username = forms.CharField(widget=TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=PasswordInput(attrs={'class': 'form-control'}))