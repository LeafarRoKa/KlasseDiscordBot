from PIL import ImageFont, ImageDraw,Image
from io import BytesIO
from datetime import timedelta,datetime, timezone
def format_to_code(code: str, language:str):
    if len(code) >= 2000:
        final_code = code
    else:
        final_code = f'```{language}\n'
        final_code += code
        final_code += '```'
    return final_code

def PIL_text_obj(draw: ImageDraw,cords, txt_to_dp = 'hello world',font_size = 20,bold_width = 0.5, text_color = (0,0,0),bold_fill = None, font = 'default'):
        if bold_fill == None:
            bold_fill = text_color
        try:
            font = ImageFont.truetype(font, font_size)
        except OSError:
            try:
                font = ImageFont.truetype("arial.ttf", font_size)  # Works on Windows
            except OSError: # Fallback for Linux/Mac if Arial is not available
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
        draw.text(cords,txt_to_dp,fill= text_color, font=font, stroke_width=bold_width, stroke_fill= bold_fill)
        return draw

def PIL_round_img_obj(img, size = None):
    with Image.open(BytesIO(img)).convert('RGBA') as img:
        jpeg_ram = BytesIO()
        img.save(jpeg_ram,'PNG')
        jpeg_ram.seek(0) #read cursor position
        if size != None:
            img = img.resize(size, Image.LANCZOS)
        width, height = img.size
        mask = Image.new('L', (width, height), 0) # L is for grayscale black and white 0 is the color black so everything that is black here covers everyting white shows
        draw = ImageDraw.Draw(mask)#the object you can draw on
        draw.ellipse((0,0, width, height), fill= 255)#it draws an image from (0,0) (x) to (50,50) (y) 
        #puts the mask over the image so only the part inside the circle is visible
        rounded_img = Image.new('RGBA', (width, height), (0,0,0,0))#creates a new Image object with the image size of the full mask and of the image to round
        rounded_img.paste(img, (0,0), mask=mask)#mask is not only just used as out it over the image but it is used as only show whats visible inside and cut the rest away its 0,0 because 0,0 is in the top left 
        return rounded_img, mask   


def can_do_daily(time_redeemed:datetime = None):
    if time_redeemed and not time_redeemed.tzinfo:
        time_redeemed = time_redeemed.replace(tzinfo = timezone.utc)
    if not time_redeemed or time_redeemed+timedelta(days=1) < datetime.now(timezone.utc):# if the diff to 1970 from the date redeemed + 1 day is greater than now then it means that that time + 24 hours are farther from 1970 meaning farther in the future
        return True, 0,0
    diff = ((time_redeemed+timedelta(days=1)) - datetime.now(timezone.utc))
    hours, rest = divmod(diff.total_seconds(), timedelta(hours=1).total_seconds())
    minutes =  int(rest//timedelta(minutes=1).total_seconds())# just does a modulo and returns the rest
    return False, hours, minutes