//This file is currently not used as authenticateSpotify function has been written directly into html template main_menu
function authenticateSpotify() {
    fetch('/spotify/is-authenticated').then((response) => response.json()).then((data) => {
        this.setState({spotifyAuthenticated: data.status});
        if (!data.status) {
            fetch('/spotify/get-auth-url').then((response) => response.json()).then((data) => {
                window.location.replace(data.url);
            })
        }
    })

}

