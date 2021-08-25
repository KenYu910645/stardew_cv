import pydirectinput
import time

while(True):
    print("Pressing 'a'")
    pydirectinput.keyDown('a')
    time.sleep(1)
    pydirectinput.keyUp('a')
    time.sleep(1)

    print("Pressing 'a'")
    pydirectinput.keyDown('d')
    time.sleep(1.5)
    pydirectinput.keyUp('d')
    time.sleep(1)

    print("Pressing 'y'")
    pydirectinput.press('y')
    time.sleep(1)
    
    print("Pressing 'e'")
    pydirectinput.press('e')
    time.sleep(1)