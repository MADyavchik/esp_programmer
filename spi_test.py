import spidev
import RPi.GPIO as GPIO
import time

DC = 23
RST = 24

# Настройка GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(DC, GPIO.OUT)
GPIO.setup(RST, GPIO.OUT)

# Сброс дисплея
GPIO.output(RST, GPIO.LOW)
time.sleep(0.1)
GPIO.output(RST, GPIO.HIGH)
time.sleep(0.1)

# Настройка SPI
spi = spidev.SpiDev()
spi.open(0, 0)  # bus 0, device 0
spi.max_speed_hz = 40000000
spi.mode = 3  # ВОТ ТУТ МЕНЯЕМ РЕЖИМ: mode 3 = CPOL=1, CPHA=1

# Пример команды инициализации дисплея ST7789
def send_command(cmd):
    GPIO.output(DC, GPIO.LOW)
    spi.writebytes([cmd])

def send_data(data):
    GPIO.output(DC, GPIO.HIGH)
    if isinstance(data, list):
        spi.writebytes(data)
    else:
        spi.writebytes([data])

# Попробуем отправить команды инициализации (неполные, просто для теста)
send_command(0x01)  # Software reset
time.sleep(0.15)
send_command(0x11)  # Sleep out
time.sleep(0.5)
send_command(0x29)  # Display ON

print("Команды отправлены. Есть изменения на экране?")
