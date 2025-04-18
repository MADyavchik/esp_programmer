import asyncio
from gpiozero import Button

btn_up = Button(26, hold_time=1, bounce_time=0.1)
btn_down = Button(13, bounce_time=0.1)
btn_back = Button(6, hold_time=3, bounce_time=0.1)
btn_select = Button(19, bounce_time=0.1)

def setup_buttons(up, down, back, select, back_hold_action=None, up_hold_action=None):
    # Оборачиваем функции, если они асинхронные
    def wrap(func):
        if asyncio.iscoroutinefunction(func):
            return lambda: asyncio.create_task(func())
        return func

    btn_up.when_pressed = wrap(up)
    btn_down.when_pressed = wrap(down)
    btn_back.when_pressed = wrap(back)
    btn_select.when_pressed = wrap(select)

    if back_hold_action:
        btn_back.when_held = wrap(back_hold_action)
    if up_hold_action:
        btn_up.when_held = wrap(up_hold_action)
