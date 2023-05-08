import string
from typing import NamedTuple, List
from mongo_connector import CLIPS


class Clip(NamedTuple):
    id: str
    broadcaster_name: str
    duration: float
    url: str
    broadcaster_id: str
    creator_id: str
    creator_name: str
    video_id: str
    game_id: str
    embed_url: str
    view_count: str
    language: str
    title: str
    created_at: str
    vod_offset: int
    download_path: str = ""
    converted_path: str = ""
    converted: int = 0
    uploaded: int = 0
    error: int = 0
    archived: int = 0

def store_clip_data(clip, downlad_file_name: string):
    clip_data = {
        **clip,
        "download_path": downlad_file_name,
        "converted_path": "",
        "converted": 0,
        "uploaded": 0,
        "error": 0,
        "archived": 0
    }
    CLIPS.insert_one(clip_data)

def _clip_parser(clip_dict):
  return {k: v for k, v in clip_dict.items() if k in Clip._fields}

def get_clips_to_convert() -> List[Clip]:
    clips = []
    query = {"error": 0, "archived": 0, "converted": 0}
    cursor = CLIPS.find(query)
    for c in cursor:
        clip_obj = Clip(**_clip_parser(c))
        clips.append(clip_obj)
    return clips

def get_clips_to_upload() -> List[Clip]:
    clips = []
    query = {"error": 0, "archived": 0, "converted": 1, "uploaded": 0}
    cursor = CLIPS.find(query)
    for c in cursor:
        clip_obj = Clip(**_clip_parser(c))
        clips.append(clip_obj)
    return clips

def clip_exists(clip_id: string):
  return CLIPS.find_one({"id": clip_id}) is not None

def set_converted(clip: Clip, output_path: string):
  CLIPS.update_one(
    {"id": clip.id},
    {"$set": {
      "converted": 1,
      "converted_path": output_path
    }}
  )

def set_uploaded(clip_id: string):
  CLIPS.update_one(
     {"id": clip_id},
     {"$set": {"uploaded": 1}}
  )

def set_error(clip_id: string):
  CLIPS.update_one(
     {"id": clip_id},
     {"$set": {"error": 1}}
  )

def set_archived(clip_id: string):
  CLIPS.update_one(
     {"id": clip_id},
     {"$set": {"archived": 1}}
  )