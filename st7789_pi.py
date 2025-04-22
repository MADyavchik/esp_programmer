# st7789_pi.py

import spidev
import RPi.GPIO as GPIO
import time
import numpy as np

class ST7789:
    def __init__(self, spi_bus=0, spi_device=0, dc=23, reset=24, bl=25, width=240, height=240):
        self.width = width
        self.height = height
        self.spi = spidev.SpiDev()
        self.spi.open(spi_bus, spi_device)
        self.spi.max_speed_hz = 62500000  # 62.5 MHz
        self.spi.mode = 0

        self.dc = dc
        self.reset = reset
        self.bl = bl

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.dc, GPIO.OUT)
        GPIO.setup(self.reset, GPIO.OUT)
        GPIO.setup(self.bl, GPIO.OUT)

        self.reset_display()
        self.init_display()
        self.set_backlight(True)

    def reset_display(self):
        GPIO.output(self.reset, GPIO.HIGH)
        time.sleep(0.1)
        GPIO.output(self.reset, GPIO.LOW)
        time.sleep(0.1)
        GPIO.output(self.reset, GPIO.HIGH)
        time.sleep(0.1)

    def write_cmd(self, cmd):
        GPIO.output(self.dc, GPIO.LOW)
        self.spi.writebytes([cmd])

    def write_data(self, data):
        GPIO.output(self.dc, GPIO.HIGH)
        if isinstance(data, int):
            data = [data]
        self.spi.writebytes(data)

    def set_backlight(self, on=True):
        GPIO.output(self.bl, GPIO.HIGH if on else GPIO.LOW)

    def init_display(self):
        # Простая инициализация (можно заменить более полной)
        self.write_cmd(0x36)
        self.write_data(0x70)
        self.write_cmd(0x3A)
        self.write_data(0x05)  # RGB565

        self.write_cmd(0x21)  # Inversion ON
        self.write_cmd(0x11)
        time.sleep(0.12)
        self.write_cmd(0x29)

    def fill_color(self, color):
        self.set_window(0, 0, self.width, self.height)
        pixel_count = self.width * self.height
        buf = [color >> 8, color & 0xFF] * pixel_count
        self.write_cmd(0x2C)
        self.write_data(buf)

    def set_window(self, x0, y0, x1, y1):
        self.write_cmd(0x2A)
        self.write_data([x0 >> 8, x0 & 0xFF, x1 >> 8, x1 & 0xFF])
        self.write_cmd(0x2B)
        self.write_data([y0 >> 8, y0 & 0xFF, y1 >> 8, y1 & 0xFF])

    def color565(self, r, g, b):
        return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
