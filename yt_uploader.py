import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from mongo_connector import YT_TOKENS
from storage.clip_storage import Clip, get_clips_to_upload, set_uploaded

def authenticate():
    scopes = ["https://www.googleapis.com/auth/youtube.upload"]
    creds = None

    # Try to find the token document in the MongoDB collection
    token_doc = YT_TOKENS.find_one({"_id": "token"})

    if token_doc:
        # Load the stored credentials from MongoDB
        creds = Credentials.from_authorized_user_info(info=token_doc['credentials'])

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                "yt_secrets.json", scopes)
            creds = flow.run_local_server(port=0)

        # Update or insert the new credentials into MongoDB
        YT_TOKENS.update_one(
            {"_id": "token"},
            {"$set": {"credentials": creds.to_json()}},
            upsert=True
        )

    return creds


def upload_clip(clip: Clip):
    youtube = googleapiclient.discovery.build("youtube", "v3", credentials=authenticate())

    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": clip.title,
                "tags": ["twitch", "clips", clip.broadcaster_name]
            },
            "status": {
                "privacyStatus": "private"
            }
        },
        media_body=googleapiclient.http.MediaFileUpload(clip.converted_path, chunksize=-1, resumable=True)
    )

    set_uploaded(clip.id)
    response = request.execute()
    print(response) # todo: get upload url
    print(f"Uploaded video with ID: {response['id']}")


def upload_clips() -> int:
    _clips = get_clips_to_upload()
    for clip in _clips:
        upload_clip(clip)

    return len(_clips)