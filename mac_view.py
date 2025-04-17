# mac_view.py
import time
from oled_ui import draw_mac_address, clear
from esp_flasher import get_mac_address
from buttons import btn_back
from oled_ui import draw_mac_qr  # вместо draw_mac_address

def show_mac_address():
    clear()
    mac = get_mac_address()
    draw_mac_qr(mac)  # теперь отрисовываем QR-код

    while not btn_back.is_pressed:
        time.sleep(0.1)
    while btn_back.is_pressed:
        time.sleep(0.1)

    return "main"
