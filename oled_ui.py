from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from PIL import Image, ImageDraw, ImageFont

# Инициализация экрана
serial = i2c(port=1, address=0x3C)
device = ssd1306(serial)
font = ImageFont.load_default()

def clear():
    device.clear()
    device.show()

def draw_progress_bar(percent, message="Flashing..."):
    width = device.width
    height = device.height

    image = Image.new("1", (width, height))
    draw = ImageDraw.Draw(image)

    bar_width = int((width - 10) * percent / 100)

    draw.text((0, 0), f"{message} {percent}%", font=font, fill=255)
    draw.rectangle((5, 20, width - 5, 35), outline=255, fill=0)
    draw.rectangle((5, 20, 5 + bar_width, 35), outline=255, fill=255)

    device.display(image)


def show_message(text):
    image = Image.new("1", device.size)
    draw = ImageDraw.Draw(image)
    draw.text((0, 0), text, font=font, fill=255)
    device.display(image)

    device.display(image)
