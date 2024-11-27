from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.middleware import get_user
from django.contrib.auth.models import User
from django import forms
from django.dispatch import receiver
from django.forms.widgets import TextInput, PasswordInput, EmailInput
from .models import DuoWrap_Request

class InviteFriendForm(forms.ModelForm):
    class Meta:
        model = DuoWrap_Request
        fields = ['receiver', 'wrap_name']
        labels = {
            'receiver': 'Friend\'s Username',
        }

    receiver = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Friend's Username"
    )

    wrap_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    # Makes form.is_valid() work by converting receiver text input into a User instance
    def clean_receiver(self):
        receiver_username = self.cleaned_data['receiver']

        try:
            receiver_user = User.objects.get(username=receiver_username)
        except User.DoesNotExist:
            raise forms.ValidationError("User with this username does not exist.")

        return receiver_user

    # Sets sender field as current User automatically when making a new DuoWrap_Request
    def save(self, commit=True, user=None):
        if user:
            self.instance.sender = user

        receiver_username = self.cleaned_data['receiver']
        try:
            receiver_user = User.objects.get(username=receiver_username)
            self.instance.receiver = receiver_user
        except User.DoesNotExist:
            raise forms.ValidationError("User with this username does not exist.")

        return super().save(commit=commit)


class SingleWrapNameForm(forms.Form):
    name = forms.CharField(max_length=255, label="Wrap Name")