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
FONT_PATH = "/home/pi/Documents/pif-ai-luma/Poem-App/fonts/pixelmix.ttf"  # Update with the correct path to your font

# Initialize e-paper display
def init_display():
    logger.info("Initializing epd3in52")
    epd = epd3in52.EPD()
    epd.init()
    epd.Clear()
    return epd

# Function to display centered text
def display_centered_text(epd, text, display_time):
    try:
        # Initial font size
        font_size = 12
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
        sleep(display_time)

    except Exception as e:
        logger.error(f"Error in display_centered_text: {e}")

# Main function for the test script
def main():
    try:
        epd = init_display()

        # Pre-made sentences
        sentences = "First Sentence\nSecond Sentence\nThird Sentence"
        
        # Displaying the sentences
        display_centered_text(epd, sentences, 10)

        logger.info("Clearing display...")
        epd.Clear()
        epd.sleep()

    except Exception as e:
        logger.error(f"Error in main: {e}")

if __name__ == "__main__":
    main()
