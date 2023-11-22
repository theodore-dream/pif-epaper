#!/bin/env python3

import os, random
import time
from time import sleep
import textwrap
import PIL
from PIL import Image, ImageFont, ImageDraw

# using luma library for OLED display through SPI 
from luma.core.interface.serial import spi
from luma.core.render import canvas
from luma.oled.device import ssd1351
from luma.core.virtual import viewport

# setup logger
import logger
from logger import setup_logger
logger = setup_logger('luma_log')

# fit for size
opening_text1 = ["HELLO? HELLO! HELLO! HELLO! HELLO!", 
                "HELLO! HELLO? HELLO! HELLO! HELLO!", 
                "HELLO! HELLO! HELLO! HELLO! HELLO!", 
                " ", 
                "HELLO! HELLO! HELLO", 
                "HELLO! HELLO? HELLO", 
                "HELLO! HELLO? HELLO", 
                " ", 
                "HELLO! HELLO! HELLO", 
                "HELLO! HELLO? HELLO", 
                "HELLO! HELLO? HELLO",
                 " ", 
                "HELLO! HELLO? HELLO",]    #line 13

opening_text2 = "HELLO! HELLO? HELLO HELLO! HELLO? HELLO HELLO! HELLO? HELLO \
HELLO! HELLO? HELLO HELLO! HELLO? HELLO HELLO! HELLO? HELLO \
HELLO! HELLO? HELLO HELLO! HELLO? HELLO HELLO! HELLO? HELLO"

serial = spi(device=0, port=0)
device = ssd1351(serial)

# setting up virtual viewport and font for OLED
virtual = viewport(device, width=device.width, height=128)
font = ImageFont.truetype('/home/pi/Documents/pif-ai-luma/Poem-App/fonts/pixelmix.ttf', 8)

def get_text_width(text, font):
    """
    Returns the width in pixels of the given text when rendered in the given font.
    """
    im = Image.new('1', (128, 128))
    draw = ImageDraw.Draw(im)
    font_mono="/home/pi/Documents/pif-ai-luma/Poem-App/fonts/pixelmix.ttf"
    font_color_white = " (255, 255, 255, 255)"
    font = ImageFont.truetype(font_mono, 8)
    txt_width, _ = im.textsize(text, font=font)
    return txt_width
    
    
    #return draw.getsize(text, font)[0]  # width is the first element

def text_wrap(text, font, max_width):
    """
    Wrap text to fit specified width in pixels
    """
    words = text.split(' ')
    lines = []
    current_line = ""

    for word in words:
        test_line = f"{current_line} {word}".strip()
        # Check the pixel width of the test line
        test_line_width = get_text_width(test_line, font)

        if test_line_width <= max_width:
            # If it fits, add the word to the current line
            current_line = test_line
        else:
            # If it doesn't fit, add the current line to the list of lines and start a new line with the current word
            lines.append(current_line)
            current_line = word

    if current_line:  # If there are any words left in current_line, add it as the final line
        lines.append(current_line)

    return lines

# Mostly crawl.py example also using http://codelectron.com/setup-oled-display-raspberry-pi-python/ for info

def luma_write(gametext, display_time):
    # [...]
    with canvas(device) as draw:
        lines = []
        # In case gametext is a list of strings
        if isinstance(gametext, list):
            for txt in gametext:
                lines.extend(text_wrap(txt, font, device.width))  # pass in the font and the device width
        # In case gametext is a single string
        elif isinstance(gametext, str):
            lines.extend(text_wrap(gametext, font, device.width))  # pass in the font and the device width

        # Ensure only the first 10 lines are taken (to fit your 10 lines OLED)
        #lines = lines[:20]
        logger.info(f"lines: {lines}")

        # Draw each line on the OLED
        for i, line in enumerate(lines):
            draw.text((0, i * 10), line, font=font, fill="white")
            print("used draw.text")
            #sleep(5)
            #term.println("Hello, World!")
            #print("Use println to print text followed by a newline")
            #sleep(5)
            #term.puts("No newline here.")
            #print("Used puts to print text without a newline")
            #sleep(5)

    # Sleep for the display_time before clearing the screen
    time.sleep(display_time)
    device.clear()
    logger.info("wrote to device")
    device.clear()
    logger.info("device cleared, luma_write function completed")

#lets run it as a unit test
if __name__ == "__main__":
    luma_write(opening_text1, 15)