import os

import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

SPOTIFY_CLIENT_ID = os.environ['CLIENT_ID']
SPOTIFY_CLIENT_SECRET = os.environ['CLIENT_SECRET']

BASE_API_URL = "https://api.spotify.com/v1"


def get_access_token():
    """Creates and returns new access token for spotify API"""

    resp = requests.post(
        "https://accounts.spotify.com/api/token",
        data={
            "grant_type": "client_credentials",
            "client_id": SPOTIFY_CLIENT_ID,
            "client_secret": SPOTIFY_CLIENT_SECRET
        }
    )
    token_data = resp.json()

    exp_time = datetime.now() + timedelta(seconds=token_data['expires_in'])

    return {
        "token": f"{token_data['token_type']} {token_data['access_token']}",
        "exp_time": exp_time
    }


def get_album_info(id, token):
    """Uses spotify API to get necessary data to add album to database"""

    resp = requests.get(f"{BASE_API_URL}/albums/{id}", headers={
        "Authorization": token
    })
    all_data = resp.json()

    required_data = {
        "id": id,
        "name": all_data["name"],
        "image_url": all_data["images"][0]["url"],
        "tracks": all_data["tracks"]["items"],
        "artists": [{
            'name': artist['name'],
            'id': artist['id']
        } for artist in all_data["artists"]],
    }

    return required_data


def get_all_album_info(id, token):
    """Uses spotify API to get all data on an album"""

    resp = requests.get(f"{BASE_API_URL}/albums/{id}", headers={
        "Authorization": token
    })
    all_data = resp.json()

    return all_data


def get_artist_info(id, token):
    """Uses spotify API to get all data on an artist"""

    resp = requests.get(f"{BASE_API_URL}/artists/{id}", headers={
        "Authorization": token
    })
    all_artist_data = resp.json()

    return_data = {
        'name': all_artist_data['name'],
        'image_url': all_artist_data['images'][0]['url'],
        'id': all_artist_data['id'],
        'spotify_link': all_artist_data['external_urls']['spotify'],
        'genres': all_artist_data['genres'],
    }

    return return_data


def get_artists_albums(artist_id, offset, token):
    """Uses spotify API to get albums made by a specific artist"""

    resp = requests.get(f"{BASE_API_URL}/artists/{artist_id}/albums",
                        headers={
                            "Authorization": token
                        }, params={
                            'limit': 10,
                            'offset': offset
                        })
    all_album_data = resp.json()

    album_data = [{
        'name': album['name'],
        'release_year': album['release_date'][0:4],
        'image_url': album['images'][0]['url'],
        'id': album['id']
    } for album in all_album_data['items']
        if album['total_tracks'] >= 4 and
        any(artist['id'] == artist_id for artist in album['artists'])]

    return album_data


def album_search(query, offset, token):
    """Uses spotify API to search for albums"""

    params = {
        'q': query,
        'type': 'album',
        'limit': 20,
        'offset': offset
    }

    resp = requests.get(
        f"{BASE_API_URL}/search",
        params=params,
        headers={"Authorization": token}
    )
    all_data = resp.json()

    data = [
        {
            'name': album['name'],
            'image_url': album['images'][1]['url'],
            'id': album['id'],
            'artist': album['artists'][0]['name'],
            'artist_id': album['artists'][0]['id']
        }
        for album in all_data["albums"]['items']
        if album['total_tracks'] >= 4]

    return data


def artist_search(query, offset, token):
    """Uses spotify API to search for artists"""

    params = {
        'q': query,
        'type': 'artist',
        'limit': 20,
        'offset': offset
    }

    resp = requests.get(
        f"{BASE_API_URL}/search",
        params=params,
        headers={"Authorization": token}
    )
    all_data = resp.json()

    data = [
        {
            'name': artist['name'],
            'image_url': artist['images'][0]['url'],
            'id': artist['id']
        }
        for artist in all_data["artists"]["items"]
        if artist['images']]

    return data
