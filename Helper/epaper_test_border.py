#!/bin/env python3

import os
import sys
from time import sleep
from PIL import Image, ImageDraw

# Setup logger
from modules.logger import setup_logger
logger = setup_logger("epaper_write")

# Specify the exact file path to the waveshare_epd folder
waveshare_epd_path = "/home/pi/Documents/pif-epaper/Poem-App/modules"  # Replace with your path
sys.path.append(waveshare_epd_path)

from waveshare_epd import epd3in52

# Constants
EPAPER_WIDTH = 360
EPAPER_HEIGHT = 240

# Initialize e-paper display
def init_display():
    logger.info("Initializing epd3in52")
    epd = epd3in52.EPD()
    epd.init()
    epd.Clear()
    return epd

# Function to display a border rectangle
def display_border_rectangle(epd, display_time=10):
    try:
        image = Image.new('1', (EPAPER_WIDTH, EPAPER_HEIGHT), 255)
        draw = ImageDraw.Draw(image)

        # Draw multiple rectangles for thicker border
        border_thickness = 3
        for i in range(border_thickness):
            border_rect = [i, i, EPAPER_WIDTH - 1 - i, EPAPER_HEIGHT - 1 - i]
            draw.rectangle(border_rect, outline=0, fill=None)

        # Display the rectangle
        epd.display(epd.getbuffer(image))
        epd.refresh()
        sleep(display_time)

    except Exception as e:
        logger.error(f"Error in display_border_rectangle: {e}")

# Main function for the test script
def main():
    try:
        epd = init_display()

        # Displaying the border rectangle
        display_border_rectangle(epd)

        logger.info("Clearing display...")
        epd.Clear()
        epd.sleep()

    except Exception as e:
        logger.error(f"Error in main: {e}")

if __name__ == "__main__":
    main()
