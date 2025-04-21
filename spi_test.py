import spidev
import RPi.GPIO as GPIO
import time

DC = 23
RST = 24

# Настройка GPIO
GPIO.setwarnings(False)
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
    write_command(0x01)  # Software Reset
    time.sleep(0.150)

    write_command(0x11)  # Sleep Out
    time.sleep(0.500)

    write_command(0x3A)  # Interface Pixel Format
    write_data(0x55)     # 16-bit/pixel (RGB565)

    write_command(0x36)  # Memory Access Control
    write_data(0x08)     # BGR порядок (важно!)

    write_command(0x29)  # Display ON
    time.sleep(0.100)

    # Установка окна (весь экран)
    write_command(0x2A)  # Column Address Set
    write_data([0x00, 0, 0x00, 239])  # X: 0–239

    write_command(0x2B)  # Row Address Set
    write_data([0x00, 0, 0x00, 239])  # Y: 0–239

    write_command(0x2C)  # RAM Write (start writing)

def color565(r, g, b):
    """RGB → RGB565"""
    r5 = r >> 3
    g6 = g >> 2
    b5 = b >> 3
    return (r5 << 11) | (g6 << 5) | b5

def fill_color(color_565):
    GPIO.output(DC, GPIO.HIGH)
    # Порядок байтов: сначала старший, потом младший (MSB first)
    buf = [color_565 >> 8, color_565 & 0xFF] * (240 * 240)
    for i in range(0, len(buf), 4096):
        spi.writebytes(buf[i:i+4096])

# ---------------- MAIN ----------------
init_display()

print("RED")
fill_color(color565(255, 0, 0))
time.sleep(2)

print("GREEN")
fill_color(color565(0, 255, 0))
time.sleep(2)

print("BLUE")
fill_color(color565(0, 0, 255))
time.sleep(2)
