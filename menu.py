import time
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

# Кнопки с debounce
btn_up = Button(5, bounce_time=0.2)
btn_down = Button(6, bounce_time=0.2)
btn_back = Button(19, bounce_time=0.2)
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

# Обработчики кнопок (с циклической прокруткой и логами)
def button_up_pressed():
    global selected_item
    selected_item = (selected_item - 1) % len(menu_items)
    print(f"[UP] selected_item: {selected_item}")
    draw_menu()

def button_down_pressed():
    global selected_item
    selected_item = (selected_item + 1) % len(menu_items)
    print(f"[DOWN] selected_item: {selected_item}")
    draw_menu()

def button_back_pressed():
    global selected_item
    selected_item = 0
    print("[BACK] Reset to 0")
    draw_menu()

def button_select_pressed():
    print(f"[SELECT] on item: {menu_items[selected_item]}")
    with canvas(device) as draw:
        if selected_item == 0:
            draw.text((10, 10), "Выбор прошивки", font=font, fill="white")
        elif selected_item == 1:
            draw.text((10, 10), "Обновление...", font=font, fill="white")
    time.sleep(2)
    draw_menu()

# Привязка обработчиков
btn_up.when_pressed = button_up_pressed
btn_down.when_pressed = button_down_pressed
btn_back.when_pressed = button_back_pressed
btn_select.when_pressed = button_select_pressed

# Стартовое меню
draw_menu()

# Цикл (можно пустой — gpiozero сам обрабатывает кнопки)
while True:
    time.sleep(0.01)
