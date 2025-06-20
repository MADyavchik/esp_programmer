# spi_test.py

from st7789_pi import ST7789
import RPi.GPIO as GPIO
import time

BL_PIN = 25
GPIO.setmode(GPIO.BCM)
GPIO.setup(BL_PIN, GPIO.OUT)

pwm = GPIO.PWM(BL_PIN, 1000)  # 1 kHz
pwm.start(100)  # 100% яркость

print("🔅 Уменьшаем яркость до 0")
for dc in range(100, -1, -5):  # от 100 до 0 с шагом 5
    pwm.ChangeDutyCycle(dc)
    time.sleep(0.1)

print("✅ Готово")
pwm.stop()
GPIO.cleanup()
