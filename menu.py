# menu.py
from buttons import setup_buttons
import time
import os
from oled_ui import draw_main_menu
from oled_ui import show_message, clear


def reboot_pi():
    show_message("Reboot...")
    time.sleep(1)
    clear()
    os.system("sudo reboot")



def start_main_menu():
    menu_items = ["FLASH", "UPDATE", "LOG", "SETTINGS"]
    selected = [0]
    scroll = [0]
    VISIBLE_LINES = 2

    def draw():
        draw_main_menu(menu_items, selected[0], scroll[0], VISIBLE_LINES)

    draw()
    selected_result = [None]
    last_redraw = [time.time()]

    def up():
        selected[0] = (selected[0] - 1) % len(menu_items)
        scroll[0] = selected[0]  # курсор всегда на первом элементе
        draw()
        last_redraw[0] = time.time()


    def down():
        selected[0] = (selected[0] + 1) % len(menu_items)
        scroll[0] = selected[0]  # курсор всегда на первом элементе
        draw()
        last_redraw[0] = time.time()

    def back():
        selected_result[0] = None

    def back_hold():
        reboot_pi()

    def select():
        if selected[0] == 0:
            selected_result[0] = "flash"
        elif selected[0] == 1:
            selected_result[0] = "update"
        elif selected[0] == 2:
            selected_result[0] = "log"
        elif selected[0] == 3:
            selected_result[0] = "settings"  # <--- новый пункт
        draw()
        last_redraw[0] = time.time()

    def up_hold():
        selected_result[0] = "mac"

    setup_buttons(up, down, back, select, up_hold_action=up_hold, back_hold_action=back_hold)

    while selected_result[0] is None:
        time.sleep(0.1)

        if time.time() - last_redraw[0] >= 3:
            draw()
            last_redraw[0] = time.time()

    return selected_result[0]
