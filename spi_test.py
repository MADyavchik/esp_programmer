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
spi.mode = 3  # CPOL=1, CPHA=1

def write_command(cmd):
    GPIO.output(DC, GPIO.LOW)
    spi.writebytes([cmd])

def write_data(data):
    GPIO.output(DC, GPIO.HIGH)
    spi.writebytes(data if isinstance(data, list) else [data])

def init_display(use_bgr=False):
    write_command(0x01)  # Software Reset
    time.sleep(0.150)

    write_command(0x11)  # Sleep Out
    time.sleep(0.500)

    write_command(0x3A)  # Interface Pixel Format
    write_data(0x55)     # 16-bit/pixel (RGB565)

    write_command(0x36)  # Memory Access Control
    write_data(0x08 if use_bgr else 0x00)  # BGR or RGB order

    write_command(0x29)  # Display ON
    time.sleep(0.100)

    # Установка окна (весь экран)
    write_command(0x2A)  # Column Address Set
    write_data([0x00, 0, 0x00, 239])  # X: 0–239

    write_command(0x2B)  # Row Address Set
    write_data([0x00, 0, 0x00, 239])  # Y: 0–239

    write_command(0x2C)  # RAM Write (start writing)

def color565(r, g, b):
    """Создать 16-битный цвет (RGB565) из обычных RGB 0–255"""
    r5 = r >> 3      # 5 бит красного
    g6 = g >> 2      # 6 бит зелёного
    b5 = b >> 3      # 5 бит синего
    return (r5 << 11) | (g6 << 5) | b5  # RRRRR GGGGGG BBBBB

def fill_color(color_565):
    GPIO.output(DC, GPIO.HIGH)
    # поменяли порядок байт: MSB first — как ST7789 и хочет
    buf = [color_565 >> 8, color_565 & 0xFF] * (240 * 240)  # Растягиваем на весь экран
    for i in range(0, len(buf), 4096):
        spi.writebytes(buf[i:i+4096])

# ---------------- MAIN ----------------
# Выбери True если нужно BGR, False — RGB
init_display(use_bgr=True)

print("Заливаю красным...")
fill_color(color565(255, 0, 0))  # ДОЛЖЕН быть красный
time.sleep(1)

print("Заливаю зелёным...")
fill_color(color565(0, 255, 0))  # ДОЛЖЕН быть зелёный
time.sleep(1)

print("Заливаю синим...")
fill_color(color565(0, 0, 255))  # ДОЛЖЕН быть синий
time.sleep(1)

print("Готово!")
