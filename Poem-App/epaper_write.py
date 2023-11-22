import os
import time
import logging
from PIL import Image, ImageDraw, ImageFont

# Setup logging
logging.basicConfig(level=logging.DEBUG)

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

logging.info("epd3in52 Demo")
epd = epd3in52.EPD()
logging.info("init and Clear")
epd.init()
epd.display_NUM(epd.WHITE)
epd.lut_GC()
epd.refresh()

epd.send_command(0x50)
epd.send_data(0x17)
time.sleep(0.5)

def display_information(epd, text):
    try:
        # Create an empty image
        image = Image.new('1', (EPAPER_WIDTH, EPAPER_HEIGHT), 255)
        draw = ImageDraw.Draw(image)

        # Load the font
        font = ImageFont.truetype(FONT_PATH, 16)  # Adjust size as needed
        logging.info("Font loaded successfully.")

        # Calculate text position for center alignment
        text_width, text_height = draw.textsize(text, font=font)
        x = (EPAPER_WIDTH - text_width) // 2
        y = (EPAPER_HEIGHT - text_height) // 2

        # Draw text
        draw.text((x, y), text, font=font, fill=0)
        logging.info("Text drawn on image successfully.")

        # Display the image
        epd.display(epd.getbuffer(image))
        epd.lut_GC()
        epd.refresh()
        logging.info("Information displayed on e-paper successfully.")

    except Exception as e:
        logging.error(f"Error in display_information: {e}")

def display_dialogue(epd, left_text, right_text):
    try:
        image = Image.new('1', (EPAPER_WIDTH, EPAPER_HEIGHT), 255)
        draw = ImageDraw.Draw(image)

        font = ImageFont.truetype(FONT_PATH, 10)  # Adjust size as needed
        logging.info("Font loaded successfully.")

        # Calculate positions
        left_x = 10  # Margin
        right_x = EPAPER_WIDTH // 2 + 10
        y = 20  # Top margin

        # Draw text
        draw.text((left_x, y), left_text, font=font, fill=0)
        draw.text((right_x, y), right_text, font=font, fill=0)
        logging.info("Dialogue text drawn on image successfully.")

        # Display the image
        epd.display(epd.getbuffer(image))
        epd.lut_GC()
        epd.refresh()
        logging.info("Dialogue displayed on e-paper successfully.")

    except Exception as e:
        logging.error(f"Error in display_dialogue: {e}")

def main():
    try:
        # Initialize e-paper display
        # Example: epd.init()
        logging.info("e-Paper display initialized.")

        # Display informational text
        display_information(epd, "Hello Information")

        # Pause to view
        time.sleep(5)

        # Display dialogue text
        display_dialogue(epd, "Hello Left", "Hello Right")

        # Pause to view
        time.sleep(5)

        logging.info("Clear...")
        epd.Clear()
    
        logging.info("Goto Sleep...")
        epd.sleep()

        # Clear the display or any additional steps
        # Example: epd.sleep()
        logging.info("Finished display updates.")

    except Exception as e:
        logging.error(f"Error in main: {e}")

if __name__ == "__main__":
    main()

