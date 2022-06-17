"""""
Step 1: Log into Youtube
Step 2 : Get Videos from Certain playlist
Step 3 : Create Playlist on Spotify
Step 4 : Search for the song
Step 5 : Add song into spotify playlist
"""
import json
import os
from pickle import FALSE
from urllib import request
import requests
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import youtube_dl

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

f = open("data.json")
data = json.load(f)
sptfy = data["spotify"]
yt = data["installed"]

spotify_UserID = sptfy["User_ID"]
spotify_AuthToken = sptfy["OAuth_Token"]

yt_clientID = yt["client_id"]
yt_clientSecret = yt["client_secret"]

class createPlaylist:

    def __init__(self) -> None:
        self.UserID = spotify_UserID
        self.AuthToken = spotify_AuthToken
        self.youtube_client = self.get_youtube_client()
        self.all_song_info = {}

    def get_youtube_client(self):
        # Copied from YT Data API

        # Disable OAuthlib's HTTPS verification when running locally.
        # *DO NOT* leave this option enabled in production.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        api_service_name = "youtube"
        api_version = "v3"
        client_secrets_file = "data.json"

        # Get credentials and create an API client
        scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
        credentials = flow.run_console()

        # from the Youtube DATA API
        youtube_client = googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)

        return youtube_client

    def get_playlist_videos(self):
        #Use youtube API to return info on videos in the playlist
        request = self.youtube_client.videos().list(
            part="snippet,contentDetails",
            maxResults=25
            #playlistId="PLTUGlDwuzyMEtIuEOY2ClT-Idi0Bj0k2R"
        )
        response = request.execute()

        # collect each video and get important information
        for item in response["items"]:
            video_title = item["snippet"]["title"]
            youtube_url = "https://www.youtube.com/watch?v={}".format(item["id"])

            # use youtube_dl to collect the song name & artist name
            video = youtube_dl.YoutubeDL({}).extract_info(youtube_url, download=False)
            song_name = video["track"]
            artist = video["artist"]

            if song_name is not None and artist is not None:
                # append all important info in a dictionary and skip any missing song and artist
                self.all_song_info[video_title] = {
                    "youtube_url": youtube_url,
                    "song_name": song_name,
                    "artist": artist,

                    # add the uri, easy to get song to put into playlist
                    "spotify_uri": self.get_spotify_uri(song_name, artist)

                }



    def create_playlist(self):
        request_body = json.dumps(
            {
            "name": "Playlist from yt",
            "description": "Playlist containing songs saved on a playlist in yt",
            "public": True
            }
        )

        query = "https://api.spotify.com/v1/users/{}/playlists".format(self.UserID)
        response = requests.post(
            query,
            data = request_body,
            headers = {
                "Content-Type: application/json"
                "Authorization:" "Bearer {}".format(self.AuthToken)
            }
        )
        response_json = response.json()

        return response_json("id") #For getting ID of newly created playlist

    def get_spotify_uri(self): #For Searching the song in the spotify search
        query = "https://api.spotify.com/v1/search?query=track%3A{}+artist%3A{}&type=track".format(
        track,
        artist
    )
        response = requests.get(
        query,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format("spotify_token")
        }
    )
        songs = response["tracks"]["items"]
  
        url = songs[0]["uri"]
        return url

    def add_song_to_playlist(self):
        #populate the songs Dictionary
        self.get_playlist_videos()

        #Collect all of URIs
        uris = []
        for song,info in self.all_song_info.items():
            uris.append(info["spotify_uri"])

        #Create a new playlist
        playlist_id = self.create_playlist()

        
        #Add all songs into new playlist
        request_data = json.dumps(uris)

        query = "https://api.spotify.com/v1/playlists/{}/tracks".format(
            playlist_id)

        response = requests.post(
            query,
            data=request_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(spotify_AuthToken)
            }
        )

        # check for valid response status
        if response.status_code != 200:
            raise ResponseException(response.status_code)

        response_json = response.json()
        return response_json


if __name__ == '__main__':
    cp = createPlaylist()
    cp.add_song_to_playlist()

