from buttons import setup_buttons
from luma.core.render import canvas
from PIL import ImageFont
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
import os, time

device = ssd1306(i2c(port=1, address=0x3C))
font = ImageFont.load_default()
menu_items = ["FLASH", "UPDATE"]
selected = [0]

def start_main_menu(open_flash_menu):
    def draw():
        with canvas(device) as draw_canvas:
            for i, item in enumerate(menu_items):
                prefix = "> " if i == selected[0] else "  "
                draw_canvas.text((10, 10 + i*20), prefix + item, font=font, fill="white")

    def select():
        if selected[0] == 0:
            open_flash_menu()  # переход в flash_menu
        else:
            print("Update...")

    def up(): selected[0] = (selected[0] - 1) % len(menu_items); draw()
    def down(): selected[0] = (selected[0] + 1) % len(menu_items); draw()
    def back(): selected[0] = 0; draw()
    def reboot(): os.system("sudo reboot")

    setup_buttons(up, down, back, select, back_hold_action=reboot)
    draw()
