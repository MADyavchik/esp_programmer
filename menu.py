import time
import os
from gpiozero import Button
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from luma.core.render import canvas
from PIL import ImageFont

# Настройка дисплея
serial = i2c(port=1, address=0x3C)
device = ssd1306(serial)

# Подгружаем шрифт
try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
except:
    font = ImageFont.load_default()

# Кнопки (номер пинов может быть другим у тебя — проверь!)
btn_up = Button(5, bounce_time=0.2)
btn_down = Button(6, bounce_time=0.2)
btn_back = Button(19, bounce_time=0.2, hold_time=3)  # добавили hold_time
btn_select = Button(26, bounce_time=0.2)

# Пункты меню
menu_items = ["FLASH", "UPDATE"]
selected_item = 0

# Функция отрисовки меню
def draw_menu():
    with canvas(device) as draw:
        for i, item in enumerate(menu_items):
            prefix = "> " if i == selected_item else "  "
            draw.text((10, 10 + i * 20), prefix + item, font=font, fill="white")

# Функция для перезагрузки
def reboot_pi():
    with canvas(device) as draw:
        draw.text((10, 10), "Перезагрузка...", font=font, fill="white")
    time.sleep(1)
    os.system("sudo reboot")

# Обработчики кнопок (циклическая прокрутка)
def button_up_pressed():
    global selected_item
    selected_item = (selected_item - 1) % len(menu_items)
    draw_menu()

def button_down_pressed():
    global selected_item
    selected_item = (selected_item + 1) % len(menu_items)
    draw_menu()

def button_back_pressed():
    global selected_item
    selected_item = 0
    draw_menu()

def button_select_pressed():
    if selected_item == 1:  # Если выбрали пункт обновления
        from git_update import update_repo
        update_repo()
    else:
        # Добавьте логику для пункта "FLASH" если нужно
        pass

# Привязка обработчиков
btn_up.when_pressed = button_up_pressed
btn_down.when_pressed = button_down_pressed
btn_back.when_pressed = button_back_pressed
btn_back.when_held = reboot_pi  # при удержании 3 сек — перезагрузка
btn_select.when_pressed = button_select_pressed

# Стартовое меню
draw_menu()
