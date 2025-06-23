#oled_ui.py
from PIL import Image, ImageDraw, ImageFont
import qrcode
import asyncio
import state
import time
import os
import subprocess


# ST7789
try:
    from st7789_pi import ST7789
    st_device = ST7789(width=240, height=240, dc=23, reset=24, bl=12)
    #st_device.set_backlight(True)
    #st_device.wake()
except Exception as e:
    st_device = None
    print("ST7789 init failed:", e)

# Шрифты
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
font_unselect = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
font_bold = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
font_message = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)

status_data = {"battery": "--%", "wifi": "-----", "esp_status": "   ", "charging": False}

async def inactivity_watcher(sleep_timeout=30, shutdown_timeout=60):
    backlight_on = True
    shutdown_initiated = False

    while True:
        await asyncio.sleep(1)
        elapsed = time.time() - state.last_activity_time[0]

        # Выключаем подсветку при бездействии
        if elapsed > sleep_timeout and backlight_on:
            print("💤 Пользователь бездействует, выключаем подсветку!")
            st_device.set_backlight_level(5)
            backlight_on = False

        # Включаем подсветку при активности
        elif elapsed <= sleep_timeout and not backlight_on:
            print("👆 Активность обнаружена, включаем подсветку")
            st_device.set_backlight_level(100)
            backlight_on = True

        # Завершаем работу устройства при долгом бездействии
        if elapsed > shutdown_timeout and not shutdown_initiated:
            print("⚠️ Долгое бездействие, выключаем устройство через 10 секунд...")
            shutdown_initiated = True

            for _ in range(10):
                await asyncio.sleep(1)
                if time.time() - state.last_activity_time[0] < shutdown_timeout:
                    print("❌ Действие отменено — активность обнаружена!")
                    shutdown_initiated = False
                    break
            else:
                print("⏹️ Завершение работы устройства...")
                st_device.set_backlight(False)

                # Ожидаем немного, чтобы вывести сообщение и отключить подсветку
                await asyncio.sleep(0.5)

                # Завершаем другие задачи, но shutdown выполняем после
                current = asyncio.current_task()
                for task in asyncio.all_tasks():
                    if task is not current:
                        task.cancel()

                try:
                    # Подождём немного, чтобы таски успели завершиться корректно
                    await asyncio.sleep(0.5)
                except asyncio.CancelledError:
                    pass

                # Завершаем систему
                os.system("sudo halt")
                break  # или break — если хочешь выйти из цикла


def display_on_all(image):
    if st_device:
        try:

            image_st = image.resize((240, 240), Image.Resampling.LANCZOS)

            st_device.display_image(image_st)

        except Exception as e:
            print("ST7789 display error:", e)

def clear():
    if st_device:
        try:
            st_device.fill_color(0x0000)
        except Exception as e:
            print("ST7789 clear error:", e)

def draw_progress_bar(percent, message="Flashing..."):
    image = Image.new("RGB", (240, 240), "black")
    draw = ImageDraw.Draw(image)
    bar_width = int((240 - 10) * percent / 100)
    draw.text((0, 0), f"{message} {percent}%", font=font, fill="white")
    draw.rectangle((5, 40, 240 - 5, 70), outline="white", fill=None)
    draw.rectangle((5, 40, 5 + bar_width, 70), outline="white", fill="yellow")
    display_on_all(image)

