# flash_menu.py
import time
from luma.core.render import canvas
from buttons import setup_buttons  # Импортируем настройки кнопок
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from PIL import ImageFont

# Настройка дисплея
serial = i2c(port=1, address=0x3C)
device = ssd1306(serial)

# Подгружаем шрифт
try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
except:
    font = ImageFont.load_default()

# Пункты меню
menu_items = ["Universal", "Master", "Repiater", "Sens_SW", "Sensor"]
selected_item = [0]  # Используем список для передачи по ссылке

# Функция отрисовки меню
def flash_draw_menu():
    with canvas(device) as draw:
        for i, item in enumerate(menu_items):
            prefix = "> " if i == selected_item[0] else "  "
            draw.text((10, 10 + i * 20), prefix + item, font=font, fill="white")


# Обработчики для меню
def button_up_pressed():
    selected_item[0] = (selected_item[0] - 1) % len(menu_items)
    flash_draw_menu()

def button_down_pressed():
    selected_item[0] = (selected_item[0] + 1) % len(menu_items)
    flash_draw_menu()

def button_back_pressed():
    selected_item[0] = 0
    flash_draw_menu()

def button_select_pressed():
    if selected_item[0] == 1:  # Если выбрали пункт обновления
        print("Обновление начнется...")
    else:
        print("Выбран пункт FLASH")

# Привязка кнопок
setup_buttons(button_up_pressed, button_down_pressed, button_back_pressed, button_select_pressed, back_hold_action=reboot_pi)

# Стартовое меню
flash_draw_menu()

# Основной цикл программы
while True:
    time.sleep(0.1)
