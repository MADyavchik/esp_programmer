#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time
import sys
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Пины GPIO
BOOT_PIN = 17
EN_PIN = 18

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BOOT_PIN, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(EN_PIN, GPIO.OUT, initial=GPIO.HIGH)

def enter_bootloader():
    setup()
    logging.info("Перевод ESP32 в режим загрузчика...")
    GPIO.output(BOOT_PIN, GPIO.LOW)
    time.sleep(0.15)
    GPIO.output(EN_PIN, GPIO.LOW)
    time.sleep(0.1)
    GPIO.output(EN_PIN, GPIO.HIGH)
    logging.info("ESP32 теперь в режиме загрузчика.")

def exit_bootloader():
    setup()
    logging.info("Выход из режима загрузчика...")
    GPIO.output(BOOT_PIN, GPIO.HIGH)
    time.sleep(0.1)
    GPIO.output(EN_PIN, GPIO.LOW)
    time.sleep(0.12)
    GPIO.output(EN_PIN, GPIO.HIGH)
    time.sleep(0.8)
    logging.info("ESP32 перезагружена в нормальный режим.")

if __name__ == "__main__":
    setup()

    if len(sys.argv) < 2:
        logging.error("Не указан режим работы! Используйте 'boot' или 'normal'.")
        sys.exit(1)

    mode = sys.argv[1]

    try:
        if mode == "boot":
            enter_bootloader()
        elif mode == "normal":
            exit_bootloader()
        else:
            logging.error("Некорректный аргумент! Используйте 'boot' или 'norma'.")
            sys.exit(1)
    finally:
        GPIO.cleanup()
