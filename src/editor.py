import os
from moviepy.editor import VideoFileClip
from src.image_people_detector import get_people_coords
from moviepy.video.fx.all import crop


def get_caster_coords(clip: VideoFileClip):
    """
    static rectangular shape
    """

    script_dir = os.path.dirname(os.path.abspath(__file__))
    temp_dir = os.path.abspath(os.path.join(script_dir, '..', 'temp'))
    frame_image = os.path.join(temp_dir, 'webcam_serach_frame.png')
    clip.save_frame(frame_image, t=5)

    person_coords = get_people_coords(frame_image)[0] #todo: choose one base on something
    # print("Person coordinates:", person_coords)
    return person_coords



def crop_webcam(clip: VideoFileClip) -> VideoFileClip:
    margin_value = 20
    #todo: empty result
    x,y,x1,y1 = tuple(get_caster_coords(clip))
    x -= margin_value
    y -= margin_value
    x1 += margin_value
    y1 += margin_value

    if x < 0 : x = 0
    if y < 0 : y = 0
    if x1 > 1080 : x1 = 1080
    if y1 > 1920 : y1 = 1920

    return crop(clip, x,y,x1,y1)
