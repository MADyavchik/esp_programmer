#screens/shotdown_screen.py

import asyncio
import os
import time
import state
from oled_ui import show_message

from st7789_pi import ST7789
st_device = ST7789(width=240, height=240, dc=23, reset=24, bl=12)

async def run_shotdown_halt():
    for i in range(10, 0, -1):
        elapsed = time.time() - state.last_activity_time[0]
        if elapsed < state.shutdown_timeout:
            print("❌ Действие отменено — активность обнаружена!")
            return

        show_message(f"Выключение через: {i} сек")
        await asyncio.sleep(1)

    print("⏹️ Завершение работы устройства...")
    st_device.set_backlight(False)

    await asyncio.sleep(0.5)  # даём гаснуть экрану

    os.system("sudo halt")
