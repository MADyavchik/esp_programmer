import asyncio
import threading
from gpiozero import Button

btn_up = Button(26, hold_time=1, bounce_time=0.1)
btn_down = Button(13, bounce_time=0.1)
btn_back = Button(6, hold_time=3, bounce_time=0.1)
btn_select = Button(19, bounce_time=0.1)

def safe_async(coro_func):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        loop.call_soon_threadsafe(lambda: asyncio.create_task(coro_func()))
    else:
        # Если event loop не запущен — запускаем в отдельном потоке с новым loop
        def run():
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            new_loop.run_until_complete(coro_func())
            new_loop.close()
        threading.Thread(target=run, daemon=True).start()

def setup_buttons(up, down, back, select, back_hold_action=None, up_hold_action=None):
    def wrap(func):
        if asyncio.iscoroutinefunction(func):
            return lambda: safe_async(func)  # НЕ вызываем func здесь!
        return func

    btn_up.when_pressed = wrap(up)
    btn_down.when_pressed = wrap(down)
    btn_back.when_pressed = wrap(back)
    btn_select.when_pressed = wrap(select)

    if back_hold_action:
        btn_back.when_held = wrap(back_hold_action)
    if up_hold_action:
        btn_up.when_held = wrap(up_hold_action)
