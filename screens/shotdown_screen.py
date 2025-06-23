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

    # Фиксируем момент начала обратного отсчёта
    shutdown_start = time.time()

    for i in range(countdown, 0, -1):
        elapsed_since_start = time.time() - shutdown_start
        activity_elapsed = time.time() - state.last_activity_time[0]

        if activity_elapsed < elapsed_since_start:
            print("❌ Действие отменено — активность обнаружена!")
            st_device.set_backlight_level(100)
            return

        show_message(f"Выключение через: {i} сек")
        print(f"Выключение через: {i} сек")
        await asyncio.sleep(1)

    print("⏹️ Завершение работы устройства...")
    st_device.set_backlight(False)
    await asyncio.sleep(0.5)  # даём гаснуть экрану

    os.system("sudo halt")
