#!/usr/bin/env python

"""
Django's command-line utility for administrative tasks.

This script sets the default settings module for the Django application
and executes command-line instructions for managing the application.

Typical commands include starting the development server, running migrations,
and managing database schemas.
"""

"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """
    Set up the environment and run administrative tasks.

    This function sets the DJANGO_SETTINGS_MODULE environment variable to point
    to the project's settings file, then tries to import and run Django's
    execute_from_command_line function to handle the command-line arguments.
    
    Raises:
        ImportError: If Django is not installed or not found in the environment.
    """
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SpotifyWrapper.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
