import os
from PIL import Image
white_image = Image.new('RGB', (800,800),(255,255,255))
white_image.save('test.jpeg')
with Image.open('test.jpeg') as img:
    with Image.open('') as img2:
        img.paste()