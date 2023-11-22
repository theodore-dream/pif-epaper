#!/bin/env python3

from datetime import datetime
from time import sleep
from PIL import Image, ImageDraw, ImageFont
from textwrap import wrap

# using luma library for OLED display through SPI 
from luma.core.interface.serial import spi
from luma.core.render import canvas
from luma.oled.device import ssd1351
from luma.core.virtual import viewport

#setup logger
from modules.logger import setup_logger
logger = setup_logger("display_write")

# script primarily from: https://levelup.gitconnected.com/how-to-properly-calculate-text-size-in-pil-images-17a2cc6f51fd

def get_y_and_heights(text_lines, dimensions, margin, font):
    """Get the first vertical coordinate at which to draw text and the height of each line of text"""
    # https://stackoverflow.com/a/46220683/9263761
    ascent, descent = font.getmetrics()

    # Calculate the height needed to draw each line of text (including its bottom margin)
    line_heights = [
        font.getmask(text_line).getbbox()[3] + descent + margin
        for text_line in text_lines
        if text_line.strip()  # Skip empty or whitespace-only lines

    ]
    # The last line doesn't have a bottom margin
    line_heights[-1] -= margin

    # Total height needed
    height_text = sum(line_heights)
    #logger.debug("total height is height_text: " + str(height_text))

    # Calculate the Y coordinate at which to draw the first line of text
    y = (dimensions[1] - sum(line_heights)) // 2

    # Return the first Y coordinate and a list with the height of each line
    return (y, line_heights)

# setting up virtual viewport and font for OLED
serial = spi(device=0, port=0)
device = ssd1351(serial)

FONT_FAMILY = "/home/pi/Documents/pif-ai-luma/Poem-App/fonts/pixelmix.ttf"
# virtual viewport for OLED 
VIRTUAL = viewport(device, width=128, height=128)
WIDTH = 128
HEIGHT = 128
FONT_SIZE = 8
V_MARGIN =  2
CHAR_LIMIT = 24
BG_COLOR = "black"
TEXT_COLOR = "white"

#text = "this is the longest fucking text you're ever going to write and I swear to god its going to show up perfectly I believe in you."

text = "Whispered tales, woven in twilight's embrace, Where innocence weaves a delicate lace, A taste of butterscotch, numbing the mind, Reflecting in amber eyes, stories entwined."

def display_write(text, display_time):
    # Create the font
    font = ImageFont.truetype(FONT_FAMILY, FONT_SIZE)
    # New image based on the settings defined above
    img = Image.new("RGB", (WIDTH, HEIGHT), color=BG_COLOR)
    # Interface to draw on the image
    draw_interface = ImageDraw.Draw(img)

    # Wrap the `text` string into a list of `CHAR_LIMIT`-character strings
    text_lines = [line for line in wrap(text, CHAR_LIMIT) if line.strip()]

    # Get the first vertical coordinate at which to draw text and the height of each line of text
    y, line_heights = get_y_and_heights(
        text_lines,
        (WIDTH, HEIGHT),
        V_MARGIN,
        font
    )

    # Draw each line of text
    for i, line in enumerate(text_lines):
        # Check if line is not empty or not just whitespace
        if line.strip():
            # Calculate the horizontally-centered position at which to draw this line
            line_width = font.getmask(line).getbbox()[2]
            x = ((WIDTH - line_width) // 2)

            # Draw this line
            draw_interface.text((x, y), line, font=font, fill=TEXT_COLOR)

            # Move on to the height at which the next line should be drawn at
            y += line_heights[i]

    # Let's see those lines!
    logger.info(f"Displaying text (original varable):\n{text}")
    logger.info("Displaying text_lines (wrapped): " + str(text_lines))
    # Display the image
    device.display(img)
    sleep(display_time)

    # Save the resulting image with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    img.save(f"text_output/result_{timestamp}.png")

if __name__ == "__main__":
    display_write(text, 10)