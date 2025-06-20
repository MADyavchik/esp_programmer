# spi_test.py

from st7789_pi import ST7789
import time

disp = ST7789()

print("🔆 Включаем подсветку на 3 секунды")
disp.set_backlight(True)
time.sleep(3)

print("🌑 Выключаем подсветку на 3 секунды")
disp.set_backlight(False)
time.sleep(3)

print("🔁 Повтор")
disp.set_backlight(True)
