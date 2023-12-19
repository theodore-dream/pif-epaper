#!/bin/env python3

import os
from time import sleep
from datetime import datetime
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

def display_information(text):
    epd = epd3in52.EPD()  # Replace with your EPD initialization
    image = Image.new('1', (EPAPER_WIDTH, EPAPER_HEIGHT), 255)
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    logger.info("Font loaded successfully.")

    # Estimate the average number of characters that can fit in the width
    average_char_width = font.getsize("A")[0]
    max_char_per_line = EPAPER_WIDTH // average_char_width

    def calculate_text_height(text):
        total_height = 0
        for paragraph in text.split('\n'):
            lines = textwrap.wrap(paragraph, width=max_char_per_line)
            for line in lines:
                bbox = font.getmask(line).getbbox()
                line_height = bbox[3] - bbox[1]
                total_height += line_height + 5
            total_height += line_height + 5
        return total_height

    def wrap_and_draw_text(text, y_start):
        y = y_start
        for paragraph in text.split('\n'):
            lines = textwrap.wrap(paragraph, width=max_char_per_line)
            for line in lines:
                text_width, _ = draw.textsize(line, font=font)
                x = (EPAPER_WIDTH - text_width) // 2
                draw.text((x, y), line, font=font, fill=0)
                bbox = font.getmask(line).getbbox()
                line_height = bbox[3] - bbox[1]
                y += line_height + 5
            y += line_height + 5

    text_height = calculate_text_height(text)
    y_start = (EPAPER_HEIGHT - text_height) // 2

    # Wrap and draw the text within the text area, starting from the calculated y position
    wrap_and_draw_text(text, y_start)

    logger.info("Text drawn on image successfully.")

    # Display the text
    epd.display(epd.getbuffer(image))
    epd.lut_GC()
    epd.refresh()
    logger.info("Information displayed on e-paper successfully.")

    # Wait for the specified display time
    # temporarily removing
    #sleep(display_time)

    # Clear the display
    #logger.info("Clear e-paper display...")
    #do not clear
    #epd.Clear()

def clear_display():
    epd = epd3in52.EPD()
    epd.Clear()


