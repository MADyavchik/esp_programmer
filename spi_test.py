import time
import ST7789 as st7789
from PIL import Image, ImageDraw, ImageFont

WIDTH = 240
HEIGHT = 240

# Инициализация дисплея (CS можно не подключать вообще физически)
disp = st7789.ST7789(
    port=0,
    cs=0,  # даже если CS нет, оставляем 0 — библиотека всё равно требует
    dc=23,
    rst=24,
    width=WIDTH,
    height=HEIGHT,
    rotation=90,
    spi_speed_hz=40000000
)

disp.begin()

# Отрисовка картинки
image = Image.new("RGB", (WIDTH, HEIGHT), "black")
draw = ImageDraw.Draw(image)
font = ImageFont.load_default()
draw.text((10, 10), "Привет, мир!", font=font, fill=(255, 255, 255))

disp.display(image)
time.sleep(10)
