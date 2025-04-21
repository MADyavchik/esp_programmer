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


def write_command(cmd):
    GPIO.output(DC, GPIO.LOW)
    spi.writebytes([cmd])

def write_data(data):
    GPIO.output(DC, GPIO.HIGH)
    spi.writebytes(data if isinstance(data, list) else [data])

# Полная инициализация ST7789 (на базе datasheet и проверенных init-последовательностей)
def init_display():
    write_command(0x01)  # Software Reset
    time.sleep(0.150)

    write_command(0x11)  # Sleep Out
    time.sleep(0.500)

    write_command(0x3A)  # Interface Pixel Format
    write_data(0x55)     # 16-bit/pixel

    write_command(0x36)  # Memory Data Access Control
    write_data(0x00)     # направление

    write_command(0x29)  # Display ON
    time.sleep(0.100)

    # Установим окно (весь экран)
    write_command(0x2A)  # CASET (Column Address Set)
    write_data([0x00, 0, 0x00, 239])  # X: 0 to 239

    write_command(0x2B)  # RASET (Row Address Set)
    write_data([0x00, 0, 0x00, 239])  # Y: 0 to 239

    write_command(0x2C)  # RAMWR (Memory Write)


def rgb565_to_bgr565(color):
    r = (color >> 11) & 0x1F
    g = (color >> 5) & 0x3F
    b = color & 0x1F
    bgr = (b << 11) | (g << 5) | r
    return bgr

def color565(r, g, b):
    """Создать 16-битный цвет (BGR565) из обычных RGB 0–255"""
    r5 = r >> 3
    g6 = g >> 2
    b5 = b >> 3
    rgb = (r5 << 11) | (g6 << 5) | b5
    return rgb565_to_bgr565(rgb)


def fill_color_test(color_565, label=""):
    print(f"Цвет: {hex(color_565)} -> {label}")
    GPIO.output(DC, GPIO.HIGH)
    buf = [color_565 >> 8, color_565 & 0xFF] * (240 * 240)
    for i in range(0, len(buf), 4096):
        spi.writebytes(buf[i:i+4096])
    time.sleep(3)

init_display()

fill_color_test(0xF800, "ДОЛЖЕН БЫТЬ КРАСНЫЙ")
fill_color_test(0x07E0, "ДОЛЖЕН БЫТЬ ЗЕЛЁНЫЙ")
fill_color_test(0x001F, "ДОЛЖЕН БЫТЬ СИНИЙ")
fill_color_test(0xFFFF, "ДОЛЖЕН БЫТЬ БЕЛЫЙ")
