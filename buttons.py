# buttons.py
from gpiozero import Button
import time

# Создаем кнопки
btn_up = Button(5, bounce_time=0.2)
btn_down = Button(6, bounce_time=0.2)
btn_back = Button(19, bounce_time=0.2, hold_time=3)  # добавили hold_time для перезагрузки
btn_select = Button(26, bounce_time=0.2)

def setup_buttons(up_action, down_action, back_action, select_action, back_hold_action=None):
    """
    Настроить кнопки с их обработчиками
    :param up_action: функция, вызываемая при нажатии на кнопку "вверх"
    :param down_action: функция, вызываемая при нажатии на кнопку "вниз"
    :param back_action: функция, вызываемая при нажатии на кнопку "назад"
    :param select_action: функция, вызываемая при нажатии на кнопку "выбрать"
    :param back_hold_action: функция для кнопки "назад", если она удерживается
    """
    # Привязка кнопок к действиям
    btn_up.when_pressed = up_action
    btn_down.when_pressed = down_action
    btn_back.when_pressed = back_action
    if back_hold_action:
        btn_back.when_held = back_hold_action
    btn_select.when_pressed = select_action
