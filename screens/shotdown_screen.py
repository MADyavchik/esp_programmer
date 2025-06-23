#screens/shotdown_screen.py

import asyncio
import os
import time
import state

from st7789_pi import ST7789
st_device = ST7789(width=240, height=240, dc=23, reset=24, bl=12)

async def shotdown_halt(shutdown_timeout):

    for _ in range(10):
                await asyncio.sleep(1)
                if time.time() - state.last_activity_time[0] < shutdown_timeout:
                    print("❌ Действие отменено — активность обнаружена!")
                    shutdown_initiated = False
                    break
                else:
                    print("⏹️ Завершение работы устройства...")
                    st_device.set_backlight(False)

                    # Ожидаем немного, чтобы вывести сообщение и отключить подсветку
                    await asyncio.sleep(0.5)

                    # Завершаем другие задачи, но shutdown выполняем после
                    current = asyncio.current_task()
                    for task in asyncio.all_tasks():
                        if task is not current:
                            task.cancel()

                    try:
                        # Подождём немного, чтобы таски успели завершиться корректно
                        await asyncio.sleep(0.5)
                    except asyncio.CancelledError:
                        pass

                    # Завершаем систему
                    os.system("sudo halt")
                    return  # или break — если хочешь выйти из цикла
