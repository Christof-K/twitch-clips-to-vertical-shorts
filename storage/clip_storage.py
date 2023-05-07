import string
from typing import NamedTuple, List
from mongo_connector import CLIPS


class Clip(NamedTuple):
    broadcaster_name: str
    clip_id: str
    clip_duration: float
    download_path: str = ""
    converted_path: str = ""
    converted: int = 0
    uploaded: int = 0
    error: int = 0
    archived: int = 0

def store_clip_data(clip, downlad_file_name: string):
    clip_data = {
        "broadcaster_name": clip["broadcaster_name"],
        "clip_id": clip["id"],
        "clip_duration": clip["duration"],
        "download_path": downlad_file_name,
        "converted_path": "",
        "converted": 0,
        "uploaded": 0,
        "error": 0,
        "archived": 0
    }
    CLIPS.insert_one(clip_data)


def get_clips_to_convert() -> List[Clip]:
    clips = []
    query = {"error": 0, "archived": 0, "converted": 0}
    cursor = CLIPS.find(query)
    for c in cursor:
        c.pop('_id', None)
        clip_obj = Clip(**c)
        clips.append(clip_obj)
    return clips

def clip_exists(clip_id: string):
  return CLIPS.find_one({"clip_id": clip_id}) is not None

def set_converted(clip: Clip, output_path: string):
  CLIPS.update_one(
    {"clip_id": clip.clip_id},
    {"$set": {
      "converted": 1,
      "converted_path": output_path
    }}
  )

def set_uploaded(clip_id: string):
  CLIPS.update_one(
     {"clip_id": clip_id},
     {"$set": {"uploaded": 1}}
  )

def set_error(clip_id: string):
  CLIPS.update_one(
     {"clip_id": clip_id},
     {"$set": {"error": 1}}
  )

def set_archived(clip_id: string):
  CLIPS.update_one(
     {"clip_id": clip_id},
     {"$set": {"archived": 1}}
  )