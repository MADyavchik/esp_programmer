# menu.py
from buttons import setup_buttons
import time
import os
import sys
from oled_ui import draw_menu  # вместо draw_main_menu
from oled_ui import show_message, clear
import asyncio
from utils import log_async

def reboot_pi():
    show_message("Reboot...")
    time.sleep(1)
    clear()
    os.execv(sys.executable, [sys.executable] + sys.argv)

@log_async
async def start_main_menu():
    menu_items = ["FLASH", "UPDATE", "LOG", "SETTINGS"]
    selected = [0]
    selected_result = [None]
    last_redraw = [time.time()]


    def draw():

        draw_menu(
            items=menu_items,
            selected_index=selected[0],
            scroll=0,
            visible_lines=None,
            highlight_color="yellow",
            show_back_button=False
        )

    def up():
        selected[0] = (selected[0] - 1) % len(menu_items)
        draw()
        last_redraw[0] = time.time()

    def down():
        selected[0] = (selected[0] + 1) % len(menu_items)
        draw()
        last_redraw[0] = time.time()

    def back():
        selected_result[0] = None

    def back_hold():
        reboot_pi()

    def select():
        selected_result[0] = menu_items[selected[0]].lower()
        draw()
        last_redraw[0] = time.time()

    def up_hold():
        selected_result[0] = "mac"

    setup_buttons(up, down, back, select, up_hold_action=up_hold, back_hold_action=back_hold)

    draw()

    while selected_result[0] is None:
        await asyncio.sleep(0.1)
        if time.time() - last_redraw[0] >= 3:
            draw()
            last_redraw[0] = time.time()

    return selected_result[0]
