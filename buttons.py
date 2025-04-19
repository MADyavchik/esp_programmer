import asyncio
import threading
from gpiozero import Button
import loop_reference


btn_up = Button(26, hold_time=1, bounce_time=0.1)
btn_down = Button(13, bounce_time=0.1)
btn_back = Button(6, hold_time=3, bounce_time=0.1)
btn_select = Button(19, bounce_time=0.1)

def safe_async(coro_func):
    try:
        # Проверяем, если главный event loop ещё не готов, выводим предупреждение
        if loop_reference.main_loop is None:
            print("⚠️ Главный event loop ещё не готов.")
            return  # Не вызываем корутину, если loop ещё не готов

        # Если loop готов, запускаем асинхронную задачу
        loop = loop_reference.main_loop
        asyncio.run_coroutine_threadsafe(coro_func(), loop)

    except Exception as e:
        print(f"⚠️ Ошибка в safe_async: {e}")

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
