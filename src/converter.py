import os
from moviepy.editor import *
from storage.clip_storage import set_converted, get_clips_to_convert, Clip, set_error
from dotenv import load_dotenv
load_dotenv();
from moviepy.video.fx.all import resize,rotate
from skimage.filters import gaussian

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

    # Create an ImageClip for the Twitch icon
    script_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.abspath(os.path.join(script_dir, '..', 'assets'))
    svg_path = os.path.join(assets_dir, 'twitch_icon.png')

    icon_clip = ImageClip(svg_path, duration=video_clip.duration)
    icon_clip = resize(icon_clip, width=80)

    # Create a TextClip for the username
    username = TextClip(clip.broadcaster_name, fontsize=50, color='white', bg_color='transparent')
    icon_clip = icon_clip.set_position((0, 0)).set_duration(video_clip.duration)
    username = username.set_position((100, 15)).set_duration(video_clip.duration)

    credentials = CompositeVideoClip([icon_clip, username], size=(1080, 200)).set_position((50, 50))


    # Create a blurred background of the inner clip
    background_clip = resize(video_clip, newsize=(video_clip.size[0] // 4, video_clip.size[1] // 4))
    background_clip = background_clip.fl_image(lambda image: gaussian(image.astype(float), sigma=25))
    background_clip = resize(background_clip, height=1920)
    background_clip = background_clip.set_position("center")

    # Create a semi-transparent watermark text diagonally across the inner clip
    # watermark_text = TextClip(channel_name, fontsize=40, color='white', bg_color='transparent', stroke_width=1)
    # watermark_text = watermark_text.set_position(("center", 1600)).set_duration(video_clip.duration)

    # Combine the black bar, centered clip, and text into a final composite clip
    final_clip = CompositeVideoClip([
        black_bar,
        background_clip,
        centered_clip,
        credentials,
        # watermark_text
    ])

    # Write the final clip to a new video file
    final_clip.write_videofile(
        output_path,
        codec='libx264',
        audio_codec='aac',
        temp_audiofile=audio_output,
        bitrate='5000k'
    )
    set_converted(clip, output_path)


def convert_clips() -> int:
    os.makedirs(converted_folder, exist_ok=True)
    os.makedirs(temp_folder, exist_ok=True)

    _clips = get_clips_to_convert()
    for clip in _clips:
        if not os.path.isfile(clip.download_path):
            set_error(clip.id)
            continue
        print(f'Converting {clip.id}...')
        convert_to_vertical(clip)
    return len(_clips)