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
    #todo: empty result
    x,y,x1,y1 = tuple(get_caster_coords(clip))
    return crop(clip, x,y,x1,y1)
