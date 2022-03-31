from urllib import response
from dotenv import load_dotenv, find_dotenv
import requests
import base64
import json
import os
import datetime

load_dotenv(find_dotenv())
REFRESH_TOKEN = os.environ.get("REFRESH_TOKEN").strip()
CLIENT_ID     = os.environ.get("CLIENT_ID").strip()
CLIENT_SECRET = os.environ.get("CLIENT_SECRET").strip()

OAUTH_TOKEN_URL = "https://accounts.spotify.com/api/token"
def refresh_access_token():
    payload        = {
        "refresh_token": REFRESH_TOKEN,
        "grant_type": "refresh_token",
        "client_id": CLIENT_ID,
    }
    encoded_client = base64.b64encode((CLIENT_ID + ":" + CLIENT_SECRET).encode('ascii'))
    headers        = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "Basic %s" % encoded_client.decode('ascii')
    }
    response = requests.post(OAUTH_TOKEN_URL, data=payload, headers=headers)
    return response.json()


def get_playlist(access_token, weekly_id):
    url     = "https://api.spotify.com/v1/playlists/%s" % weekly_id
    headers = {
       "Content-Type": "application/json",
       "Authorization": "Bearer %s" % access_token
    }
    response = requests.get(url, headers=headers)
    return response.json()

def create_playlist(access_token, name):
    url     = "https://api.spotify.com/v1/users/lenoxfro/playlists"
    payload = {
        "name": name,
        "description": name,
        "public": False
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer %s" % access_token
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers)

    return response.json()['id']

def add_to_playlist(access_token, tracklist, new_playlist):
    url     = "https://api.spotify.com/v1/playlists/%s/tracks" % new_playlist
    payload = {
        "uris" : tracklist
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer %s" % access_token
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    return response.json()


def main():
    if REFRESH_TOKEN is None or CLIENT_ID is None or CLIENT_SECRET is None:
        print("Environment variables have not been loaded!")
        return

    today        = datetime.date.today()
    access_token = refresh_access_token()['access_token']

    #get all playlists to save
    f = open('playlists.json')
    playlistConfig = json.load(f)
    for playlist in playlistConfig:
        playlist = playlistConfig[playlist]
        name     = str(today.isocalendar().year) + ' ' + playlist['prefix'] + ' ' + str(today.isocalendar().week)

        tracks    =  get_playlist(access_token, playlist['weekly'])['tracks']['items']
        tracklist = []
        for item in tracks:
            tracklist.append(item['track']['uri'])
        response = add_to_playlist(access_token, tracklist, create_playlist(access_token, name))
    
        if "snapshot_id" in response:
            print("Successfully added all songs to \"" + name + "\"")
        else:
            print(response)

main()