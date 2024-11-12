# Setup Instructions:
add the env file from discord to the project root and rename it to .env (add a period at the front). Don't leak it because 
it contains the Django secret key and we are planning on hosting publicly in the future so security is important.
Go to localhost/user/welcome to get to the welcome page

# Development:
When pushing local changes to the git hub always push to a new branch and then merge to main later.

Spotify Client ID, Client Secret, and Redirect URI variables have been added to the .env file. Add the new lines to the file for the project to work.
the database had been flushed so any old accounts will have to be remade.


# Design Mock Ups:
Here is a link to webpage design examples:
https://www.figma.com/design/dI2UZkfy02gMTxSbnOmwbe/Spotify-Wrapped?node-id=0-1&t=IOjxovrWf84rb8o9-1
