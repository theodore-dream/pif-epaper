#!/bin/env python3

import os
from time import sleep
from PIL import Image, ImageDraw, ImageFont
import textwrap

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
FONT_SIZE = 10

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

    # Split text into lines
    lines = text.splitlines()

    # Calculate the height of a single line of text
    _, line_height = draw.textsize('A', font=font)  # Using 'A' as a sample character

    # Calculate starting y position to center the block of text vertically
    total_height = line_height * len(lines)
    y = (EPAPER_HEIGHT - total_height) // 2

    for line in lines:
        # Calculate text width for each line
        text_width, _ = draw.textsize(line, font=font)
        x = (EPAPER_WIDTH - text_width) // 2

        # Draw each line
        draw.text((x, y), line, font=font, fill=0)
        y += line_height  # Move y down for next line

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


def display_dialogue(left_text, right_text, display_time):
    epd = epd3in52.EPD()

    try:
        image = Image.new('1', (EPAPER_WIDTH, EPAPER_HEIGHT), 255)
        draw = ImageDraw.Draw(image)

        font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
        logger.info("Font loaded successfully.")

        # Text wrapping
        wrap_width = (EPAPER_WIDTH // 2) - 20  # Half the screen width minus margins
        left_lines = textwrap.wrap(left_text, width=wrap_width)
        right_lines = textwrap.wrap(right_text, width=wrap_width)

        y = 20  # Top margin

        # Draw and calculate height for left text
        for line in left_lines:
            bbox = font.getmask(line).getbbox()
            text_height = bbox[3] - bbox[1]  # Bottom minus top
            draw.text((10, y), line, font=font, fill=0)
            y += text_height + 5  # Increment y position with a small padding

        # Reset y position for right text
        y = 20
        for line in right_lines:
            bbox = font.getmask(line).getbbox()
            text_height = bbox[3] - bbox[1]  # Bottom minus top
            draw.text((EPAPER_WIDTH // 2 + 10, y), line, font=font, fill=0)
            y += text_height + 5  # Increment y position with a small padding

        logger.info("Dialogue text drawn on image successfully.")

        # Display the image
        epd.display(epd.getbuffer(image))
        epd.lut_GC()
        epd.refresh()
        logger.info("Dialogue displayed on e-paper successfully.")
        sleep(display_time)

    except Exception as e:
        logger.error(f"Error in display_dialogue: {e}")
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

