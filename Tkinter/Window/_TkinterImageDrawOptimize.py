from typing import Union

from PIL import Image

Number = Union[int,float]

def OptimizeRenderMiss(im:Image.Image,x:Number) -> Image.Image:
    if x <= 1.0:
        raise ValueError("x must be greater than 1.0")
    target_width = im.width * x
    target_height = im.height * x
    target_width,target_height = int(target_width),int(target_height)
    target_im = Image.new("RGBA",(target_width,target_height),(255,255,255,0))
    target_im.paste(im,(
        int(target_width / 2 - im.width / 2),
        int(target_height / 2 - im.height / 2)
    ))
    return target_im