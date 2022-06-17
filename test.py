import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import youtube_dl
import requests
import json
spotify_token = 'BQBi4Wtsb0PP3BGrHrUM22XErGc4EN5aC0_eiuTp0fyp_OcsU2SdW1qFIoiuNRFTq3cIumPTfv9_tILRCtGvxn_ZxXrjn9DW-eJg6_3MrHZYBezqln3FKlWkBkRfMampgErxN07SV7lUoQYtjd2hU8H8PPAsWv_AhqsmDQMpIBv93RvCZy1yQ-pJDjZ72S7iXLl0qurlbNsbUuRWYfRQVOyDuu-sKW7xviis'
spotify_user_id = '11u8c4w6zt5bc55ljopa32qld'
scopes = ["https://www.googleapis.com/auth/youtube.readonly"]


def get_play():

	# Disable OAuthlib's HTTPS verification when running locally.
	# *DO NOT* leave this option enabled in production.
	os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

	api_service_name = "youtube"
	api_version = "v3"
	client_secrets_file = "data.json"

	# Get credentials and create an API client
	flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
		client_secrets_file, scopes)
	credentials = flow.run_console()
	youtube = googleapiclient.discovery.build(
		api_service_name, api_version, credentials=credentials)

	request = youtube.playlistItems().list(
		part="snippet",
		playlistId="PLvcDEv0bQcCgLS-OncIWVRlviC6vyZiju"
	)
	response = request.execute()

	return response


def extract_song_from_yt(dic):
	"""Fetch song name from Youtube"""

	url = "https://www.youtube.com/watch?v="
	info = []
	song = ""
	for i in range(len(dic["items"])):

		video_url = url+str(dic["items"][i]["snippet"]
							['resourceId']['videoId'])
		details = youtube_dl.YoutubeDL(
			{}).extract_info(video_url, download=False)
		track, artist = details['track'], details['artist']

		info.append((track, artist))
	return info


def get_spotify_uri(track, artist):
	"""Search For the Song"""

	query = "https://api.spotify.com/v1/search?\
	query=track%3A{}+artist%3A{}&type=track".format(
		track,
		artist
	)
	response = requests.get(
		query,
		headers={
			"Content-Type": "application/json",
			"Authorization": "Bearer {}".format(spotify_token)
		}
	)
	response = response.json()
	songs = response["tracks"]["items"]

	url = songs[0]["uri"]

	return url


def create_playlist():
	"""Create A New Playlist"""
	request_body = json.dumps(
		{
			"name": "My New Geeks Playlist",
			"description": "Songs",
			"public": True,
		}
	)

	query = "https://api.spotify.com/v1/users/{}/playlists".format(
		spotify_user_id)
	response = requests.post(
		query,
		data=request_body,
		headers={
			"Content-Type": "application/json",
			"Authorization": "Bearer {}".format(spotify_token),
		},
	)
	response = response.json()
	return response["id"]


def add_song(playlist_id, urls):
	"""Add all liked songs into a new Spotify playlist"""

	request_data = json.dumps(urls)

	query = "https://api.spotify.com/v1/playlists/{}/tracks".format(
		playlist_id)

	response = requests.post(
		query,
		data=request_data,
		headers={
			"Content-Type": "application/json",
			"Authorization": "Bearer {}".format(spotify_token)
		}
	)

	return "songs added successfully"


# fething data from youtube
response = get_play()

# creating spotify playlist
play_id = create_playlist()

# getting track name and artist name form yt
song_info = extract_song_from_yt(response)

# getting url for spotify songs

urls = []
for i in range(len(response['items'])):
	urls.append(get_spotify_uri(song_info[i][0], song_info[i][1]))

# adding song to new playlist
add_song(play_id, urls)
