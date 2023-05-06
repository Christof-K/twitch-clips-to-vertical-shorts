import pymongo

# Connect to the MongoDB server
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["twitch_clips"]
CLIPS = db["clips"]
