import requests
import base64
import datetime

# Set up the Spotify Developer credentials
client_id = "c33d2440576744c2a3ac3a1423f23721"
client_secret = "5ca6565b86d8485d8d8ff011156d7908"
redirect_uri = "https://developer.spotify.com/dashboard"


# Redirect user to authorize the application
authorization_url = f"https://accounts.spotify.com/authorize?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&scope=user-read-recently-played"
print("Please visit the following URL to authorize the application:")
print(authorization_url)

# Handle the authorization callback and extract authorization code
authorization_code = input("Enter the authorization code from the callback URL: ")

# Exchange authorization code for access token
auth_headers = {
    "Authorization": "Basic " + base64.b64encode((client_id + ":" + client_secret).encode()).decode(),
    "Content-Type": "application/x-www-form-urlencoded"
}

auth_data = {
    "grant_type": "authorization_code",
    "code": authorization_code,
    "redirect_uri": redirect_uri
}

response = requests.post("https://accounts.spotify.com/api/token", headers=auth_headers, data=auth_data)
response_data = response.json()

# Extract the access token
access_token = response_data["access_token"]

# Make API request to get recently played songs
api_headers = {
    "Authorization": "Bearer " + access_token
}

today = datetime.datetime.now()
yesterday = today - datetime.timedelta(days=10)
yesterday_unix_timestamp = int(yesterday.timestamp()) * 1000

r = requests.get("https://api.spotify.com/v1/me/player/recently-played?after={time}".format(time=yesterday_unix_timestamp), headers = api_headers)
response_data = r.json()

# Process the response and extract relevant information
if "items" in response_data:
    for item in response_data["items"]:
        track_name = item["track"]["name"]
        artist_name = item["track"]["artists"][0]["name"]
        album_name = item["track"]["album"]["name"]
        played_at = item["played_at"]

        print("Track:", track_name)
        print("Artist:", artist_name)
        print("Album:", album_name)
        print("Played at:", played_at)
        print("------------------------------")
else:
    print("No recently played songs found.")
