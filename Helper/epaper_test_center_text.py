#!/bin/env python3

import os
import sys
from time import sleep
from PIL import Image, ImageDraw, ImageFont

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
FONT_PATH = "/home/pi/Documents/pif-epaper/Poem-App/fonts/InputMono-Regular.ttf"  # Update with the correct path to your font

# Initialize e-paper display
def init_display():
    logger.info("Initializing epd3in52")
    epd = epd3in52.EPD()
    epd.init()
    epd.Clear()
    return epd

# Function to display centered text
def display_centered_text(epd, text):
    try:
        # Initial font size
        font_size = 14
        image = Image.new('1', (EPAPER_WIDTH, EPAPER_HEIGHT), 255)
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(FONT_PATH, font_size)

        # Word wrap
        lines = text.split('\n')
        total_height = len(lines) * draw.textsize('A', font=font)[1]

        y = (EPAPER_HEIGHT - total_height) // 2  # Center vertically
        for line in lines:
            text_width, text_height = draw.textsize(line, font=font)
            x = (EPAPER_WIDTH - text_width) // 2  # Center horizontally
            draw.text((x, y), line, font=font, fill=0)
            y += text_height

        # Display the text
        epd.display(epd.getbuffer(image))
        epd.refresh()
        sleep(10)
        epd.Clear()

    except Exception as e:
        logger.error(f"Error in display_centered_text: {e}")

# Main function for the test script
def main():
    try:
        epd = init_display()

        # Pre-made sentences
        sentences = "Crestfallen leaves fall,\n" \
                    "Swindled by the gadfly's breeze,\n" \
                    "Nature's trick revealed."
        
        # Displaying the sentences
        display_centered_text(epd, sentences)

        logger.info("sleeping display...")
        epd.sleep()

    except KeyboardInterrupt:    
        logging.info("ctrl + c:")
        epd1in54.epdconfig.module_exit()
        exit()

if __name__ == "__main__":
    main()
