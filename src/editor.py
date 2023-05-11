import os
from typing import List
from moviepy.editor import VideoFileClip
from src.image_people_detector import get_people_coords
from moviepy.video.fx.all import crop


def get_caster_coords(clip: VideoFileClip) -> None|List[int]:
    """
    static rectangular shape
    """

    script_dir = os.path.dirname(os.path.abspath(__file__))
    temp_dir = os.path.abspath(os.path.join(script_dir, '..', 'temp'))
    frame_image = os.path.join(temp_dir, 'webcam_serach_frame.png')
    clip.save_frame(frame_image, t=5)

    ppl_coords = get_people_coords(frame_image)
    #skip tiny face
    # todo: if > 40% of the screen skip

    filtered_ppl = []
    for p in ppl_coords:
        x,y,x1,y1 = tuple(p)
        # todo: relative to clip size
        if (x1 - x) < 200 : continue
        if (y1 - y) < 200 : continue
        filtered_ppl.append(p)

    if len(filtered_ppl) > 1 or not filtered_ppl : return None;
    return filtered_ppl[0]



def crop_webcam(clip: VideoFileClip) -> VideoFileClip|None:
    margin_value = 20

    print("looking for caster face...")
    box = get_caster_coords(clip)
    if not box :
        print("\tnot found caster face - skipped")
        return None
    print("\tfound caster face - cropping zoom")

    x,y,x1,y1 = tuple(box)
    x -= margin_value
    y -= margin_value
    x1 += margin_value
    y1 += margin_value

    if x < 0 : x = 0
    if y < 0 : y = 0
    if x1 > 1080 : x1 = 1080
    if y1 > 1920 : y1 = 1920

    return crop(clip, x,y,x1,y1)
