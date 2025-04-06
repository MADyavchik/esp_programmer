import time
from gpiozero import Button
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from luma.core.render import canvas
from PIL import ImageFont
from git_update import update_repo  # Импортируем функцию для обновления репозитория

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

# Функция отображения статуса
def display_status(message, y_position=10):
    with canvas(device) as draw:
        draw.text((10, y_position), message, font=font, fill="white")

# Обработчики кнопок
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
    if selected_item == 0:
        display_status("Выбор прошивки", 10)
        draw_menu()
    elif selected_item == 1:
        # Начинаем обновление репозитория
        display_status("Обновление начато...", 10)
        draw_menu()

        stdout, stderr = update_repo()  # Вызываем обновление через git_update.py

        if stdout:
            # Если обновление прошло успешно, показываем успех
            display_status("Обновление завершено!", 10)
        elif stderr:
            # Если произошла ошибка, показываем ошибку
            display_status(f"Ошибка: {stderr}", 10)
        else:
            # Если произошла неизвестная ошибка
            display_status("Неизвестная ошибка", 10)

        time.sleep(2)  # Показываем результат несколько секунд
        draw_menu()  # Обновляем меню

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
