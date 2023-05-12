from src.converter import convert_to_vertical
from src.editor import crop_webcam
from moviepy.editor import *
from moviepy.video.fx.all import resize
from storage.clip_storage import Clip
from src.tiktok_uploader import upload_clip

# path = "/Users/kk/projects/twitch_clips2yt_shorts_automation/downloads/AcceptableSquareOpossumOSfrog-9k6gyv_aUxk1AFE6.mp4"
# path = "/Users/kk/projects/twitch_clips2yt_shorts_automation/downloads/AnnoyingShinyHummingbirdNinjaGrumpy-KN5BFLQWH4QDonXS.mp4"
path = "/Users/kk/projects/twitch_clips2yt_shorts_automation/converted/vertical_PowerfulPerfectSalamanderBrainSlug-Ypr88N7RuyoKYjx5.mp4"
clip = Clip(
  id="test",
  # download_path=path,
  converted_path=path,
  broadcaster_name="test",
  duration=10,
  url="",
  broadcaster_id="",
  creator_id="",
  creator_name="",
  video_id="",
  game_id="",
  embed_url="",
  view_count="",
  language="",
  title="Back to back!",
  created_at="",
  vod_offset=""
)


upload_clip(clip)

# convert_to_vertical(clip, True)

# webcam_clip = crop_webcam(video_clip)
# webcam_clip = resize(webcam_clip, width=1000)
# # webcam_clip.write_videofile('/Users/kk/projects/twitch_clips2yt_shorts_automation/temp/webcam_test.mp4')

# res = CompositeVideoClip([video_clip, webcam_clip.set_position((0,0))])
# res.write_videofile('/Users/kk/projects/twitch_clips2yt_shorts_automation/temp/test_res.mp4')