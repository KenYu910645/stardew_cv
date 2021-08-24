import time
# Computer vision
from PIL import ImageGrab, Image
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
CONFIENT_THRES = 0.5
DEBUG = True# False 

STATE = 'casting' # 'unknown'
ALLOW_CAST = True
UNKNOW_ALIVE_TIME = 2 # sec
# Color range
THRES_BROWN_UP = (50, 255, 255)
THRES_BROWN_LO = (0, 200, 100)
THRES_BROWN = 340
# THRES_BAR_UP = (55, 255, 255)
# THRES_BAR_LO = (50, 230, 200)
THRES_BAR_UP = (65, 255, 255)
THRES_BAR_LO = (40, 150, 150)
THRES_FISH_UP = (40, 255, 255)
THRES_FISH_UP = (0, 200, 100)
# Global variable 
LAST_HSV = Image.new("RGB", (25, 40), (0, 0, 0))
T_ENTER_UNKNOWN = time.time()

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
    global SCREENS_CAP, IMG_EX, LAST_HSV, STATE, UNKNOW_ALIVE_TIME, T_ENTER_UNKNOWN
    brown_mask = None 
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

        if STATE == 'unknown':
            ########################
            ### Find Message Box ###
            ########################
            img_msg_box = img_resize[110:200, 215:295]
            brown_mask = cv2.inRange(cv2.cvtColor(img_msg_box, cv2.COLOR_RGB2HSV), THRES_BROWN_LO, THRES_BROWN_UP)
            # Matching with exclamation images
            res = cv2.matchTemplate(brown_mask, IMG_BOX, cv2.TM_CCOEFF_NORMED )
            max_cof = np.amax(res)
            if max_cof > CONFIENT_THRES:
                pydirectinput.press('c')
                print("I saw a msg box(" + (str(max_cof)) + "), pressed 'c'")
                STATE = 'casting'
            # Keepalive 
            # if (time.time() - T_ENTER_UNKNOWN) > UNKNOW_ALIVE_TIME:
            #     print("Need to keep alive.")
            #     STATE = 'casting'
        
        elif STATE == 'casting':
            if ALLOW_CAST:
                print("Casting")
                pydirectinput.keyDown('c')
                time.sleep(0.9)
                pydirectinput.keyUp('c')
            STATE = 'baiting'
        
        elif STATE == 'baiting':
            ########################
            ### Find Exclamation ###
            ########################
            img_exclamation = img_resize[180:220, 245:270]
            img_hsv = cv2.cvtColor(img_exclamation, cv2.COLOR_RGB2HSV)
            # Get differ
            diff_hsv = img_hsv - LAST_HSV
            # Matching with exclamation images
            ret, mask_ex = cv2.threshold(cv2.split(diff_hsv)[-1] ,25,255,cv2.THRESH_BINARY)
            res = cv2.matchTemplate(mask_ex, IMG_EX, cv2.TM_CCOEFF_NORMED )
            max_cof = np.amax(res)
            if max_cof > CONFIENT_THRES:
                pydirectinput.press('c')
                print("Get fish! (" + str(max_cof) + ")")
                T_ENTER_UNKNOWN = time.time()
                STATE = "unknown"
            # Post-process
            LAST_HSV = img_hsv
        # elif STATE == 'fishing':
        # img_fish = img_resize[80:380, 190:240]
        # bar_mask = cv2.inRange(cv2.cvtColor(img_fish, cv2.COLOR_RGB2HSV), THRES_BAR_LO, THRES_BAR_UP)
        # res = cv2.matchTemplate(bar_mask, IMG_BAR, cv2.TM_CCOEFF_NORMED )
        # max_cof = np.amax(res)
        # if max_cof > CONFIENT_THRES:
        #     pydirectinput.press('c')
        #     print("Get bar")
        #     STATE = "fishing"

        if DEBUG:
            try:
                cv2.imshow('brown_mask', brown_mask)
            except:
                pass
            # try:
            #     cv2.imshow('bar_mask', bar_mask)
            # except:
            #     pass
            # try:
            #     cv2.imshow('img_fish', img_fish)
            # except:
            #     pass
            try: 
                cv2.imshow('mask_ex',cv2.cvtColor(mask_ex, cv2.COLOR_BGR2RGB))
            except: 
                pass

            cv2.imshow('window',cv2.cvtColor(img_resize, cv2.COLOR_BGR2RGB))
            if cv2.waitKey(1) & 0xFF == ord('q'):
                IS_RUN = False
            #     cv2.imshow('mask_ex', mask_ex)
            #     cv2.imshow('brown_mask', brown_mask)
            #     # cv2.imshow('diff_hsv', diff_hsv)
            #     cv2.imshow("img_msg_box", img_msg_box)
            #     cv2.imshow('window',cv2.cvtColor(img_resize, cv2.COLOR_BGR2RGB))
            #     cv2.imshow('img_exclamation',cv2.cvtColor(img_exclamation, cv2.COLOR_BGR2RGB))
            #     if cv2.waitKey(1) & 0xFF == ord('q'):
            #         IS_RUN = False

if __name__ == '__main__':
    IMG_EX = cv2.imread("exclamation.png" ,cv2.IMREAD_GRAYSCALE)
    IMG_BOX = cv2.imread("msg_box.png" ,cv2.IMREAD_GRAYSCALE)
    IMG_BAR = cv2.imread("bar.png" ,cv2.IMREAD_GRAYSCALE)
    while IS_RUN:
        main()
        time.sleep(0.1)