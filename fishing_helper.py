import time
# Computer vision
from PIL import ImageGrab
import cv2
import numpy as np
import pydirectinput
# Screen monitor
import win32gui
# Logging
import sys

GAME_TITLE = 'stardew valley' # windows title must cantain these characters
IS_RUN = True
SCREENS_CAP = None
# Color range
NUM_HSV_LO = (20, 150, 0) # Green number on mini-map
NUM_HSV_UP = (40, 255, 255)
CONFIENT_THRES = 0.5

WIN_LIST = []
def enum_cb(hwnd, results):
    global WIN_LIST
    WIN_LIST.append((hwnd, win32gui.GetWindowText(hwnd)))
    
def get_screens(screen_name):
    screens = None
    for hwnd, title in WIN_LIST:
        if screen_name == title.lower():
            screens = (hwnd, title)
    return screens

def list_all_windows_name():
    win32gui.EnumWindows(enum_cb, WIN_LIST)
    names = []
    for hwnd, title in WIN_LIST:
        names.append(title.lower())
    return names

def remove_isolated_pixels(image):
    (num_stats, labels, stats, _) = cv2.connectedComponentsWithStats(image, 8, cv2.CV_32S)
    new_image = image.copy()
    for label in range(num_stats):
        if stats[label,cv2.CC_STAT_AREA] == 1:
            new_image[labels == label] = 0
    return new_image

def main():
    global SCREENS_CAP, IMG_EX
    if SCREENS_CAP == None:
        # wait for the program to start initially.
        win32gui.EnumWindows(enum_cb, WIN_LIST)
        SCREENS_CAP = get_screens(GAME_TITLE)
        if SCREENS_CAP == None:
            print("Can't find stardew valley. Please execute stardew valley!")
        else:
            # Get screen handle
            print("Found stardew valley screen!")
    
    # Try to get screen
    if SCREENS_CAP != None:
        try:
            img_window = np.array(ImageGrab.grab(bbox=win32gui.GetWindowRect(SCREENS_CAP[0])))
        except:
            SCREENS_CAP = None
            print("Can't find MHW game. Please execute MHW!")

    if SCREENS_CAP != None:
        # Resize 
        img_resize = cv2.resize(img_window, (512, 512), interpolation=cv2.INTER_AREA)
        # img_exclamation = img_resize[160:200, 245:270]
        img_exclamation = img_resize[100:250, 200:320]
        img_hsv = cv2.cvtColor(img_exclamation, cv2.COLOR_RGB2HSV)

        # Mask 
        mask = cv2.inRange(img_hsv, NUM_HSV_LO, NUM_HSV_UP)
        remove_isolated_pixels(mask)
        
        # Matching with exclamation images
        res = cv2.matchTemplate(mask, IMG_EX, cv2.TM_CCOEFF_NORMED )
        max_cof = np.amax(res)
        if max_cof > CONFIENT_THRES:
            pydirectinput.press('c')
            print("Get fish! (" + str(max_cof) + ")")
        
        # img_window
        # cv2.imshow('mask', mask)
        # cv2.imshow('window',cv2.cvtColor(img_resize, cv2.COLOR_BGR2RGB))
        # cv2.imshow('img_exclamation',cv2.cvtColor(img_exclamation, cv2.COLOR_BGR2RGB))
        if cv2.waitKey(1) & 0xFF == ord('q'):
            IS_RUN = False

if __name__ == '__main__':
    IMG_EX = cv2.imread("exclamation.png" ,cv2.IMREAD_GRAYSCALE)
    while IS_RUN:
        main()
        time.sleep(0.1)