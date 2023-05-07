import os
import requests
from datetime import timedelta
from storage.clip_storage import store_clip_data,clip_exists
from storage.broadcaster_storage import get_active_broadcasters
from dotenv import load_dotenv
from twitch_api import get_clips_page, MAX_CLIPS_PER_REQUEST
timedelta
load_dotenv();

download_folder = "downloads"


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


for broadcaster in get_active_broadcasters():

    # Get all clips from the last week
    all_clips = get_all_clips(broadcaster.id)
    if all_clips:

        # Sort clips by view count, most first
        sorted_clips = sorted(all_clips, key=lambda clip: clip['view_count'], reverse=True)

        # Calculate average view count
        average_view_count = sum([clip['view_count'] for clip in sorted_clips]) / len(sorted_clips)

        # Filter clips with more than the average amount of views and at least 1000 views
        filtered_clips = [clip for clip in sorted_clips if clip['view_count'] > average_view_count and clip['view_count'] > 1000]

        # Download filtered clips
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