def show_message(text):
    from textwrap import wrap

    image = Image.new("RGB", (240, 240), "black")
    draw = ImageDraw.Draw(image)

    # Фиксированная ширина прямоугольника
    rect_w = 220
    max_text_width = rect_w - 20  # по 10 пикселей отступа с каждой стороны

    # Разбивка текста на строки с учётом ширины
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + " " + word if current_line else word
        bbox = draw.textbbox((0, 0), test_line, font=font_message)
        line_width = bbox[2] - bbox[0]
        if line_width <= max_text_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)

    # Подсчёт высоты текста
    line_height = font_message.getbbox("Ay")[3] + 4
    total_text_height = line_height * len(lines)
    rect_h = total_text_height + 20  # отступ сверху и снизу по 10px

    # Центровка прямоугольника по экрану
    rect_x1 = (240 - rect_w) // 2
    rect_y1 = (240 - rect_h) // 2
    rect_x2 = rect_x1 + rect_w
    rect_y2 = rect_y1 + rect_h

    # Нарисовать прямоугольник
    draw.rounded_rectangle(
        [(rect_x1, rect_y1), (rect_x2, rect_y2)],
        radius=15,
        outline="yellow",
        width=3,
        fill="yellow"
    )

    # Центровка текста по вертикали внутри прямоугольника
    y_text_start = rect_y1 + 10  # отступ сверху

    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font_message)
        line_width = bbox[2] - bbox[0]
        x = rect_x1 + (rect_w - line_width) // 2
        y = y_text_start + i * line_height
        draw.text((x, y), line, font=font_message, fill="black")

    display_on_all(image)

def draw_log_table(data):

    print("🎨 draw_log_table called with:", data)  # DEBUG

    image = Image.new("RGB", (240, 240), "grey")
    draw = ImageDraw.Draw(image)

    draw.rectangle((0, 0, 239, 40), outline="black", fill=data['Battery']['status'])
    draw.text((0, 0), f"BATT: {data['Battery']['value']}", font=font, fill="black")

    draw.rectangle((0, 40, 239, 80), outline="black", fill=data['Weight']['status'])
    draw.text((0, 40), f"W: {data['Weight']['value']}", font=font, fill="black")

    #draw.text((0, 40), f"W: {data['Weight']}", font=font, fill="white")

    draw.text((0, 80), f"TEMP: {data['Temp']['value']}", font=font, fill=data['Temp']['status'])
    #draw.text((0, 80), f"TEMP: {data['Temp']}", font=font, fill="white")

    draw.text((0, 120), f"TOF: {data['TOF']['value']}", font=font, fill=data['TOF']['status'])
    #draw.text((0, 120), f"TOF: {data['TOF']}", font=font, fill="white")


    draw.rectangle((0, 160, 239, 200), outline="black", fill=data['CPU Temp']['status'])
    draw.text((0, 160), f"CPU t: {data['CPU Temp']['value']}", font=font, fill="black")
    #draw.text((0, 160), f"CPU t: {data['CPU Temp']}", font=font, fill="white")

    draw.text((0, 200), f"RSSI: {data['DOM.Online']['value']}", font=font, fill=data['DOM.Online']['status'])
    #draw.text((0, 200), f"RSSI: {data['DOM.Online']}", font=font, fill="white")

    display_on_all(image)

def update_status_data(battery, wifi, charging=False):
    global status_data
    status_data["battery"] = battery
    status_data["wifi"] = wifi
    status_data["charging"] = charging
    #status_data["esp_status"] = esp_status

def draw_status_bar(draw):
    draw.text((0, 0), status_data["battery"], font=font_unselect, fill="white")
    #draw.text((90, 0), status_data["esp_status"], font=font_unselect, fill="white")
    draw.text((160, 0), status_data["wifi"], font=font_unselect, fill="white")
    if status_data.get("charging"):
        x, y = 70, 0
        draw.line((x+2, y+0, x+8, y+8), fill="yellow")
        draw.line((x+8, y+8, x+2, y+8), fill="yellow")
        draw.line((x+2, y+8, x+8, y+16), fill="yellow")



def draw_mac_address(mac):
    image = Image.new("RGB", (240, 240), "black")
    draw = ImageDraw.Draw(image)
    if mac:
        draw.text((0, 0), "MAC Address:", font=font, fill="white")
        draw.text((0, 30), mac, font=font, fill="white")
    else:
        draw.text((10, 10), "Error getting MAC", font=font, fill="white")
    display_on_all(image)



