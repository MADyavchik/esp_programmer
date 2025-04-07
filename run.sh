#!/bin/bash

# Определяем реальный путь к скрипту, даже если он вызван через символическую с>
SCRIPT_PATH=$(readlink -f "$0")
SCRIPT_DIR=$(dirname "$SCRIPT_PATH")

# Переходим в папку, где лежит сам скрипт
cd "$SCRIPT_DIR" || exit 1

echo "Текущий каталог: $(pwd)"
echo "Путь к скрипту: $(dirname "$0")"

BOOTLOADER="bootloader_0x1000.bin"
FIRMWARE="firmware_0x10000.bin"
OTA="ota_data_initial_0xe000.bin"
PARTITIONS="partitions_0x8000.bin"
#NVS="repeater_nvs_0x9000.bin"

# Выбор NVS
echo "Выберите NVS-файл:"

echo "1) repeater_nvs_0x9000.bin"
echo "2) master_nvs_0x9000.bin"
echo "3) sw_nvs_0x9000.bin"
read -p "Введите номер (1/2/3): " nvs_choice

case "$nvs_choice" in
  1) NVS="repeater_nvs_0x9000.bin" ;;
  2) NVS="master_nvs_0x9000.bin" ;;
  3) NVS="sw_nvs_0x9000.bin" ;;
  *) echo "Неверный ввод! Завершение."; exit 1 ;;
esac

echo "Выбран NVS: $NVS"
python3 ssd1306_display.py

port="/dev/ttyS0"

if [ "$port" == "" ]; then
  echo "Usage: flash.sh {port}"
  exit 0
fi

# Переход в режим загрузчика
echo "Перевод ESP32 в режим bootloader..."
#python3 esp32_boot.py boot
python3 "$(dirname "$0")/esp32_boot.py" boot

# Установка зависимостей
#pip3 install esptool

# Установка напряжения (если eFuse не настроен)
espefuse.py --chip esp32 -p "$port" set_flash_voltage 3.3V --do-not-confirm

# Очистка флеша
esptool.py --chip esp32 -b 460800 -p "$port" erase_flash

# АППАРАТНЫЙ СБРОС после очистки флеша
echo "Перезагрузка ESP32 после очистки флеша..."
#python3 ssd1306_display.py "Hard reset"
#python3 esp32_boot.py normal
python3 "$(dirname "$0")/esp32_boot.py" normal
sleep 1  # Ждем, чтобы устройство полностью перезагрузилось

# Снова входим в bootloader для прошивки
echo "Повторный вход в bootloader для прошивки..."
#python3 ssd1306_display.py "Boot.."
#python3 esp32_boot.py boot
python3 "$(dirname "$0")/esp32_boot.py" boot
sleep 1

# Прошивка
#python3 ssd1306_display.py "Flash.."
esptool.py --chip esp32 -b 460800 -p "$port" write_flash --flash_mode dio --flash_freq 40m --flash_size 4MB  \
  0x1000 "./$BOOTLOADER" \
  0x10000 "./$FIRMWARE" \
  0x8000 "./$PARTITIONS" \
  0xe000 "./$OTA" \
  0x9000 "./$NVS"

# Выход из режима загрузчика
echo "Вывод ESP32 из режима bootloader..."
#python3 esp32_boot.py normal
python3 "$(dirname "$0")/esp32_boot.py" normal

echo "Прошивка завершена!"
