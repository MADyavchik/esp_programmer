#screens/shotdown_screen.py

import asyncio
import os
import time
import state
from oled_ui import show_message

from st7789_pi import ST7789
st_device = ST7789(width=240, height=240, dc=23, reset=24, bl=12)

async def run_shotdown_halt():
    print("⚠️ Без активности. Запуск таймера выключения...")

    countdown = 10
    shutdown_start = time.time()
    last_displayed = None

    while True:
        now = time.time()
        activity_elapsed = now - state.last_activity_time[0]
        elapsed_since_start = now - shutdown_start

        # Если пользователь проявил активность — отмена
        if activity_elapsed < elapsed_since_start:
            print("❌ Действие отменено — активность обнаружена!")
            st_device.set_backlight_level(100)
            state.shutdown_pending = False
            return

        # Вычисляем, сколько секунд осталось
        remaining = countdown - int(elapsed_since_start)

        if remaining != last_displayed and remaining > 0:
            show_message(f"Выключение через: {remaining} сек")
            print(f"Выключение через: {remaining} сек")
            last_displayed = remaining

        if remaining <= 0:
            break

        await asyncio.sleep(0.1)  # чаще проверяем

    print("⏹️ Завершение работы устройства...")
    st_device.set_backlight(False)
    await asyncio.sleep(0.5)
    os.system("sudo halt")

    os.system("sudo halt")
