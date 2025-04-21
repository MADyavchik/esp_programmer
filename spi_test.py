import st7789
from PIL import Image
import time

WIDTH = 240
HEIGHT = 240

disp = st7789.ST7789(
    port=0,
    cs=0,
    dc=23,
    rst=24,
    width=WIDTH,
    height=HEIGHT,
    rotation=90,
    spi_speed_hz=40000000
)

disp.begin()

# Простой экран - красный цвет
img = Image.new("RGB", (WIDTH, HEIGHT), (255, 0, 0))
disp.display(img)

time.sleep(5)

# Потом зелёный
img = Image.new("RGB", (WIDTH, HEIGHT), (0, 255, 0))
disp.display(img)

time.sleep(5)

# Потом синий
img = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 255))
disp.display(img)

time.sleep(5)
