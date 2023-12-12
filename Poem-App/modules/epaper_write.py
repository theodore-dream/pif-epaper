#!/bin/env python3

import os
from time import sleep
from PIL import Image, ImageDraw, ImageFont

#setup logger
from modules.logger import setup_logger
logger = setup_logger("epaper_write")

# make sure the waveshare epd module is found? not sure if needed
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

from modules.waveshare_epd import epd3in52

# Constants
EPAPER_WIDTH = 360
EPAPER_HEIGHT = 240
FONT_PATH = "/home/pi/Documents/pif-epaper/Poem-App/fonts/InputMono-Regular.ttf"  # Update with the correct path to your font
FONT_SIZE = 8

# Initialize your e-paper display here

def init_display():
    logger.info("Initializing epd3in52")
    epd = epd3in52.EPD()
    epd.init()
    epd.Clear()

def display_information(text, display_time):
    epd = epd3in52.EPD()
    image = Image.new('1', (EPAPER_WIDTH, EPAPER_HEIGHT), 255)
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)

    # Calculate text size
    text_width, text_height = draw.textsize(text, font=font)

    # Center the text
    x = (EPAPER_WIDTH - text_width) // 2
    y = (EPAPER_HEIGHT - text_height) // 2

    # Check if text fits on the display
    if text_width > EPAPER_WIDTH or text_height > EPAPER_HEIGHT:
        raise ValueError("Text too long to display")

    # Draw the text
    draw.text((x, y), text, font=font, fill=0)
    logger.info("Text drawn on image successfully.")

    # Display the text
    epd.display(epd.getbuffer(image))
    epd.lut_GC()
    epd.refresh()
    logger.info("Information displayed on e-paper successfully.")

    # Wait for the specified display time
    sleep(display_time)

    # Clear the display
    logger.info("Clear e-paper display...")
    epd.Clear()

def display_dialogue(epd, left_text, right_text):
    try:
        image = Image.new('1', (EPAPER_WIDTH, EPAPER_HEIGHT), 255)
        draw = ImageDraw.Draw(image)

        font = ImageFont.truetype(FONT_PATH, FONT_SIZE)  # Adjust size as needed
        logger.info("Font loaded successfully.")

        # Calculate positions
        left_x = 10  # Margin
        right_x = EPAPER_WIDTH // 2 + 10
        y = 20  # Top margin

        # Draw text
        draw.text((left_x, y), left_text, font=font, fill=0)
        draw.text((right_x, y), right_text, font=font, fill=0)
        logger.info("Dialogue text drawn on image successfully.")

        # Display the image
        epd.display(epd.getbuffer(image))
        epd.lut_GC()
        epd.refresh()
        logger.info("Dialogue displayed on e-paper successfully.")
        sleep(5)

    except Exception as e:
        logger.error(f"Error in display_dialogue: {e}")

def main():
    try:
        # Initialize e-paper display
        # Example: epd.init()
        logger.info("e-Paper display initialized.")

        # Display informational text
        display_information(epd, "Hello Information")

        # Pause to view
        sleep(5)

        # Display dialogue text
        display_dialogue(epd, "Hello Left", "Hello Right")

        # Pause to view
        sleep(5)

        logger.info("Clear...")
        epd.Clear()
    
        logger.info("Goto Sleep...")
        epd.sleep()

        # Clear the display or any additional steps
        # Example: epd.sleep()
        logger.info("Finished display updates.")

    except Exception as e:
        logger.error(f"Error in main: {e}")

if __name__ == "__main__":
    main()

