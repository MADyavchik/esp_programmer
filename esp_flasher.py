import os
import subprocess
import logging
from esp32_boot import enter_bootloader, exit_bootloader

from oled_ui import draw_progress_bar, show_message, clear
import re  # для разбора %
import time

logging.basicConfig(level=logging.INFO)

FLASH_DIR = "esp"
PORT = "/dev/ttyS0"

# Названия прошивок без NVS
NO_NVS = ["sens_sw", "sens_old"]

def flash_firmware(firmware_name):
    firmware_name = firmware_name.lower()
    logging.info(f"🚀 Начинаем прошивку: {firmware_name}")

    firmware_path = os.path.join(FLASH_DIR, firmware_name)

    if not os.path.exists(firmware_path):
        logging.error(f"❌ Папка с прошивкой не найдена: {firmware_path}")
        return

    # Обязательные бинарники
    bootloader = os.path.join(firmware_path, "bootloader_0x1000.bin")
    firmware = os.path.join(firmware_path, "firmware_0x10000.bin")
    partitions = os.path.join(firmware_path, "partitions_0x8000.bin")
    ota = os.path.join(firmware_path, "ota_data_initial_0xe000.bin")

    # NVS — только если прошивка его использует
    use_nvs = firmware_name not in NO_NVS
    if use_nvs:
        # Подставляем нужный nvs-файл
        if firmware_name == "master":
            nvs = os.path.join(firmware_path, "master_nvs_0x9000.bin")
        elif firmware_name == "repeater":
            nvs = os.path.join(firmware_path, "repeater_nvs_0x9000.bin")
        else:
            nvs = os.path.join(firmware_path, "sw_nvs_0x9000.bin")

        if not os.path.exists(nvs):
            logging.error(f"❌ NVS-файл не найден: {nvs}")
            return

    # Проверка основных файлов
    for file in [bootloader, firmware, partitions, ota]:
        if not os.path.exists(file):
            logging.error(f"❌ Файл не найден: {file}")
            return

    try:
        logging.info("🔌 Перевод ESP32 в режим bootloader...")
        show_message("Bootloader...")
        enter_bootloader()

        logging.info("🧽 Очистка флеша...")
        show_message("Erasing flash...")
        subprocess.run([
            "esptool.py", "--chip", "esp32", "-b", "460800", "-p", PORT, "erase_flash"
        ], check=True)

        logging.info("🔁 Повторный вход в bootloader...")
        enter_bootloader()

        logging.info("📦 Прошиваем...")
        show_message("Flashing...")

        flash_args = [
            "esptool.py", "--chip", "esp32", "-b", "460800", "-p", PORT,
            "write_flash", "--flash_mode", "dio", "--flash_freq", "40m", "--flash_size", "4MB",
            "0x1000", bootloader,
            "0x10000", firmware,
            "0x8000", partitions,
            "0xe000", ota,
        ]

        if use_nvs:
            flash_args += ["0x9000", nvs]

        #subprocess.run(flash_args, check=True)
        process = subprocess.Popen(
            flash_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )

        for line in process.stdout:
            line = line.strip()
            print(line)
            match = re.search(r"\((\d+)%\)", line)
            if match:
                percent = int(match.group(1))
                draw_progress_bar(percent)

        process.wait()

        logging.info("✅ Прошивка завершена, перезагрузка...")
        # вставка
        draw_progress_bar(100, message="Done")
        time.sleep(1)
        clear()

        exit_bootloader()

    except subprocess.CalledProcessError as e:
        logging.error(f"Прошивка не удалась: {e}")
    except Exception as e:
        logging.error(f"Ошибка: {e}")
