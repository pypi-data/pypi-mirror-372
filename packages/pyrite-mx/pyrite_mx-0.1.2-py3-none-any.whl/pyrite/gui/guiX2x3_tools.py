from . import types
from . import wintypes
from . import winapi
from . import wintools
from . import wintraits
import time
import psutil
from sortedcontainers import SortedDict, SortedSet
from typing import Tuple
from PIL import Image, ImageChops
from PIL.Image import Image as PilImage


def is_in_color_range(px: Tuple[int, int, int], minimal_color:int) -> bool:
    return px[0] >= minimal_color and px[1] >= minimal_color and px[2] >= minimal_color


def is_line_color_range(im: PilImage, y: int, minimal_color: int) -> bool:
    width, _ = im.size

    for x in range(0, width-1):
        px = im.getpixel((x, y))
        if not is_in_color_range(px, minimal_color):
            return False
    return True


def is_column_color_range(im: PilImage, x: int, minimal_color: int) -> bool:
    _, height = im.size

    for y in range(0, height-1):
        px = im.getpixel((x, y))
        if not is_in_color_range(px, minimal_color):
            return False
    return True

def get_crop_box_by_px_color(
    im: PilImage, 
    px: Tuple[int, int], 
    scale: float, 
    offset: int) -> Tuple[int, int, int, int]:

    bg = Image.new(im.mode, im.size, px)
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, scale, offset)
    return diff.getbbox()

def crop_by_background(
    im: PilImage, 
    minimal_light_background_color_value: int) -> Tuple[int, int, int, int]:

    width, height = im.size
    original_box = (0, 0, width, height)

    # crop by top left pixel color
    px = im.getpixel((0,height-1))
    if is_in_color_range(px, minimal_light_background_color_value):
        bbox1 = get_crop_box_by_px_color(im, px, 2.0, -100)
    else: 
        bbox1 = original_box

    # crop by bottom right pixel color
    px = im.getpixel((width-1,height-1))
    if is_in_color_range(px, minimal_light_background_color_value):
        bbox2 = get_crop_box_by_px_color(im, px, 2.0, -100)
    else:
        bbox2 = original_box

    crop = (
        max(bbox1[0], bbox2[0]),
        max(bbox1[1], bbox2[1]),
        min(bbox1[2], bbox2[2]),
        min(bbox1[3], bbox2[3])
    )

    return crop


def list_windows(options=None) -> list[types.W]:
    return types.W.list_windows(options)

def rake_windows(options=None, **kwargs):
    return types.W.rake_windows(options,**kwargs)
