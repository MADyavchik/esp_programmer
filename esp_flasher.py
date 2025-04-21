# esp_flasher.py
import os
import subprocess
import logging
from esp32_boot import enter_bootloader, exit_bootloader
from oled_ui import draw_progress_bar, show_message, clear
import re
import time
import threading

logging.basicConfig(level=logging.INFO)

FLASH_DIR = "esp"
PORT = "/dev/ttyS0"

# Названия прошивок без NVS
NO_NVS = ["sens_sw", "sens_old"]

async def flash_firmware(firmware_name):
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

    use_nvs = firmware_name not in NO_NVS
    if use_nvs:
        if firmware_name == "master":
            nvs = os.path.join(firmware_path, "master_nvs_0x9000.bin")
        elif firmware_name == "repeater":
            nvs = os.path.join(firmware_path, "repeater_nvs_0x9000.bin")
        else:
            nvs = os.path.join(firmware_path, "sw_nvs_0x9000.bin")
        if not os.path.exists(nvs):
            logging.error(f"❌ NVS-файл не найден: {nvs}")
            return

    for file in [bootloader, firmware, partitions, ota]:
        if not os.path.exists(file):
            logging.error(f"❌ Файл не найден: {file}")
            return

    mac_address = None  # Добавляем переменную для MAC-адреса

    try:
        logging.info("🔌 Перевод ESP32 в режим bootloader...")
        show_message("Bootloader...")
        enter_bootloader()

        # Прожигаем фьюзы
        logging.info("⚡ Прожигаем фьюзы...")
        show_message("Burning fuse...")
        subprocess.run([
            "espefuse.py", "--chip", "esp32", "-p", PORT, "set_flash_voltage", "3.3V", "--do-not-confirm"
        ], check=True)

        logging.info("🧽 Очистка флеша...")
        show_message("Erasing flash...")

        # Запускаем процесс очистки флеша, чтобы парсить MAC-адрес
        process = subprocess.Popen([
            "esptool.py", "--chip", "esp32", "-b", "460800", "-p", PORT, "erase_flash"
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, universal_newlines=True)

        # Парсим вывод команды очистки флеша
        while True:
            line = process.stdout.readline()
            if not line:
                break
            line = line.strip()
            print(f"💬 {line}")
            logging.info(line)

            # Проверяем, не содержит ли строка MAC-адрес
            mac_match = re.search(r"MAC:\s*([0-9a-fA-F:]{17})", line)
            if mac_match and not mac_address:
                mac_address = mac_match.group(1).lower()  # Сохраняем MAC-адрес
                logging.info(f"📡 Обнаружен MAC-адрес: {mac_address}")  # Выводим в лог

               # 🔍 Проверка статуса подключения принтера
                from settings import printer_connection  # импортируем только когда нужен
                if printer_connection["connected"]:
                    logging.info("🖨️ Принтер уже подключен.")
                    if printer_connection.get("device"):
                        logging.info(f"🔧 Device: {printer_connection['device']}")
                    else:
                        logging.info("⚠️ Устройство не найдено в printer_connection.")
                else:
                    logging.info("🖨️ Принтер не подключен.")
        process.wait()

        logging.info("🔁 Повторный вход в bootloader...")
        enter_bootloader()

        logging.info("📦 Прошивка...")
        show_message("Flashing...")

        flash_args = [
            "python3", "-u", "-m", "esptool", "--chip", "esp32", "-b", "460800", "-p", PORT,
            "write_flash", "--flash_mode", "dio", "--flash_freq", "40m", "--flash_size", "4MB",
            "0x1000", bootloader,
            "0x10000", firmware,
            "0x8000", partitions,
            "0xe000", ota,
        ]
        if use_nvs:
            flash_args += ["0x9000", nvs]

        process = subprocess.Popen(
            flash_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            universal_newlines=True,
            env={**os.environ, "PYTHONUNBUFFERED": "1"}
        )

        prev_percent = -1
        while True:
            line = process.stdout.readline()
            if not line:
                break
            line = line.strip()
            print(f"💬 {line}")
            logging.info(line)

            match = re.search(r"\((\d+)\s*%\)", line)
            if match:
                percent = int(match.group(1))
                if percent != prev_percent:
                    prev_percent = percent
                    draw_progress_bar(percent, message="Flashing...")

        process.wait()

        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, flash_args)

        logging.info("✅ Прошивка завершена, перезагрузка...")
        draw_progress_bar(100, message="Done")
        time.sleep(1)
        #clear()
        exit_bootloader()

        # 📤 Печать MAC-адреса, если принтер подключен
        from settings import printer_connection
        if printer_connection["connected"] and printer_connection.get("printer"):
            from printer_functions import print_mac_address
            logging.info("🖨️ Отправляем MAC на печать...")
            show_message("Printing MAC...")
            #time.sleep(2)
            await print_mac_address(printer_connection["printer"], mac_address, config=printer_connection["config"])
        else:
            logging.warning("⚠️ Принтер не подключен — печать пропущена.")

    except subprocess.CalledProcessError as e:
        logging.error(f"❌ Прошивка не удалась: {e}")
        show_message("Ошибка прошивки")
        time.sleep(2)
        clear()
    except Exception as e:
        logging.error(f"❌ Ошибка: {e}")
        show_message("Ошибка")
        time.sleep(2)
        clear()
    return "flash"

def get_mac_address():
    try:
        logging.info("📡 Получение MAC-адреса...")
        show_message("Read MAC...")

        enter_bootloader()

        result = subprocess.run(
            ["esptool.py", "--chip", "esp32", "-p", PORT, "read_mac"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            check=True
        )

        mac_line = next((line for line in result.stdout.splitlines() if "MAC:" in line), None)
        if mac_line:
            mac = mac_line.split("MAC:")[1].strip()
            logging.info(f"✅ MAC-адрес: {mac}")
            exit_bootloader()
            return mac
        else:
            raise Exception("MAC-адрес не найден в выводе esptool")

    except Exception as e:
        logging.error(f"❌ Ошибка получения MAC-адреса: {e}")
        exit_bootloader()
        return None
