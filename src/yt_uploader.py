import json
import os
import sys
from typing import NamedTuple,List
import google_auth_oauthlib
import googleapiclient.discovery
import googleapiclient.errors
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from storage.mongo_connector import YT_TOKENS
from storage.clip_storage import Clip, get_clips_to_upload, set_error, set_uploaded
from googleapiclient.discovery import build


class DbTokenInfo(NamedTuple):
    access_token: str
    refresh_token: str
    scope: List[str]
    token_type: str
    expires_in: int
    expires_at: float

class YtCredentials(NamedTuple):
    token: str
    refresh_token: str
    token_uri: str
    client_id: str
    client_secret: str
    scopes: List[str]

def get_credentail_object_from_token_info(token_info: DbTokenInfo) -> Credentials:
    yt_secrets = json.load(open("yt_secrets.json", "r"))
    return Credentials.from_authorized_user_info(info={
        **token_info._asdict(),
        "client_id": yt_secrets["installed"]["client_id"],
        "client_secret": yt_secrets["installed"]["client_secret"]
    }, scopes=token_info.scope)

def update_db_token(token_info: DbTokenInfo):
    YT_TOKENS.update_one(
        {"_id": "token"},
        {"$set": {"credentials": token_info._asdict()}},
        upsert=True
    )

def authenticate():
    scopes = ["https://www.googleapis.com/auth/youtube.upload"]
    credentials = None
    db_token_info = None

    # Load the stored credentials from MongoDB
    token_doc = YT_TOKENS.find_one({"_id": "token"})

    if token_doc:
        db_token_info = DbTokenInfo(**token_doc['credentials'])
        credentials = get_credentail_object_from_token_info(db_token_info)

    if not credentials or not credentials.valid:
        print('token not valid')

        # refresh token
        if credentials and credentials.expired and credentials.refresh_token and db_token_info:
            print('token expired - refreshing...')
            credentials.refresh(Request())
            update_db_token(db_token_info._replace(refresh_token=credentials.refresh_token))#todo: expiry update
        # get fresh token
        else:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                "yt_secrets.json", scopes, redirect_uri="http://localhost")

            auth_url, _ = flow.authorization_url(prompt='consent', include_granted_scopes='true')
            print('Please go to this URL and authorize the application:', auth_url)
            code = input('Enter the authorization code: ')
            token_info = flow.fetch_token(code=code)
            db_token_info = DbTokenInfo(**token_info)
            credentials = get_credentail_object_from_token_info(db_token_info)
            update_db_token(db_token_info)

    return credentials


def upload_clip(clip: Clip):
    creds = authenticate()
    youtube = build('youtube', 'v3', credentials=creds)

    print(f"uploading clip: {clip.broadcaster_name} - {clip.title}")
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                # "notifySubscribers"
                "title": clip.broadcaster_name + " - " + clip.title,
                "tags": [clip.broadcaster_name, "shorts", "twitch", "clips"],
                "defaultLanguage": clip.language,
                # "categoryId":
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False,
                "license": "youtube"
            }
        },
        media_body=googleapiclient.http.MediaFileUpload(clip.converted_path, chunksize=-1, resumable=True)
    )

    response = request.execute()
    if response:
        print(f"Finished! {response['id']}", response)
        set_uploaded(clip.id) # todo: video url <--------------


def upload_clips() -> int:
    _clips = get_clips_to_upload()
    for clip in _clips:
        if not os.path.isfile(clip.converted_path):
            set_error(clip.id)
            continue
        upload_clip(clip)

    return len(_clips)