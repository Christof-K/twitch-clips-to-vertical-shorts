import os
import sys
import requests
from datetime import timedelta
from storage.clip_storage import store_clip_data,clip_exists
from storage.broadcaster_storage import get_broadcasters
from dotenv import load_dotenv
from src.twitch_api import get_clips_page, MAX_CLIPS_PER_REQUEST
from storage.games import get_games
timedelta
load_dotenv();

download_folder = "downloads"
views_treshold = int(os.environ.get("CLIP_VIEW_TRESHOLD"))
CLIPS_PER_CASTER = 1
CLIPS_PER_GAME = 3
languages = os.getenv("CLIP_LANGUAGES")



def get_broadcaster_clips(broadcaster_id):
    all_clips = []
    after = None

    while True:
        json_data = get_clips_page(broadcaster_id=broadcaster_id, after=after)
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

def get_game_clips(game_id):
    all_clips = []
    after = None

    while True:
        json_data = get_clips_page(game_id=game_id, after=after)
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

def handle_clips(clips, limit):
    clips = [clip for clip in clips if clip["language"] in languages]

    if clips:
        # Sort clips by view count, most first
        sorted_clips = sorted(clips, key=lambda clip: clip['view_count'], reverse=True)

        # Calculate average view count
        average_view_count = sum([clip['view_count'] for clip in sorted_clips]) / len(sorted_clips)

        # Filter clips with more than the average amount of views and at least (views_treshold) views
        filtered_clips = [clip for clip in sorted_clips if clip['view_count'] > average_view_count and clip['view_count'] > views_treshold][:limit]

        # Download filtered clips
        os.makedirs(download_folder, exist_ok=True)

        for clip in filtered_clips:
            if clip_exists(clip["id"]):
                print(f"Clip {clip['id']} already exists, skipping...")
                continue
            print(f"\tDownloading: {clip['title']}, URL: {clip['url']}, Views: {clip['view_count']}")
            file_name = os.path.join(download_folder, f"{clip['id']}.mp4")
            download_clip(clip['thumbnail_url'].replace('-preview-480x272.jpg', '.mp4'), file_name)
            # Store clip data in the MongoDB database
            store_clip_data(clip, file_name)

def download_clips() -> int:

    # for game_id in get_games():
    #     print(f"fetching clips from game \"{game_id}\"")
    #     clips = get_game_clips(game_id)
    #     if clips:
    #         handle_clips(clips, CLIPS_PER_GAME)


    for broadcaster in get_broadcasters():
        print(f"fetching clips from \"{broadcaster.display_name}\"")
        clips = get_broadcaster_clips(broadcaster.id)
        if clips:
            handle_clips(clips, CLIPS_PER_CASTER)

    return 0 #todo: --
