import subprocess
import time
import os
from pathlib import Path
from esp32_boot import enter_bootloader, exit_bootloader

PORT = "/dev/ttyS0"
FLASH_ARGS = [
    ("bootloader_0x1000.bin", "0x1000"),
    ("firmware_0x10000.bin",  "0x10000"),
    ("partitions_0x8000.bin", "0x8000"),
    ("ota_data_initial_0xe000.bin", "0xe000"),
    # NVS добавим динамически
]

# Отображение: прошивка -> NVS
NVS_MAP = {
    "Universal": "repeater_nvs_0x9000.bin",
    "Master":    "master_nvs_0x9000.bin",
    "Repiater":  "repeater_nvs_0x9000.bin",
    "Sens_SW":   "sw_nvs_0x9000.bin",
    "Sens_OLD":  "sw_nvs_0x9000.bin",
}

ESP_DIR = Path(__file__).parent / "esp"

def flash_firmware(fw_name: str):
    print(f"🚀 Начинаем прошивку: {fw_name}")

    if fw_name not in NVS_MAP:
        print(f"❌ Неизвестная прошивка: {fw_name}")
        return

    # Список всех .bin файлов для прошивки
    bin_files = FLASH_ARGS.copy()
    nvs_file = NVS_MAP[fw_name]
    bin_files.append((nvs_file, "0x9000"))

    # Проверка наличия всех файлов
    for filename, _ in bin_files:
        path = ESP_DIR / filename
        if not path.exists():
            print(f"❌ Файл не найден: {path}")
            return

    try:
        print("🔌 Перевод ESP32 в режим bootloader...")
        enter_bootloader()
        time.sleep(1)

        print("🧹 Очистка флеша...")
        subprocess.run(["esptool.py", "--chip", "esp32", "-b", "460800", "-p", PORT, "erase_flash"], check=True)

        print("🔄 Перезагрузка после очистки...")
        exit_bootloader()
        time.sleep(1)

        print("🔁 Повторный вход в bootloader...")
        enter_bootloader()
        time.sleep(1)

        print("📦 Запись прошивки:")
        cmd = [
            "esptool.py", "--chip", "esp32", "-b", "460800", "-p", PORT,
            "write_flash", "--flash_mode", "dio", "--flash_freq", "40m", "--flash_size", "4MB"
        ]

        for filename, addr in bin_files:
            full_path = str(ESP_DIR / filename)
            cmd += [addr, full_path]
            print(f"  - {addr}: {filename}")

        subprocess.run(cmd, check=True)

        print("✅ Выход из bootloader...")
        exit_bootloader()
        print("🎉 Прошивка завершена успешно!")

    except subprocess.CalledProcessError as e:
        print(f"⚠️ Ошибка прошивки: {e}")
