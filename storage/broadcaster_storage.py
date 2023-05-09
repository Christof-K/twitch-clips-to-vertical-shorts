import json
import sys
from typing import NamedTuple, List
from storage.mongo_connector import TWITCH_BROADCASTERS
from src.twitch_api import Broadcaster, get_broadcaster



def get_broadcasters() -> List[Broadcaster]:
  print("fetching broadcasters data...")
  result = []
  casters = json.load(open("storage/broadcasters.json", "r"))
  for caster in casters:
    bc = get_broadcaster(caster)
    result.append(bc)

  return result