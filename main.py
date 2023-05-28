import requests
import base64
import datetime
import sqlalchemy
import sqlite3
import pandas as pd

# Set up the Spotify Developer credentials
CLIENT_ID = "c33d2440576744c2a3ac3a1423f23721"
CLIENT_SECRET = "5ca6565b86d8485d8d8ff011156d7908"
REDIRECT_IRI = "https://developer.spotify.com/dashboard"

DATABASE_LOCATION = "sqlite:///my_played_tracks.sqlite"

#Data validation function
def check_if_valid_data(df: pd.DataFrame) -> bool:
    # Check if dataframe is empty
    if df.empty:
        print("No songs downloaded. Finishing execution")
        return False

    # Primary Key Check
    if pd.Series(df['played_at']).is_unique:
        pass
    else:
        raise Exception("Primary Key check is violated")

    # Check for nulls
    if df.isnull().values.any():
        raise Exception("Null values found")


    return True

# Redirect user to authorize the application
authorization_url = f"https://accounts.spotify.com/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_IRI}&scope=user-read-recently-played"
print("Please visit the following URL to authorize the application:")
print(authorization_url)

# Handle the authorization callback and extract authorization code
authorization_code = input("Enter the authorization code from the callback URL: ")

# Exchange authorization code for access token
auth_headers = {
    "Authorization": "Basic " + base64.b64encode((CLIENT_ID + ":" + CLIENT_SECRET).encode()).decode(),
    "Content-Type": "application/x-www-form-urlencoded"
}

auth_data = {
    "grant_type": "authorization_code",
    "code": authorization_code,
    "redirect_uri": REDIRECT_IRI,
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
timeframe = today - datetime.timedelta(days=10)
timeframe_unix_timestamp = int(timeframe.timestamp()) * 1000

r = requests.get("https://api.spotify.com/v1/me/player/recently-played?after={time}".format(time=timeframe_unix_timestamp), headers = api_headers)
response_data = r.json()

song_names = []
artist_names = []
played_at_list = []
timestamps = []

# Extracting only the relevant bits of data from the json object
for song in response_data["items"]:
    song_names.append(song["track"]["name"])
    artist_names.append(song["track"]["album"]["artists"][0]["name"])
    played_at_list.append(song["played_at"])
    timestamps.append(song["played_at"][0:10])

# Prepare a dictionary in order to turn it into a pandas dataframe below
song_dict = {
    "song_name": song_names,
    "artist_name": artist_names,
    "played_at": played_at_list,
    "timestamp": timestamps
}

#Create a Pandas dateframe
song_df = pd.DataFrame(song_dict, columns = ["song_name", "artist_name", "played_at", "timestamp"])
pd.set_option('display.max_columns', 20)
pd.set_option('display.width', 2000)


#Validate
if check_if_valid_data(song_df):
        print("Data valid, proceed to Load stage")


#Loading DF to SQLite

engine = sqlalchemy.create_engine(DATABASE_LOCATION)
conn = sqlite3.connect('my_played_tracks.sqlite')
cursor = conn.cursor()

sql_query = """
    CREATE TABLE IF NOT EXISTS my_played_tracks(
        song_name VARCHAR(200),
        artist_name VARCHAR(200),
        played_at VARCHAR(200),
        timestamp VARCHAR(200),
        CONSTRAINT primary_key_constraint PRIMARY KEY (played_at)
    )
    """

cursor.execute(sql_query)

try:
    song_df.to_sql("my_played_tracks", engine, index=False, if_exists='append')
except:
    print("Data already exists in the database")

conn.close()

