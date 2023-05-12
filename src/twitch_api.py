from datetime import datetime, timedelta
import os
from typing import List, NamedTuple
from dotenv import load_dotenv
import requests
from storage.mongo_connector import TWITCH_BROADCASTERS, TWITCH_TOKENS
load_dotenv();

CLIENT_ID = os.environ.get('TWITCH_CLIENT_ID')
MAX_CLIPS_PER_REQUEST = 100

class Broadcaster(NamedTuple):
  id: str
  lang: str
  login: str
  display_name: str

def call_api(url, headers, params):
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 401:
        headers["Authorization"] = get_oauth_token(force=True)
        response = requests.get(url, headers=headers, params=params)

    return response


def get_oauth_token(force: bool = False):
    # Check if there is a stored token in the database
    token_data = TWITCH_TOKENS.find_one({"type": "twitch_oauth"})

    # If a token exists and is not expired, use it
    if not force and token_data and token_data["expires_at"] > datetime.utcnow():
        return "Bearer " + token_data["access_token"]

    # If no token or expired, request a new one
    response = requests.post(
        "https://id.twitch.tv/oauth2/token",
        data={
        "client_id": CLIENT_ID,
        "client_secret": os.environ.get('TWITCH_CLIENT_SECRET'),
        "grant_type": "client_credentials"
    })

    if response.status_code == 200:
        json_data = response.json()
        access_token = "Bearer " + json_data["access_token"]
        expires_in = json_data["expires_in"]
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

        # Store the new token and its expiration time in the database
        if token_data:
            TWITCH_TOKENS.update_one({"type": "twitch_oauth"}, {"$set": {"access_token": access_token, "expires_at": expires_at}})
        else:
            TWITCH_TOKENS.insert_one({"type": "twitch_oauth", "access_token": access_token, "expires_at": expires_at})

        return access_token
    else:
        print(f"get_oauth_token - Error: {response.status_code}, {response.text}")
        return None


def get_headers():
    return {
        "Client-ID": CLIENT_ID,
        "Authorization": get_oauth_token(),
        "Accept": "application/vnd.twitchtv.v5+json"
    }

def parse_response(response: requests.Response):
    if response.status_code == 200:
        json_data = response.json()
        return json_data
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None


def get_clips_page(broadcaster_id=None, game_id=None, after=None):
    url = "https://api.twitch.tv/helix/clips"

    params = {
        "broadcaster_id": broadcaster_id,
        "game_id": game_id,
        "first": MAX_CLIPS_PER_REQUEST,
        "started_at": (datetime.utcnow() - timedelta(days=1)).isoformat() + "Z"
    }

    if after:
        params["after"] = after

    response = call_api(url, get_headers(), params)
    return parse_response(response);

# todo: refactor
def get_broadcaster(login: str) -> Broadcaster|None:
    caster_data = get_caster_by_login(login)
    if not caster_data:
        url = "https://api.twitch.tv/helix/search/channels"
        response = call_api(url, get_headers(), {"query": login})
        result = parse_response(response)
        broadcaster = None
        for caster_data in result["data"]:
            if caster_data["broadcaster_login"] == login:
                broadcaster = Broadcaster(
                    id = caster_data["id"],
                    lang = caster_data["broadcaster_language"],
                    login = caster_data["broadcaster_login"],
                    display_name = caster_data["display_name"]
                )
                store_caster(broadcaster)
                break
    else:
        broadcaster = Broadcaster(
            id = caster_data["id"],
            lang = caster_data["lang"],
            login = caster_data["login"],
            display_name = caster_data["display_name"]
        )
    return broadcaster;


def get_caster_by_login(login: str):
    return TWITCH_BROADCASTERS.find_one({"login": login})

def store_caster(caster: Broadcaster):
    TWITCH_BROADCASTERS.insert_one({
        "id": caster.id,
        'lang': caster.lang,
        "login": caster.login,
        "display_name": caster.display_name,
    })