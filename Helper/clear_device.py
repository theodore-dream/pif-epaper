#!/usr/bin/env python3

import time
import logging

from luma.core.interface.serial import spi
from luma.oled.device import ssd1351

# setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('luma_log')

serial = spi(device=0, port=0)
device = ssd1351(serial)

def clear_device():
    logger.info("clearing device")
    device.clear()
    logger.info("device cleared, function completed successfully")

if __name__ == "__main__":
    clear_device()

