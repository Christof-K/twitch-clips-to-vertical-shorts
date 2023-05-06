import os
import requests
from datetime import datetime, timedelta
from clip_storage import store_clip_data,clip_exists

MAX_CLIPS_PER_REQUEST = 100
CLIENT_ID = "1a7upfme0ykcfa8ub492mk9eqmwojc"
TOKEN = "Bearer 78zsr8l62p4u80u61b9slre9io4rzt"

def get_clips_page(broadcaster_id, after=None):
    url = "https://api.twitch.tv/helix/clips"
    headers = {
        "Client-ID": CLIENT_ID,
        "Authorization": TOKEN,
        "Accept": "application/vnd.twitchtv.v5+json"

    }
    params = {
        "broadcaster_id": broadcaster_id,
        "first": MAX_CLIPS_PER_REQUEST,
        "started_at": (datetime.utcnow() - timedelta(days=1)).isoformat() + "Z"
    }

    if after:
        params["after"] = after

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        json_data = response.json()
        return json_data
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None

def get_all_clips(broadcaster_id):
    all_clips = []
    after = None

    while True:
        json_data = get_clips_page(broadcaster_id, after)
        if json_data:
            clips = json_data["data"]
            if not clips:
                break
            all_clips.extend(clips)
            after = json_data["pagination"].get("cursor")
            if after is None or len(clips) < MAX_CLIPS_PER_REQUEST:
                break
        else:
            break

    return all_clips

def download_clip(clip_url, file_name):
    response = requests.get(clip_url, stream=True)
    if response.status_code == 200:
        with open(file_name, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
    else:
        print(f"Error: {response.status_code}, {response.text}")



broadcaster_id = "71092938"


# Get all clips from the last week
all_clips = get_all_clips(broadcaster_id)

# Sort clips by view count, most first
sorted_clips = sorted(all_clips, key=lambda clip: clip['view_count'], reverse=True)

# Calculate average view count
average_view_count = sum([clip['view_count'] for clip in sorted_clips]) / len(sorted_clips)

# Filter clips with more than the average amount of views and at least 1000 views
filtered_clips = [clip for clip in sorted_clips if clip['view_count'] > average_view_count and clip['view_count'] > 1000]



# Download filtered clips
download_folder = "downloads"
os.makedirs(download_folder, exist_ok=True)

for clip in filtered_clips:
    if clip_exists(clip["id"]):
      print(f"Clip {clip['id']} already exists, skipping...")
      continue
    print(f"Downloading: {clip['title']}, URL: {clip['url']}, Views: {clip['view_count']}")
    file_name = os.path.join(download_folder, f"{clip['id']}.mp4")
    download_clip(clip['thumbnail_url'].replace('-preview-480x272.jpg', '.mp4'), file_name)
    # Store clip data in the MongoDB database
    store_clip_data(clip, file_name)
