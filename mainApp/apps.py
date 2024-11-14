from django.apps import AppConfig
"""
    Configuration for the mainApp Django application.

    This class contains metadata and configuration options for the `mainApp` application.
    It sets the default field type for auto-generated primary keys and specifies the 
    application name.
    """

class MainappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mainApp'
