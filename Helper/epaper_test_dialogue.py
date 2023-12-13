#!/usr/bin/env python3

import os
import sys
from time import sleep
from PIL import Image, ImageDraw, ImageFont
import textwrap


# Setup logger
from modules.logger import setup_logger
logger = setup_logger("epaper_test_dialogue")

# Specify the exact file path to the waveshare_epd folder and other modules
waveshare_epd_path = "/home/pi/Documents/pif-epaper/Poem-App/modules"  # Replace with your path
sys.path.append(waveshare_epd_path)



from waveshare_epd import epd3in52

def display_dialogue(left_text, right_text, display_time):
    epd = epd3in52.EPD()
    image = Image.new('1', (EPAPER_WIDTH, EPAPER_HEIGHT), 255)
    draw = ImageDraw.Draw(image)

    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    logger.info("Font loaded successfully.")

    # Estimate the average number of characters that can fit in the column width
    average_char_width = font.getsize("A")[0]  # Width of a single character
    column_width = EPAPER_WIDTH // 2  # Width of each column
    max_char_per_line = column_width // average_char_width

    def wrap_and_draw_text(text, x_offset):
        y = 20  # Top margin
        for paragraph in text.split('\n'):
            lines = textwrap.wrap(paragraph, width=max_char_per_line)
            for line in lines:
                bbox = font.getmask(line).getbbox()
                text_height = bbox[3] - bbox[1]  # Bottom minus top
                draw.text((x_offset, y), line, font=font, fill=0)
                y += text_height + 5  # Increment y position with a small padding
            y += text_height + 5  # Additional space between paragraphs

    # Draw left and right text
    wrap_and_draw_text(left_text, 10)
    wrap_and_draw_text(right_text, EPAPER_WIDTH // 2 + 10)

    logger.info("Dialogue text drawn on image successfully.")

    # Display the image
    epd.display(epd.getbuffer(image))
    epd.lut_GC()
    epd.refresh()
    logger.info("Dialogue displayed on e-paper successfully.")
    sleep(display_time)

# Constants
EPAPER_WIDTH = 360
EPAPER_HEIGHT = 240
FONT_PATH = "/home/pi/Documents/pif-epaper/Poem-App/fonts/InputMono-Regular.ttf"  # Update with your font path
FONT_SIZE = 10

# Initialize e-paper display
def init_display():
    logger.info("Initializing epd3in52")
    epd = epd3in52.EPD()
    epd.init()
    epd.Clear()
    return epd

# Main function for the test script
def main():
    try:
        epd = init_display()

        # Define test dialogue
        left_text = "Eclipse shadows dance, in harmonized silence, on reflective cosmic shores.,"
        right_text = "Sunny moons go below the stars, then they stay there, flying forever."

        # Displaying the dialogue
        display_dialogue(left_text, right_text, 10)

        sleep(5)  # Pause to view

        logger.info("Clearing display...")
        epd.Clear()
        epd.sleep()

    except Exception as e:
        logger.error(f"Error in main: {e}")

if __name__ == "__main__":
    main()