def display_dialogue_left(left_text, right_text, player_name, match_name, entropy, display_time):
    epd = epd3in52.EPD()
    image = Image.new('1', (EPAPER_WIDTH, EPAPER_HEIGHT), 255)
    draw = ImageDraw.Draw(image)

    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    logger.info("Font loaded successfully.")

    # Calculate new heights
    dialogue_height = int(EPAPER_HEIGHT * 0.8)  # 4/5 of the height for dialogue

    #game_info_height = EPAPER_HEIGHT - dialogue_height  # Remaining 1/5 for game info

    # Estimate the average number of characters that can fit in the column width
    average_char_width = font.getsize("A")[0]  # Width of a single character
    column_width = EPAPER_WIDTH // 2  # Width of each column
    max_char_per_line = column_width // average_char_width

    # Modify wrap_and_draw_text function to respect new height
    def wrap_and_draw_text(text, x_offset, y_limit):
        y = 10  # Top margin
        for paragraph in text.split('\n'):
            lines = textwrap.wrap(paragraph, width=max_char_per_line)
            for line in lines:
                bbox = font.getmask(line).getbbox()
                text_height = bbox[3] - bbox[1]  # Bottom minus top
                if y + text_height > y_limit:  # Check if within the dialogue area
                    return  # Stop drawing if it exceeds the limit
                draw.text((x_offset, y), line, font=font, fill=0)
                y += text_height + 5  # Increment y position with a small padding
            y += text_height + 5  # Additional space between paragraphs

    # Draw left and right text within the dialogue area
    wrap_and_draw_text(left_text, 10, dialogue_height)
    #wrap_and_draw_text(right_text, EPAPER_WIDTH // 2 + 10, dialogue_height) # stops the right side from being drawn

    # Draw game information in the bottom area
    #draw.text((10, dialogue_height + 10), game_info, font=font, fill=0)

    # create a line to seperate the actual game content vs the game info
    draw.text((0, dialogue_height + 10), "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++", font=font, fill=0)

    # draw game information about player and entropy in the bottom left area
    draw.text((10, dialogue_height + 20), "player: " + player_name, font=font, fill=0)

    # getting entropy data into more presentable format
    entropy_percentage = int(entropy * 100)
    entropy_str = f"{entropy_percentage}%"
    logger.info(f"entropy is {entropy}")
    draw.text((10, dialogue_height + 30), "entropy: " + entropy_str, font=font, fill=0)

    # draw game information about match in the bottom right area
    draw.text((EPAPER_WIDTH // 2 + 10, dialogue_height + 20), "match: " + match_name, font=font, fill=0)

    logger.info("Dialogue and game information drawn on image successfully.")

    # Display the image
    epd.display(epd.getbuffer(image))
    epd.lut_GC()
    epd.refresh()
    logger.info("Dialogue displayed on e-paper successfully.")
    sleep(display_time)

def display_dialogue_both(left_text, right_text, player_name, match_name, entropy, display_time):
    epd = epd3in52.EPD()
    image = Image.new('1', (EPAPER_WIDTH, EPAPER_HEIGHT), 255)
    draw = ImageDraw.Draw(image)

    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    logger.info("Font loaded successfully.")
    logger.info(f"right text is {right_text}")

    # Calculate new heights
    dialogue_height = int(EPAPER_HEIGHT * 0.8)  # 4/5 of the height for dialogue

    #game_info_height = EPAPER_HEIGHT - dialogue_height  # Remaining 1/5 for game info

    # Estimate the average number of characters that can fit in the column width
    average_char_width = font.getsize("A")[0]  # Width of a single character
    column_width = EPAPER_WIDTH // 2  # Width of each column
    max_char_per_line = column_width // average_char_width

    # Modify wrap_and_draw_text function to respect new height
    def wrap_and_draw_text(text, x_offset, y_limit):
        logger.info(f"Type of text: {type(text)}")
        y = 10  # Top margin
        for paragraph in text.split('\n'):
            lines = textwrap.wrap(paragraph, width=max_char_per_line)
            for line in lines:
                bbox = font.getmask(line).getbbox()
                text_height = bbox[3] - bbox[1]  # Bottom minus top
                if y + text_height > y_limit:  # Check if within the dialogue area
                    return  # Stop drawing if it exceeds the limit
                draw.text((x_offset, y), line, font=font, fill=0)
                y += text_height + 5  # Increment y position with a small padding
            y += text_height + 5  # Additional space between paragraphs

    # Draw left and right text within the dialogue area
    wrap_and_draw_text(left_text, 10, dialogue_height)
    wrap_and_draw_text(right_text, EPAPER_WIDTH // 2 + 10, dialogue_height)

    # Draw game information in the bottom area
    #draw.text((10, dialogue_height + 10), game_info, font=font, fill=0)

    # create a line to seperate the actual game content vs the game info
    draw.text((0, dialogue_height + 10), "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++", font=font, fill=0)

    # draw game information about player and entropy in the bottom left area
    draw.text((10, dialogue_height + 20), "player: " + player_name, font=font, fill=0)

    # getting entropy data into more presentable format
    entropy_percentage = int(entropy * 100)
    entropy_str = f"{entropy_percentage}%"
    logger.info(f"entropy is {entropy}")
    draw.text((10, dialogue_height + 30), "entropy: " + entropy_str, font=font, fill=0)

    # draw game information about match in the bottom right area
    draw.text((EPAPER_WIDTH // 2 + 10, dialogue_height + 20), "match: " + match_name, font=font, fill=0)

    # Display the image
    epd.display(epd.getbuffer(image))
    epd.lut_GC()
    epd.refresh()
    logger.debug("Dialogue displayed on e-paper successfully.")

    # Save the image to the 'display_output' directory
    output_directory = "display_output"
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Get the current timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_file_name = f"dialogue_{player_name}_{match_name}_{timestamp}.bmp"
    image_path = os.path.join(output_directory, image_file_name)

     # Save the image to the 'display_output' directory
    output_directory = "display_output"
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    image_file_name = f"dialogue_{player_name}_{match_name}.bmp"
    image_path = os.path.join(output_directory, image_file_name)
    image.save(image_path)
    logger.info(f"Image saved to {image_path}")

    logger.info("Saving to disk.....")
    sleep(display_time)



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

# should modify to save a copy of the output to file 