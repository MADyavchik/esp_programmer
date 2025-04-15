# oled_ui.py
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from PIL import Image, ImageDraw, ImageFont
from luma.core.render import canvas


serial = i2c(port=1, address=0x3C)
device = ssd1306(serial)
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
font_select = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)

status_data = {"battery": "--%", "wifi": "--", "charging": False}

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

def draw_log_table(data):
    image = Image.new("1", device.size)
    draw = ImageDraw.Draw(image)

    draw.text((0, 0), f"B: {data['Battery']}", font=font, fill=255)
    draw.text((0, 40), f"T: {data['Temp']}", font=font, fill=255)

    draw.text((64, 0), f"H: {data['TOF']}", font=font, fill=255)
    draw.text((0, 20), f"W: {data['Weight']}", font=font, fill=255)

    device.display(image)


def update_status_data(battery, wifi, charging=False):
    global status_data
    status_data["battery"] = battery
    status_data["wifi"] = wifi
    status_data["charging"] = charging


def draw_status_bar(draw):
    draw.text((0, 0), status_data["battery"], font=font, fill=255)
    draw.text((60, 0), status_data["wifi"], font=font, fill=255)

    if status_data.get("charging"):
        x, y = 40, 0  # Координаты правее Wi-Fi
        draw.line((x+2, y+0, x+4, y+4), fill=255)
        draw.line((x+4, y+4, x+1, y+4), fill=255)
        draw.line((x+1, y+4, x+3, y+9), fill=255)

def draw_main_menu(menu_items, selected_index, scroll, visible_lines=2):
    with canvas(device) as draw:
        draw_status_bar(draw)  # Статусная строка

        for i in range(visible_lines):
            index = scroll + i
            if index >= len(menu_items):
                break
            prefix = "> " if i == 0 else "  "
            draw.text((10, 18 + i * 20), prefix + menu_items[index], font=font, fill="white")

def draw_mac_address(mac):
    clear()
    with canvas(device) as draw:
        if mac:
            draw.text((0, 0), "MAC Address:", font=font, fill="white")
            draw.text((0, 30), mac, font=font, fill="white")
        else:
            draw.text((10, 10), "Error getting MAC", font=font, fill="white")


def draw_flash_menu(items, selected_index, scroll, visible_lines=3):
    with canvas(device) as draw:
        for i in range(visible_lines):
            index = scroll + i
            if index >= len(items):
                break
            prefix = "> " if index == selected_index else "  "
            draw.text((10, 10 + i * 20), prefix + items[index], font=font, fill="white")
