# settings.py
import os
import time
from oled_ui import show_message, clear, draw_main_menu
from buttons import setup_buttons

def toggle_wifi():
    os.system("nmcli radio wifi off" if is_wifi_enabled() else "nmcli radio wifi on")

def toggle_bluetooth():
    os.system("rfkill block bluetooth" if is_bt_enabled() else "rfkill unblock bluetooth")

def is_wifi_enabled():
    result = os.popen("nmcli radio wifi").read().strip()
    return result == "enabled"

def is_bt_enabled():
    result = os.popen("rfkill list bluetooth").read()
    return "Soft blocked: yes" not in result

def start_settings_menu():
    menu_items = ["Wi-Fi: ?", "Bluetooth: ?"]
    selected = [0]
    selected_result = [None]
    last_redraw = [0]

    def refresh_labels():
        menu_items[0] = f"Wi-Fi: {'ON' if is_wifi_enabled() else 'OFF'}"
        menu_items[1] = f"Bluetooth: {'ON' if is_bt_enabled() else 'OFF'}"

    def draw():
        refresh_labels()
        draw_main_menu(menu_items, selected[0], selected[0], visible_lines=2)

    def up():
        selected[0] = (selected[0] - 1) % len(menu_items)
        draw()

    def down():
        selected[0] = (selected[0] + 1) % len(menu_items)
        draw()

    def back():
        selected_result[0] = "main"

    def select():
        if selected[0] == 0:
            toggle_wifi()
        elif selected[0] == 1:
            toggle_bluetooth()
        draw()

    setup_buttons(up, down, back, select)

    draw()
    while selected_result[0] is None:
        time.sleep(0.1)
        if time.time() - last_redraw[0] > 3:
            draw()
            last_redraw[0] = time.time()

    return selected_result[0]
