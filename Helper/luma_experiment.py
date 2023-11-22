#!/bin/env python3

import os, random
import time
from time import sleep

# using luma library for OLED display through SPI 
from luma.core.interface.serial import spi
from luma.core.render import canvas
from luma.oled.device import ssd1351
from luma.core.virtual import viewport
from PIL import ImageFont, ImageDraw

# setup logger
from modules import logger
from modules.logger import setup_logger

logger = setup_logger('luma_log')

serial = spi(device=0, port=0)
device = ssd1351(serial)

# Helper function to display text
def display_text(device, text, pos=(30, 40), fill="white"):
    with canvas(device) as draw:
        font = ImageFont.truetype('/home/pi/Documents/pif-ai-luma/luma-integrate/fonts/pixelmix.ttf',9)
        draw.text(pos, text, font=font, fill=fill)

if __name__ == "__main__":
    try:
        # Call the helper function to display the text
        display_text(device, "Hello World")
        time.sleep(30)  # Leave the text on the screen for 30 seconds
        device.clear()  # Clear the device after use
    except KeyboardInterrupt:
        pass
