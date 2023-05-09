import pymongo

# Connect to the MongoDB server
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["twitch_clips"]
CLIPS = db["clips"]
TWITCH_BROADCASTERS = db["twitch_broadcasters"]
TWITCH_TOKENS = db["twitch_tokens"]
YT_TOKENS = db["yt_tokens"]
