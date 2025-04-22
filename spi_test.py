# spi_test.py

from st7789_pi import ST7789
import time

disp = ST7789(width=240, height=240, dc=23, reset=24, bl=25)

# Заполни экран синим
blue = disp.color565(0, 0, 255)
disp.fill_color(blue)

time.sleep(5)

# Заполни экран красным
red = disp.color565(255, 0, 0)
disp.fill_color(red)

time.sleep(5)
