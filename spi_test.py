import spidev
import RPi.GPIO as GPIO
import time

DC = 23
RST = 24

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(DC, GPIO.OUT)
GPIO.setup(RST, GPIO.OUT)

# Reset
GPIO.output(RST, GPIO.LOW)
time.sleep(0.1)
GPIO.output(RST, GPIO.HIGH)
time.sleep(0.1)

# SPI init
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 40000000
spi.mode = 3

def write_command(cmd):
    GPIO.output(DC, GPIO.LOW)
    spi.writebytes([cmd])

def write_data(data):
    GPIO.output(DC, GPIO.HIGH)
    spi.writebytes(data if isinstance(data, list) else [data])

def init_display():
    write_command(0x01)
    time.sleep(0.150)

    write_command(0x11)
    time.sleep(0.500)

    write_command(0x3A)
    write_data(0x55)  # RGB565 формат

    write_command(0x36)
    write_data(0x08)  # ВКЛЮЧАЕМ BGR! Было 0x00

    write_command(0x29)
    time.sleep(0.100)

    write_command(0x2A)
    write_data([0x00, 0, 0x00, 239])

    write_command(0x2B)
    write_data([0x00, 0, 0x00, 239])

    write_command(0x2C)

def color565(r, g, b):
    r5 = r >> 3
    g6 = g >> 2
    b5 = b >> 3
    return (r5 << 11) | (g6 << 5) | b5

def fill_color(color_565):
    GPIO.output(DC, GPIO.HIGH)
    # !!! Поменяли порядок: сначала младший, потом старший
    buf = [color_565 & 0xFF, color_565 >> 8] * (240 * 240)
    for i in range(0, len(buf), 4096):
        spi.writebytes(buf[i:i+4096])

# MAIN
init_display()

# 🔴 RED
print("RED")
fill_color(color565(255, 0, 0))
time.sleep(2)

# 🟢 GREEN
print("GREEN")
fill_color(color565(0, 255, 0))
time.sleep(2)

# 🔵 BLUE
print("BLUE")
fill_color(color565(0, 0, 255))
time.sleep(2)
