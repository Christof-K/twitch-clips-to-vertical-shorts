import os
from moviepy.editor import *
from moviepy.video.fx.all import rotate
from storage.clip_storage import set_converted, get_clips_to_convert, Clip
from dotenv import load_dotenv
load_dotenv();

channel_name = os.environ.get('YT_CHANNEL_NAME')
converted_folder = "converted"
temp_folder = "temp"
max_height = 1080

def convert_to_vertical(clip: Clip):

    output_path = os.path.join(converted_folder, f'vertical_{clip.id}.mp4')
    audio_output = os.path.join(temp_folder, f'sound_vertical_{clip.id}.mp4')
    video_clip = VideoFileClip(clip.download_path, target_resolution=(607, 1080))
    black_bar = ColorClip((1080, 1920), color=[0, 0, 0], duration=video_clip.duration)

    # Position the inner clip in the vertical center of the black_bar
    centered_clip = video_clip.set_position((0, "center"))

    # Create a TextClip with broadcaster name
    text = TextClip('twitch.tv/'+clip.broadcaster_name, fontsize=60, color='white', bg_color='transparent', size=(black_bar.size[0], 50))
    text = text.set_position(('center', 50)).set_duration(video_clip.duration)

     # Create a semi-transparent watermark text diagonally across the inner clip
    watermark_text = TextClip(channel_name, fontsize=70, color='white', bg_color='transparent')
    watermark_text = watermark_text.set_position(("center", "center"), relative=True)
    watermark_text = rotate(watermark_text, angle=-35, unit="deg", resample="bicubic", expand=True)
    watermark_text.set_opacity(0.7)
    watermark_text = watermark_text.set_duration(video_clip.duration)

    # Combine the black bar, centered clip, and text into a final composite clip
    final_clip = CompositeVideoClip([black_bar, centered_clip, text, watermark_text])

    # Write the final clip to a new video file
    final_clip.write_videofile(
        output_path,
        codec='libx264',
        audio_codec='aac',
        temp_audiofile=audio_output
    )
    set_converted(clip, output_path)


os.makedirs(converted_folder, exist_ok=True)
os.makedirs(temp_folder, exist_ok=True)

_clips = get_clips_to_convert()
if not _clips:
    print('No clips to convert')
for clip in _clips:
    print(f'Converting {clip.id} to 9:16 aspect ratio')
    convert_to_vertical(clip)