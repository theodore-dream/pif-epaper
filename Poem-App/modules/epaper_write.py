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
FONT_PATH = "/home/pi/Documents/pif-ai-luma/Poem-App/fonts/pixelmix.ttf"  # Update with the correct path to your font

# Initialize your e-paper display here

def init_display():
    logger.info("epd3in52 initialization")
    epd = epd3in52.EPD()
    logger.info("init and Clear")
    epd.init()
    epd.display_NUM(epd.WHITE)
    epd.lut_GC()
    epd.refresh()

    epd.send_command(0x50)
    epd.send_data(0x17)
    sleep(0.1)

def display_information(text, display_time):
    epd = epd3in52.EPD()
    # Initial font size
    font_size = 12

    while True:
        image = Image.new('1', (EPAPER_WIDTH, EPAPER_HEIGHT), 255)
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(FONT_PATH, font_size)

        # Word wrap
        words = text.split()
        lines = []
        line = words.pop(0)
        for word in words:
            # Check if adding the word exceeds line width
            if draw.textsize(line + ' ' + word, font=font)[0] <= EPAPER_WIDTH:
                line += ' ' + word
            else:
                lines.append(line)
                line = word
        lines.append(line)  # Add the last line

        # Check if all lines fit vertically
        total_height = len(lines) * draw.textsize(text, font=font)[1]
        if total_height > EPAPER_HEIGHT:
            font_size -= 1  # Reduce font size and try again
            if font_size == 0:  # Minimum font size reached
                raise ValueError("Text too long to display")
            continue

        y = (EPAPER_HEIGHT - total_height) // 2  # Center vertically
        for line in lines:
            text_width, text_height = draw.textsize(line, font=font)
            x = (EPAPER_WIDTH - text_width) // 2  # Center horizontally
            draw.text((x, y), line, font=font, fill=0)
            y += text_height

        break  # Text fits, exit the loop

    logger.info("Text drawn on image successfully.")
    epd.display(epd.getbuffer(image))
    epd.lut_GC()
    epd.refresh()
    logger.info("Information displayed on e-paper successfully.")
    sleep(display_time)
    logger.info("Clear e-paper display...")
    epd.Clear()

def display_dialogue(epd, left_text, right_text):
    try:
        image = Image.new('1', (EPAPER_WIDTH, EPAPER_HEIGHT), 255)
        draw = ImageDraw.Draw(image)

        font = ImageFont.truetype(FONT_PATH, 10)  # Adjust size as needed
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

