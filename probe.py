import numpy as np
import cv2
import time
import win32gui
from PIL import ImageGrab

COLOR_ROWS = 160
COLOR_COLS = 500
REVERSE_RGB = True #True if your channel is BGR, False if it's RGB 
WINDOW_SIZE = (512,512)

SCREENS_CAP = None
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


def on_mouse_click(event, x, y, flags, userParams):
    global colorArray, snapshot
    if event == cv2.EVENT_LBUTTONDOWN:
        colorArray[:] = snapshot[y, x, :]
        rgb = snapshot[y, x, [2,1,0]]

        # HSV convert
        snapshot_hsv = cv2.cvtColor(snapshot, cv2.COLOR_BGR2HSV)
        hsv = snapshot_hsv[y, x, [0,1,2]]

        # From stackoverflow/com/questions/1855884/determine-font-color-based-on-background-color
        # Get text Color 
        luminance = 1 - (0.299*rgb[0] + 0.587*rgb[1] + 0.114*rgb[2]) / 255
        if luminance < 0.5:
            textColor = [0,0,0]
        else:
            textColor = [255,255,255]
        
        cv2.putText(colorArray, "(x,y): " + str((x,y)), (20, COLOR_ROWS - 100),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.8, color=textColor)
        cv2.putText(colorArray, "RGB:" + str(rgb), (20, COLOR_ROWS - 60),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.8, color=textColor)
        cv2.putText(colorArray, "HSV:" + str(hsv), (20, COLOR_ROWS - 20),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.8, color=textColor)
        cv2.imshow('Color', colorArray)

GAME_TITLE = 'stardew valley'

if __name__ == '__main__':
    names = list_all_windows_name()
    # print(names)
    screen = None
    for name in names:
        if GAME_TITLE == name:
            screen = name
            print("Windows name: " + screen)
    screens = get_screens(screen)
    
    # # Convert to array
    # img_window = np.array(ImageGrab.grab(bbox=win32gui.GetWindowRect(screens[0])))
    
    # # Resize
    # (imgH, imgW, _) = img_window.shape
    # img_mhw = cv2.resize(img_window, (int(imgW*RESIZE_SCALE), int(imgH*RESIZE_SCALE)), interpolation=cv2.INTER_AREA)
    # (h, w, _) = img_mhw.shape

    # Init snapshot
    snapshot = np.zeros(WINDOW_SIZE, dtype=np.uint8)
    cv2.imshow('Snapshot',cv2.cvtColor(snapshot, cv2.COLOR_BGR2RGB))
    cv2.setMouseCallback('Snapshot', on_mouse_click)

    # init color array
    colorArray = np.zeros((COLOR_ROWS, COLOR_COLS, 3), dtype=np.uint8)
    cv2.imshow('Color', colorArray)

    is_run = True
    snapshot = None
    while is_run:
        # Convert to array
        img_window = np.array(ImageGrab.grab(bbox=win32gui.GetWindowRect(screens[0])))
        # Resize
        img_mhw = cv2.resize(img_window, WINDOW_SIZE, interpolation=cv2.INTER_AREA)
        (h, w, _) = img_mhw.shape

        cv2.imshow('window',cv2.cvtColor(img_mhw, cv2.COLOR_BGR2RGB))

        keyVal = cv2.waitKey(1) & 0xFF
        if keyVal == ord('q'):
            break
        elif keyVal == ord('t'):
            snapshot = img_mhw.copy()
            if REVERSE_RGB:
                snapshot = cv2.cvtColor(snapshot, cv2.COLOR_BGR2RGB)
            cv2.imshow('Snapshot',snapshot)
        time.sleep(0.2)
    cv2.destroyAllWindows()