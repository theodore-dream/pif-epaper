from PIL import Image, ImageDraw, ImageFont
from textwrap import wrap

# using luma library for OLED display through SPI 
from luma.core.interface.serial import spi
from luma.core.render import canvas
from luma.oled.device import ssd1351
from luma.core.virtual import viewport


serial = spi(device=0, port=0)
device = ssd1351(serial)

# script primarily from: https://levelup.gitconnected.com/how-to-properly-calculate-text-size-in-pil-images-17a2cc6f51fd

# not using this 
def get_text_dimensions(text_string, font):
    # https://stackoverflow.com/a/46220683/9263761
    ascent, descent = font.getmetrics()

    text_width = font.getmask(text_string).getbbox()[2]
    text_height = font.getmask(text_string).getbbox()[3] + descent

    return (text_width, text_height)

def get_y_and_heights(text_wrapped, dimensions, margin, font):
    """Get the first vertical coordinate at which to draw text and the height of each line of text"""
    # https://stackoverflow.com/a/46220683/9263761
    ascent, descent = font.getmetrics()

    # Calculate the height needed to draw each line of text (including its bottom margin)
    line_heights = [
        font.getmask(text_line).getbbox()[3] + descent + margin
        for text_line in text_wrapped
    ]
    # The last line doesn't have a bottom margin
    line_heights[-1] -= margin

    # Total height needed
    height_text = sum(line_heights)
    print("total height is height_text: ", height_text)

    # Calculate the Y coordinate at which to draw the first line of text
    y = (dimensions[1] - height_text) // 2

    # Return the first Y coordinate and a list with the height of each line
    return (y, line_heights)


FONT_FAMILY = "/home/pi/Documents/pif-ai-luma/Poem-App/fonts/pixelmix.ttf"
WIDTH = 128
HEIGHT = 128
FONT_SIZE = 8
V_MARGIN =  5
CHAR_LIMIT = 20
BG_COLOR = "black"
TEXT_COLOR = "white"
DISPLAYTIME = 10

text = "HELLO! HELLO? HELLO HELLO! HELLO? HELLO HELLO! HELLO? HELLO \
HELLO! HELLO? HELLO HELLO! HELLO? HELLO HELLO! HELLO? HELLO \
HELLO! HELLO? HELLO HELLO! HELLO? HELLO HELLO! HELLO? HELLO"

def PIL_write():
    # Create the font
    font = ImageFont.truetype(FONT_FAMILY, FONT_SIZE)
    # New image based on the settings defined above
    img = Image.new("1", (WIDTH, HEIGHT), color=BG_COLOR)
    # Interface to draw on the image
    draw_interface = ImageDraw.Draw(img)

    # Wrap the `text` string into a list of `CHAR_LIMIT`-character strings
    text_lines = wrap(text, CHAR_LIMIT)
    # Get the first vertical coordinate at which to draw text and the height of each line of text
    y, line_heights = get_y_and_heights(
        text_lines,
        (WIDTH, HEIGHT),
        V_MARGIN,
        font
    )

    # Draw each line of text
    for i, line in enumerate(text_lines):
        # Calculate the horizontally-centered position at which to draw this line
        line_width = font.getmask(line).getbbox()[2]
        print("line_width: ", line_width)
        x = ((WIDTH - line_width) // 2)

        # Draw this line
        draw_interface.text((x, y), line, font=font, fill=TEXT_COLOR)
        #with canvas(device) as draw:
        #    draw.text((x, y), line, font=font, fill=TEXT_COLOR)
        

        # Move on to the height at which the next line should be drawn at
        y += line_heights[i]

    # Save the resulting image
    img.save("result.png")

# let's run this as a unit test
if __name__ == "__main__":
    PIL_write()