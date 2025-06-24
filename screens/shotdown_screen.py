#screens/shotdown_screen.py

import asyncio
import os
import time
import state
from oled_ui import show_message, clear, st_device
import RPi.GPIO as GPIO




async def run_shotdown_halt():
    print("⚠️ Без активности. Запуск таймера выключения...")

    countdown = 10
    shutdown_start = time.time()

    for i in range(countdown, 0, -1):
        elapsed_since_start = time.time() - shutdown_start
        activity_elapsed = time.time() - state.last_activity_time[0]

        if activity_elapsed < elapsed_since_start:
            print("❌ Действие отменено — активность обнаружена!")
            if st_device:
                st_device.set_backlight_level(100)
            state.shutdown_pending = False
            return

        show_message(f"Выключение через: {i} сек")
        await asyncio.sleep(1)

    print("⏹️ Завершение работы устройства...")

    if st_device:
        clear()
        st_device.set_backlight(False)


    #state.shutdown_pending = False
    await asyncio.sleep(0.5)

    cleanup_and_shutdown()

        # 🛑 Мгновенно завершаем Python-процесс
    #os._exit(0)


def cleanup_and_shutdown():
    print("⚙️ Выключаем подсветку и чистим GPIO перед завершением...")
    state.status_updater_running = False

    try:
        GPIO.setmode(GPIO.BCM)  # Обязательно до любого использования GPIO
        BACKLIGHT_PIN = 12

        GPIO.setup(BACKLIGHT_PIN, GPIO.OUT)
        GPIO.output(BACKLIGHT_PIN, GPIO.LOW)
        #GPIO.cleanup()  # Теперь безопасно
    except Exception as e:
        print(f"[GPIO Cleanup Error] {e}")

    os.system("sudo halt")  # Требует прав root
