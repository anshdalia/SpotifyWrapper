var is_authenticated;

/**
 * Checks if the user is authenticated with Spotify and redirects to the authentication URL if not.
 */
function authenticateSpotify() {
    fetch('/is-authenticated').then((response) => response.json()).then((data) => {
        is_authenticated = data.status;
        //console.log("Is user authenticated:", data.status); // Debug, true if authenticated
        if (!data.status) {
            fetch('/get-auth-url').then((response) => response.json()).then((data) => {
                window.location.replace(data.url);
            });
        }
    });
}

/**
 * Fetches the user's Spotify profile information using an access token.
 *
 * @param {string} token - The Spotify access token.
 * @returns {Promise<Object|undefined>} The profile data if fetched successfully, otherwise undefined.
 */

async function fetchProfile(token) {
    try {
        //console.log("Token received in fetchProfile:", token); // Debug: Check token received

        const result = await fetch("https://api.spotify.com/v1/me", {
            method: "GET",
            headers: { Authorization: `Bearer ${token}` }
        });

        // Check for response errors
        if (!result.ok) {
            console.error("Error in fetchProfile response:", result.status, result.statusText);
            const contentType = result.headers.get("content-type");
            
            // Check if the response is JSON
            if (contentType && contentType.includes("application/json")) {
                const errorResponse = await result.json();
                console.error("Error details (JSON):", errorResponse); // Log JSON error details
            } else {
                const errorText = await result.text();
                console.error("Error details (Text):", errorText); // Log non-JSON error details
            }
            return;
        }

        // Parse the profile data
        const profile = await result.json();
        //console.log("Profile data received:", profile); // Debug: print profile data

        document.getElementById("displayName").innerText = profile.display_name || "No display name found";
        return profile;
    } catch (error) {
        //console.error("Error fetching profile:", error); // Debug: log fetch error
    }
}

/**
 * Sends a request to the Spotify Web API with specified parameters.
 *
 * @param {string} endpoint - The Spotify API endpoint to call.
 * @param {string} method - The HTTP method to use (e.g., "GET", "POST").
 * @param {Object} body - The request body, if any.
 * @param {string} token - The Spotify access token for authorization.
 * @returns {Promise<Object>} The JSON response from the Spotify API.
 */

async function fetchWebApi(endpoint, method, body, token) {
    const res = await fetch(`https://api.spotify.com/${endpoint}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
    method,
    body:JSON.stringify(body)
    });
    return await res.json();
}

async function getTopTracks(token){
  // Endpoint reference : https://developer.spotify.com/documentation/web-api/reference/get-users-top-artists-and-tracks
  return (await fetchWebApi(
    'v1/me/top/tracks?time_range=long_term&limit=5', 'GET', token
  )).items;
}



