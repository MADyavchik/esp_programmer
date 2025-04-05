import time
import board
import digitalio
from adafruit_ssd1306 import SSD1306_I2C
from gpiozero import Button

# Настройка дисплея
i2c = board.I2C()
oled = SSD1306_I2C(128, 64, i2c)

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
    oled.fill(0)  # Очистить экран
    for i, item in enumerate(menu_items):
        if i == selected_item:
            oled.text(f"> {item}", 10, 10 + i * 20, 1)  # Выделить выбранный пункт
        else:
            oled.text(item, 10, 10 + i * 20, 1)  # Отобразить остальные пункты
    oled.show()

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
    if selected_item == 0:
        oled.fill(0)
        oled.text("Выбор прошивки", 10, 10)
        oled.show()
        time.sleep(2)  # Заглушка на переход, можно добавить логику выбора прошивки
    elif selected_item == 1:
        oled.fill(0)
        oled.text("Обновление...", 10, 10)
        oled.show()
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
