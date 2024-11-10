var is_authenticated;
function authenticateSpotify() {
fetch('/is-authenticated').then((response) => response.json()).then((data) => {
    is_authenticated = data.status;
    console.log(data.status) //Debug, true if authenticated
    if (!data.status) {

        fetch('/get-auth-url').then((response) => response.json()).then((data) => {
            window.location.replace(data.url);
        })
    }
})}

async function fetchProfile(token) {
    const result = await fetch("https://api.spotify.com/v1/me", {
        method: "GET", headers: { Authorization: `Bearer ${token}` }
    });
    const profile = await result.json();


    document.getElementById("displayName").innerText = profile.display_name;
    return profile;
}
