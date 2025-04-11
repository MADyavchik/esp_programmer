# buttons.py
from gpiozero import Button

# Указываем bounce_time=0.1 (100 мс) — это стандартная задержка, можно варьировать
btn_up = Button(26, hold_time=1, bounce_time=0.1)
btn_down = Button(13, bounce_time=0.1)
btn_back = Button(6, hold_time=3, bounce_time=0.1)
btn_select = Button(19, bounce_time=0.1)

def setup_buttons(up, down, back, select, back_hold_action=None, up_hold_action=None):
    btn_up.when_pressed = up
    btn_down.when_pressed = down
    btn_back.when_pressed = back
    btn_select.when_pressed = select
    if back_hold_action:
        btn_back.when_held = back_hold_action
    if up_hold_action:
        btn_up.when_held = up_hold_action  # Добавляем обработчик для кнопки up при удержании
