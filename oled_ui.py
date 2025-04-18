# oled_ui.py
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from PIL import Image, ImageDraw, ImageFont
from luma.core.render import canvas
import qrcode


serial = i2c(port=1, address=0x3C)
device = ssd1306(serial)
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
font_unselect = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
font_bold = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)

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
    draw.text((0, 0), status_data["battery"], font=font_unselect, fill=255)
    draw.text((60, 0), status_data["wifi"], font=font_unselect, fill=255)

    if status_data.get("charging"):
        x, y = 40, 0  # Координаты правее Wi-Fi
        draw.line((x+2, y+0, x+4, y+4), fill=255)
        draw.line((x+4, y+4, x+1, y+4), fill=255)
        draw.line((x+1, y+4, x+3, y+9), fill=255)

def draw_main_menu(menu_items, selected_index, scroll, visible_lines=2):
    with canvas(device) as draw:
        draw_status_bar(draw)

        for i in range(visible_lines):
            index = (scroll + i) % len(menu_items)
            y = 18 + i * 20

            if i == 0:  # Выделяем всегда первый видимый пункт
                draw.rectangle((0, y - 2, 127, y + 16), fill=255)
                draw.text((10, y), menu_items[index], font=font_bold, fill=0)
            else:
                draw.text((10, y), menu_items[index], font=font_unselect, fill=255)
def draw_mac_address(mac):
    clear()
    with canvas(device) as draw:
        if mac:
            draw.text((0, 0), "MAC Address:", font=font, fill="white")
            draw.text((0, 30), mac, font=font, fill="white")
        else:
            draw.text((10, 10), "Error getting MAC", font=font, fill="white")


def draw_flash_menu(items, selected_index, scroll, visible_lines=2):
    with canvas(device) as draw:
        # Заголовок "< menu"
        draw.text((5, 0), "< menu", font=font_unselect, fill=255)

        for i in range(visible_lines):
            index = (scroll + i) % len(items)
            y = 18 + i * 20  # отрисовка начинается ниже заголовка

            if index == selected_index:
                draw.rectangle((0, y - 2, 127, y + 16), fill=255)
                draw.text((10, y), items[index], font=font_bold, fill=0)
            else:
                draw.text((10, y), items[index], font=font_unselect, fill=255)

def draw_mac_qr(mac):
    qr = qrcode.QRCode(border=1)
    qr.add_data(mac)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color="white", back_color="black").convert("1")
    qr_img = qr_img.resize((50, 50), Image.NEAREST)

    with canvas(device) as draw:
        # Надёжный способ центрирования текста
        dummy_img = Image.new("1", (128, 64))
        dummy_draw = ImageDraw.Draw(dummy_img)
        bbox = dummy_draw.textbbox((0, 0), mac, font=font_unselect)
        text_width = bbox[2] - bbox[0]

        x = 64 - text_width // 2
        draw.text((x, 0), mac, font=font_unselect, fill=255)

        # Отображаем QR-код под текстом
        draw.bitmap((39, 14), qr_img, fill=1)
