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

    def clean_receiver(self):
        # Get the value of the receiver field
        receiver_username = self.cleaned_data['receiver']

        # Try to fetch the User object based on the username
        try:
            receiver_user = User.objects.get(username=receiver_username)
        except User.DoesNotExist:
            raise forms.ValidationError("User with this username does not exist.")

        # Return the User instance for further processing in the save method
        return receiver_user

    def save(self, commit=True, user=None):
        if user:
            self.instance.sender = user  # Set the sender as the logged-in user

        # Convert the receiver username to a User instance
        receiver_username = self.cleaned_data['receiver']
        try:
            receiver_user = User.objects.get(username=receiver_username)  # Get the User instance by username
            self.instance.receiver = receiver_user  # Assign the User instance to the receiver field
        except User.DoesNotExist:
            raise forms.ValidationError("User with this username does not exist.")

        # Save the instance
        return super().save(commit=commit)

