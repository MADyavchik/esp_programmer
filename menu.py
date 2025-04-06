import time
from luma.core.render import canvas
from luma.oled.device import ssd1306
from luma.core.interface.serial import i2c
from PIL import ImageFont
from gpiozero import Button

# Настройка дисплея
serial = i2c(port=1, address=0x3C)  # Подключение через I2C
device = ssd1306(serial)  # Инициализация устройства SSD1306

# Настройка шрифта
try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
except:
    font = ImageFont.load_default()

# Настройка кнопок
btn_up = Button(5)    # Кнопка вверх
btn_down = Button(6)  # Кнопка вниз
btn_back = Button(19) # Кнопка назад
btn_select = Button(26)  # Кнопка подтвердить

# Меню
menu_items = ["FLASH", "UPDATE"]
selected_item = 0

# Функция для отрисовки главного меню
def draw_menu():
    with canvas(device) as draw:
        draw.rectangle(device.bounding_box, outline="white", fill="black")  # Очистить экран
        for i, item in enumerate(menu_items):
            if i == selected_item:
                draw.text((10, 10 + i * 20), f"> {item}", font=font, fill="white")  # Выделить выбранный пункт
            else:
                draw.text((10, 10 + i * 20), item, font=font, fill="white")  # Отобразить остальные пункты

# Обработчики кнопок
def button_up_pressed():
    global selected_item
    if selected_item > 0:
        selected_item -= 1
    draw_menu()

def button_down_pressed():
    global selected_item
    if selected_item < len(menu_items) - 1:
        selected_item += 1
    draw_menu()

def button_back_pressed():
    global selected_item
    selected_item = 0  # Возвращаемся в начало
    draw_menu()

def button_select_pressed():
    with canvas(device) as draw:
        if selected_item == 0:
            draw.text((10, 10), "Выбор прошивки", font=font, fill="white")
        elif selected_item == 1:
            draw.text((10, 10), "Обновление...", font=font, fill="white")
        time.sleep(2)  # Заглушка на обновление
    draw_menu()

# Подключаем обработчики
btn_up.when_pressed = button_up_pressed
btn_down.when_pressed = button_down_pressed
btn_back.when_pressed = button_back_pressed
btn_select.when_pressed = button_select_pressed

# Изначальная отрисовка меню
draw_menu()

# Бесконечный цикл, чтобы обновлять экран и следить за кнопками
while True:
    time.sleep(0.1)
