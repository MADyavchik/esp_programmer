from gpiozero import Button

btn_up = Button(5)
btn_down = Button(6)
btn_back = Button(19, hold_time=3)
btn_select = Button(26)

def setup_buttons(up, down, back, select, back_hold_action=None):
    btn_up.when_pressed = up
    btn_down.when_pressed = down
    btn_back.when_pressed = back
    btn_select.when_pressed = select
    if back_hold_action:
        btn_back.when_held = back_hold_action
