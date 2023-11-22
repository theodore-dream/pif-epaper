#!/bin/env python3

import os, random
import time
from time import sleep

# using luma library for OLED display through SPI 
from luma.core.interface.serial import spi
from luma.core.render import canvas
from luma.oled.device import ssd1351
from luma.core.virtual import viewport

# setup logger
from modules import logger
from modules.logger import setup_logger

logger = setup_logger('luma_log')

serial = spi(device=0, port=0)
device = ssd1351(serial)

from PIL import ImageFont, ImageDraw


# 20x11 grid
# 18, 19, 20 20 20 20
# 18 wide x 10 is the max size for disayable characters 
gametext = "xoxxxxxxxxxxxxxxox", \
           "xxxxxxxxxxxxxxxxxx", \
           "oxxxxxxxxxxxxxxxxo", \
           "xxxxxxxxxxxxxxxxxx", \
           "xxxxxxxxxxxxxxxxxx", \
           "xxxxxxxxxxxxxxxxxx", \
           "xxxxxxxxxxxxxxxxxx", \
           "oxxxxxxxxxxxxxxxxo", \
           "xxxxxxxxxxxxxxxxxx", \
           "xoxxxxxxxxxxxxxxox"  # Here, each string is 18 characters long, and there are 10 strings


# Mostly crawl.py example also using http://codelectron.com/setup-oled-display-raspberry-pi-python/ for info

# importing a text file (raw poem) and then splitting into a line with 3 words each line:
# how to split into 1 word each line https://stackoverflow.com/questions/16922214/reading-a-text-file-and-splitting-it-into-single-words-in-python
# how to split with specifying a number of words / strings https://www.w3schools.com/python/ref_string_split.asp

def luma_write(gametext):
    # first let's make sure device is clear
    device.clear()
    logger.info("Starting luma_write function")

    virtual = viewport(device, width=device.width, height=768)
    font = ImageFont.truetype('/home/pi/Documents/pif-ai-luma/Poem-App/fonts/pixelmix.ttf',9)

    for _ in range(1):
        with canvas(device) as draw:
            #for i, line in enumerate(gametext.split("\n")):
            for i, line in enumerate(gametext):  
                draw.text((0, 0 + (i * 12)), text=line, font=font, fill="white")

    logger.info("wrote to device")
    time.sleep(30)
    logger.info("clearing device")
    device.clear()
    logger.info("device cleared, luma_write function completed successfully")

#def luma_test():
#    with canvas(device) as draw:
#        draw.rectangle(device.bounding_box, outline="white", fill="black")
#        draw.text((30, 40), "Hello World", fill="white")

if __name__ == "__main__":
    try:
        luma_write(gametext)
    except KeyboardInterrupt:
        pass

