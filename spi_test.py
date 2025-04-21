import time
import digitalio
import board
import adafruit_st7789
from PIL import Image, ImageDraw, ImageFont

# Настройка пинов
dc_pin = digitalio.DigitalInOut(board.D23)
reset_pin = digitalio.DigitalInOut(board.D24)

# Инициализация SPI
spi = board.SPI()

# Инициализация дисплея без CS
display = adafruit_st7789.ST7789(
    spi,
    dc=dc_pin,
    rst=reset_pin,
    width=240,
    height=240,
    rotation=90,
    cs=None,  # ВАЖНО: если нет пина CS
)

# Пауза на инициализацию
time.sleep(0.5)

# Создаем изображение
image = Image.new("RGB", (240, 240), "black")
draw = ImageDraw.Draw(image)
font = ImageFont.load_default()
draw.text((10, 10), "Привет, мир!", font=font, fill=(255, 255, 255))

# Отправляем изображение на экран
display.image(image)
