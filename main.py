from time import sleep
from urllib import response
from dotenv import load_dotenv, find_dotenv
import requests
import base64
import json
import os
import datetime
import ftplib

load_dotenv(find_dotenv())
REFRESH_TOKEN = os.environ.get("REFRESH_TOKEN").strip()
CLIENT_ID     = os.environ.get("CLIENT_ID").strip()
CLIENT_SECRET = os.environ.get("CLIENT_SECRET").strip()
FTP_SERV      = os.environ.get("FTP_SERV").strip()
FTP_USER      = os.environ.get("FTP_USER").strip()
FTP_PASS      = os.environ.get("FTP_PASS").strip()

OAUTH_TOKEN_URL = "https://accounts.spotify.com/api/token"

def ftp_login():
    ftp = ftplib.FTP_TLS(FTP_SERV)
    ftp.login(user=FTP_USER, passwd=FTP_PASS)
    return ftp

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


def get_playlist(access_token, playlist_id):
    url     = "https://api.spotify.com/v1/playlists/%s" % playlist_id
    headers = {
       "Content-Type": "application/json",
       "Authorization": "Bearer %s" % access_token
    }
    response = requests.get(url, headers=headers)
    return response.json()

def create_playlist(access_token, name):
    #url     = "https://api.spotify.com/v1/users/lenoxfro/playlists"
    url     = "https://api.spotify.com/v1/users/31uyjhexjxswkhnqf5mlib3xx2fi/playlists"
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

def find_user(json, name):
    for user in json['users']:
        if user['name'] == name:
            return user

def update_user(json, newUser):
    for user in json['users']:
        if user['name'] == newUser['name']:
            user = newUser
            return json

def get_playlist_tracks(access_token, playlist):
    response = get_playlist(access_token, playlist)
    return response['tracks']['total']

def get_playlist_image(access_token, playlist):
    response = get_playlist(access_token, playlist)
    return response['images'][0]['url']

def main():
    if REFRESH_TOKEN is None or CLIENT_ID is None or CLIENT_SECRET is None:
        print("Environment variables have not been loaded!")
        return

    today        = datetime.date.today()
    access_token = refresh_access_token()['access_token']

    ftp          = ftp_login()
    exportFile   = open('export.json', 'wb')
    ftp.retrbinary('RETR playlists.json', exportFile.write, 1024)
    exportFile.close()

    export       = json.load(open('export.json', 'r'))

    #get all playlists to save
    f              = open('playlists.json')
    playlistConfig = json.load(f)
    for username in playlistConfig:
        playlist = playlistConfig[username]
        name     = str(today.isocalendar().year) + ' ' + playlist['prefix'] + ' ' + str(today.isocalendar().week)

        tracks    =  get_playlist(access_token, playlist['weekly'])['tracks']['items']
        tracklist = []
        for item in tracks:
            tracklist.append(item['track']['uri'])

        newPlaylistId = create_playlist(access_token, name)
        response = add_to_playlist(access_token, tracklist, newPlaylistId)

        sleep(5)

        newPlaylistObj = {
            "id": newPlaylistId,
            "name": name,
            "image": get_playlist_image(access_token, newPlaylistId),
            "week": "KW " + str(today.isocalendar().week),
            "trackCount": get_playlist_tracks(access_token, newPlaylistId)
        }
        
        user = find_user(export, username)
        user['playlists'].insert(1, newPlaylistObj)
        export = update_user(export, user)
        json.dump(export, open('export.json', 'w'))
        

        if "snapshot_id" in response:
            print("Successfully added all songs to \"" + name + "\"")
        else:
            print(response)
    
    exportFile.close()
    #upload File
    ftp.storbinary('STOR playlists.json', open('export.json', 'rb'))

main()