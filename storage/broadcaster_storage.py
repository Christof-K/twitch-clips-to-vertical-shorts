import sys
from typing import NamedTuple, List
from mongo_connector import TWITCH_BROADCASTERS

class Broadcaster(NamedTuple):
  id: int
  name: str
  active: int

def get_active_broadcasters() -> List[Broadcaster]:
  result = []
  query = {"active": 1}
  cursor = TWITCH_BROADCASTERS.find(query)
  for c in cursor:
    c.pop('_id', None)
    result.append(Broadcaster(**c))
  return result