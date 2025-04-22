import time
import st7789
import RPi.GPIO as GPIO

# Пины для подключения дисплея
DC = 9
RST = 8
BL = 7  # Пин подсветки, если есть

# Инициализация дисплея
disp = st7789.ST7789(
    port=0,
    cs=st7789.CS0,
    dc=DC,
    rst=RST,
    bl=BL,
    width=240,
    height=240,
    rotation=0  # Повернуть дисплей, если нужно
)

disp.begin()

# Очищаем экран
disp.fill(0)  # Черный фон

# Выводим текст на экран
disp.text('Hello, World!', 50, 50, st7789.WHITE)

# Ждем 5 секунд
time.sleep(5)

# Выключаем дисплей
disp.fill(0)  # Очищаем экран
