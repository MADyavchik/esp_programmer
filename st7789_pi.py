# st7789_pi.py

import spidev
import RPi.GPIO as GPIO
import time
import array
import numpy as np

class ST7789:
    def __init__(self, spi_bus=0, spi_device=0, dc=23, reset=24, bl=25, width=240, height=240, pwm_freq=10000):
        self.width = width
        self.height = height
        self.spi = spidev.SpiDev()
        self.spi.open(spi_bus, spi_device)
        self.spi.max_speed_hz = 30000000  # 30 MHz
        self.spi.mode = 3

        self.dc = dc
        self.reset = reset
        self.bl = bl

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.dc, GPIO.OUT)
        GPIO.setup(self.reset, GPIO.OUT)
        GPIO.setup(self.bl, GPIO.OUT)

        self.pwm = GPIO.PWM(bl, pwm_freq)
        self.pwm.start(100)  # Стартуем с полной яркостью

        self.reset_display()
        self.init_display()
        self.set_backlight(True)

    def reset_display(self):
        GPIO.output(self.reset, GPIO.HIGH)
        time.sleep(0.1)
        GPIO.output(self.reset, GPIO.LOW)
        time.sleep(0.1)
        GPIO.output(self.reset, GPIO.HIGH)
        time.sleep(0.2)

    def write_cmd(self, cmd):
        GPIO.output(self.dc, GPIO.LOW)
        self.spi.writebytes([cmd])

    def write_data(self, data):
        GPIO.output(self.dc, GPIO.HIGH)
        if isinstance(data, int):
            data = [data]
        max_chunk = 4096
        for i in range(0, len(data), max_chunk):
            self.spi.writebytes(data[i:i + max_chunk])

    def set_backlight(self, on=True):
        """Полное включение/выключение подсветки"""
        self.pwm.ChangeDutyCycle(100 if on else 0)

    def set_backlight_level(self, level_percent):
        """Регулировка яркости от 0 до 100%"""
        print(f"🔆 Меняем яркость на {level_percent}%")
        level = max(0, min(100, level_percent))
        self.pwm.ChangeDutyCycle(level)

    #def set_backlight(self, on=True):
        #GPIO.output(self.bl, GPIO.HIGH if on else GPIO.LOW)

    def init_display(self):
        self.write_cmd(0x36)
        self.write_data(0x00)  # Orientation (0x00 = default, try 0x70 or 0xC0 if изображение повернуто)

        self.write_cmd(0x3A)
        self.write_data(0x05)  # RGB565

        self.write_cmd(0x21)  # Inversion ON
        self.write_cmd(0x11)  # Sleep Out
        time.sleep(0.15)
        self.write_cmd(0x29)  # Display ON
        time.sleep(0.1)

        #self.fill_color(0x0000)

    def set_window(self, x0, y0, x1, y1):
        self.write_cmd(0x2A)
        self.write_data([x0 >> 8, x0 & 0xFF, x1 >> 8, x1 & 0xFF])
        self.write_cmd(0x2B)
        self.write_data([y0 >> 8, y0 & 0xFF, y1 >> 8, y1 & 0xFF])
        self.write_cmd(0x2C)

    def fill_color(self, color):
        self.set_window(0, 0, self.width - 1, self.height - 1)
        pixel_count = self.width * self.height
        color_hi = color >> 8
        color_lo = color & 0xFF
        buf = array.array('B', [color_hi, color_lo] * pixel_count)
        self.write_data(buf)

    def color565(self, r, g, b):
        return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)

    def display_image(self, image):
        image = image.resize((self.width, self.height))  # на всякий случай
        rgb565 = self.convert_image_to_rgb565(image)
        self.set_window(0, 0, self.width, self.height)
        self.write_cmd(0x2C)
        self.write_data(rgb565)

    def convert_image_to_rgb565(self, image):
        image = image.convert("RGB")
        arr = np.array(image)
        r = (arr[:, :, 0] >> 3).astype(np.uint16)
        g = (arr[:, :, 1] >> 2).astype(np.uint16)
        b = (arr[:, :, 2] >> 3).astype(np.uint16)
        rgb565 = (r << 11) | (g << 5) | b
        result = np.dstack(((rgb565 >> 8) & 0xFF, rgb565 & 0xFF)).flatten().tolist()
        return result

    def sleep(self):
        self.write_cmd(0x28)  # Display OFF
        time.sleep(0.05)
        self.write_cmd(0x10)  # Sleep IN
        time.sleep(0.1)

    def wake(self):
        self.write_cmd(0x11)  # Sleep OUT
        time.sleep(0.12)
        self.write_cmd(0x29)  # Display ON
