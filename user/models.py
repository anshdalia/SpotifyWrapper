from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class UserProfile(models.Model):

    """
    A model to store additional information about the user, specifically 
    an authentication status flag.

    Attributes:
        user: A one-to-one relationship to Django's built-in User model.
        is_authenticated: A boolean field indicating whether the user is 
                          authenticated, defaulting to False.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_authenticated = models.BooleanField(default=False)

    def __str__(self):
        """
        Returns the username of the associated User as the string representation 
        of the UserProfile instance.
        """
        return self.user.username