def draw_mac_qr(mac):
    # Создаём QR-код
    qr = qrcode.QRCode(border=1)
    qr.add_data(mac)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="white", back_color="black").convert("RGB")
    qr_img = qr_img.resize((80, 80), Image.NEAREST)

    # Создаём изображение для вывода (размер 240x240)
    image = Image.new("RGB", (240, 240), "black")
    draw = ImageDraw.Draw(image)

    # Получаем размеры изображения с QR-кодом
    qr_width, qr_height = qr_img.size

    # Рисуем QR-код в центре изображения
    x_offset = (240 - qr_width) // 2
    y_offset = (240 - qr_height) // 2
    image.paste(qr_img, (x_offset, y_offset))

    # Вычисляем размер и позицию для текста
    bbox = draw.textbbox((0, 0), mac, font=font_unselect)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Позиция текста: немного ниже QR-кода
    x_position = (240 - text_width) // 2
    y_position = y_offset + qr_height + 10  # Немного отступаем от QR-кода

    # Рисуем текст (MAC-адрес) на изображении
    draw.text((x_position, y_position), mac, font=font_unselect, fill="white")

    # Возвращаем изображение с QR-кодом и MAC-адресом
    display_on_all(image)


def draw_menu(
    items,
    selected_index,
    scroll=0,
    visible_lines=None,
    highlight_color="yellow",
    show_back_button=False
):
    image = Image.new("RGB", (240, 240), "black")
    draw = ImageDraw.Draw(image)

    # Сначала всегда статус-бар
    draw_status_bar(draw)

    y_offset = 40  # статус-бар занимает 40 пикселей

    if show_back_button:
        # Рисуем жёлтый круг
        center_x, center_y = 24, y_offset + 24
        radius = 15
        draw.ellipse(
            (center_x - radius, center_y - radius, center_x + radius, center_y + radius),
            fill="black"
        )
        draw.line(
            [(center_x + 4, center_y - 10), (center_x - 6, center_y), (center_x + 4, center_y + 10)],
            fill="yellow",
            width=4
        )
        y_offset += 45

    line_height = 42
    radius = line_height // 2

    if visible_lines is None:
        visible_lines = len(items)

    for i in range(visible_lines):
        index = scroll + i
        if index >= len(items):
            break  # если индекс вышел за пределы списка, остановить рисование

        y = y_offset + i * line_height

        if index == selected_index:
            draw.rounded_rectangle(
                (5, y - 2, 235, y + line_height - 10),
                radius=radius,
                fill=highlight_color
            )
            draw.text((30, y), items[index], font=font_bold, fill="black")
        else:
            draw.text((30, y), items[index], font=font_unselect, fill="grey")

    display_on_all(image)

async def animate_activity(stop_event, message="Printing..."):
    bar_count = 5
    width = 240
    height = 240
    bar_width = 10
    spacing = 15
    center_y = height // 2
    max_bar_height = 60
    min_bar_height = 20
    step = 5

    # координаты X для пяти столбиков, равномерно распределенных по центру
    start_x = (width - ((bar_count - 1) * spacing + bar_count * bar_width)) // 2
    bar_xs = [start_x + i * (bar_width + spacing) for i in range(bar_count)]
    heights = [min_bar_height] * bar_count
    directions = [1] * bar_count

    tick = 0
    while not stop_event.is_set():
        image = Image.new("RGB", (width, height), "black")
        draw = ImageDraw.Draw(image)

        # текст сверху
        draw.text((10, 10), message, font=font, fill="white")

        for i in range(bar_count):
            # волнообразное движение по очереди
            if tick % bar_count == i:
                heights[i] += step * directions[i]
                if heights[i] >= max_bar_height or heights[i] <= min_bar_height:
                    directions[i] *= -1  # реверс направления

            bar_height = heights[i]
            x = bar_xs[i]
            y_top = center_y - bar_height // 2
            y_bottom = center_y + bar_height // 2

            draw.rectangle((x, y_top, x + bar_width, y_bottom), fill="yellow")

        display_on_all(image)
        tick += 1
        await asyncio.sleep(0.1)


