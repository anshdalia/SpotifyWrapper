# setup instructions:
when cloning project onto your own machine you will have to create and add your own Django Secret Key to the settings.py file. If you end up committing your secret key by accident to your local repo during development you can create a new branch with the --orphan setting once the secret key is removed before pushing to the git hub. Creating an orphan branch removes the commit history.

When pushing local changes to the git hub always push to a new branch and then merge to main.
