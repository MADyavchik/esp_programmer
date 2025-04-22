# oled_ui.py
from PIL import Image, ImageDraw, ImageFont
import qrcode

# OLED через luma
try:
    from luma.core.interface.serial import i2c
    from luma.oled.device import ssd1306
    from luma.core.render import canvas
    serial = i2c(port=1, address=0x3C)
    oled_device = ssd1306(serial)
except Exception as e:
    oled_device = None
    print("OLED init failed:", e)

# ST7789
try:
    from st7789_pi import ST7789
    st_device = ST7789(width=240, height=240, dc=23, reset=24, bl=25)
except Exception as e:
    st_device = None
    print("ST7789 init failed:", e)

# Шрифты
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
font_unselect = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
font_bold = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)

status_data = {"battery": "--%", "wifi": "--", "charging": False}

def display_on_all(image):
    """Показываем картинку на всех экранах"""

    # Приводим картинку к нужному размеру для OLED
    if oled_device:
        try:
            # Приводим к нужному размеру для OLED экрана (128x64 по умолчанию)
            image_oled = image.resize(oled_device.size).convert("1")
            oled_device.display(image_oled)
        except Exception as e:
            print("OLED display error:", e)

    # Для ST7789 экрана, преобразуем картинку в RGB и отображаем
    if st_device:
        try:
            # Приводим изображение к размеру экрана ST7789 (240x240 или иной размер)
            image_st = image.resize((240, 240))  # Здесь можно указать свой размер экрана для ST7789
            st_device.display_image(image_st)
        except Exception as e:
            print("ST7789 display error:", e)

def clear():
    if oled_device:
        try:
            oled_device.clear()
            oled_device.show()
        except Exception as e:
            print("OLED clear error:", e)
    if st_device:
        try:
            st_device.fill_color(0x0000)  # черный
        except Exception as e:
            print("ST7789 clear error:", e)

def draw_progress_bar(percent, message="Flashing..."):
    image = Image.new("RGB", (240, 240), "black")
    draw = ImageDraw.Draw(image)

    bar_width = int((240 - 10) * percent / 100)
    draw.text((0, 0), f"{message} {percent}%", font=font, fill="white")
    draw.rectangle((5, 20, 240 - 5, 35), outline="white", fill=None)
    draw.rectangle((5, 20, 5 + bar_width, 35), outline="white", fill="white")

    display_on_all(image)

def show_message(text):
    image = Image.new("RGB", (240, 240), "black")
    draw = ImageDraw.Draw(image)
    draw.text((10, 10), text, font=font, fill="white")

    display_on_all(image)

def draw_log_table(data):
    image = Image.new("RGB", (240, 240), "black")
    draw = ImageDraw.Draw(image)

    draw.text((0, 0), f"B: {data['Battery']}", font=font, fill="white")
    draw.text((0, 40), f"T: {data['Temp']}", font=font, fill="white")
    draw.text((64, 0), f"H: {data['TOF']}", font=font, fill="white")
    draw.text((0, 20), f"W: {data['Weight']}", font=font, fill="white")

    display_on_all(image)

def update_status_data(battery, wifi, charging=False):
    global status_data
    status_data["battery"] = battery
    status_data["wifi"] = wifi
    status_data["charging"] = charging

def draw_status_bar(draw):
    draw.text((0, 0), status_data["battery"], font=font_unselect, fill="white")
    draw.text((60, 0), status_data["wifi"], font=font_unselect, fill="white")

    if status_data.get("charging"):
        x, y = 40, 0
        draw.line((x+2, y+0, x+4, y+4), fill="white")
        draw.line((x+4, y+4, x+1, y+4), fill="white")
        draw.line((x+1, y+4, x+3, y+9), fill="white")

def draw_main_menu(menu_items, selected_index, scroll, visible_lines=2):
    image = Image.new("RGB", (240, 240), "black")
    draw = ImageDraw.Draw(image)

    draw_status_bar(draw)

    for i in range(visible_lines):
        index = (scroll + i) % len(menu_items)
        y = 18 + i * 20

        if i == 0:
            draw.rectangle((0, y - 2, 240, y + 16), fill="white")
            draw.text((10, y), menu_items[index], font=font_bold, fill="black")
        else:
            draw.text((10, y), menu_items[index], font=font_unselect, fill="white")

    display_on_all(image)

def draw_mac_address(mac):
    image = Image.new("RGB", (240, 240), "black")
    draw = ImageDraw.Draw(image)

    if mac:
        draw.text((0, 0), "MAC Address:", font=font, fill="white")
        draw.text((0, 30), mac, font=font, fill="white")
    else:
        draw.text((10, 10), "Error getting MAC", font=font, fill="white")

    display_on_all(image)

def draw_flash_menu(items, selected_index, scroll, visible_lines=2):
    image = Image.new("RGB", (240, 240), "black")
    draw = ImageDraw.Draw(image)

    draw.text((5, 0), "< menu", font=font_unselect, fill="white")

    for i in range(visible_lines):
        index = (scroll + i) % len(items)
        y = 18 + i * 20

        if index == selected_index:
            draw.rectangle((0, y - 2, 240, y + 16), fill="white")
            draw.text((10, y), items[index], font=font_bold, fill="black")
        else:
            draw.text((10, y), items[index], font=font_unselect, fill="white")

    display_on_all(image)

def draw_mac_qr(mac):
    qr = qrcode.QRCode(border=1)
    qr.add_data(mac)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color="white", back_color="black").convert("RGB")
    qr_img = qr_img.resize((80, 80), Image.NEAREST)

    image = Image.new("RGB", (240, 240), "black")
    draw = ImageDraw.Draw(image)

    dummy = Image.new("RGB", (240, 240))
    dummy_draw = ImageDraw.Draw(dummy)
    bbox = dummy_draw.textbbox((0, 0), mac, font=font_unselect)
    text_width = bbox[2] - bbox[0]
    x = 120 - text_width // 2
    draw.text((x, 10), mac, font=font_unselect, fill="white")

    image.paste(qr_img, (80, 60))

    display_on_all(image)
