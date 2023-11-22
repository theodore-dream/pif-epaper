import time
import RPi.GPIO as GPIO

def setup():
    print("setting up GPIO...")
    GPIO.setmode(GPIO.BCM)
    
    GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Button 1 input
    GPIO.setup(17, GPIO.OUT)                           # LED 1 output

    GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Button 2 input
    GPIO.setup(23, GPIO.OUT)                           # LED 2 output


# Functions to check if buttons are pressed
def left_button_pressed():
    return GPIO.input(27) == False
    

def right_button_pressed():
    return GPIO.input(16) == False


def handle_button_presses(session_id, session_state, entropy):
    setup()  # Set up the GPIO pins for buttons and LEDs

    print("Waiting for button press...")
    try:
        while True:
            # Check state for the left button and control the left LED
            if left_button_pressed():
                GPIO.output(17, True)   # Turn on LED 1
                print('Left Button Pressed...')
                time.sleep(0.5)
                pressed_button = "L"
                GPIO.output(17, False)  # Turn off LED 1
                break  # Break out of the loop since the button has been pressed
            else:
                GPIO.output(17, False)  # Turn off LED 1

            # Check state for the right button and control the right LED
            if right_button_pressed():
                GPIO.output(23, True)   # Turn on LED 2
                print('Right Button Pressed...')
                time.sleep(0.5)
                pressed_button = "R"
                GPIO.output(23, False)  # Turn off LED 2
                break  # Break out of the loop since the button has been pressed
            else:
                GPIO.output(23, False)  # Turn off LED 2

            time.sleep(0.1)  # Delay for 0.1 seconds to prevent excessive CPU usage

    except KeyboardInterrupt:  # Gracefully exit on Ctrl+C
        GPIO.cleanup()
    return pressed_button