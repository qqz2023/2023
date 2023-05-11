import cv2
import numpy as np
import win32api
import win32con
import win32gui
import win32ui

hwnd_title = dict()


def get_all_hwnd(hwnd, mouse):
    if win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(hwnd) and win32gui.IsWindowVisible(hwnd):
        hwnd_title.update({hwnd: win32gui.GetWindowText(hwnd)})


def update_hwnd_title():
    win32gui.EnumWindows(get_all_hwnd, 0)
    hwnd_list = []
    for h, t in hwnd_title.items():
        if t != "":
            hwnd_list.append(t)
    return hwnd_list


def win32_capture(grab_info):
    hwnd = 0

    hwndDC = win32gui.GetWindowDC(hwnd)

    mfcDC = win32ui.CreateDCFromHandle(hwndDC)

    saveDC = mfcDC.CreateCompatibleDC()

    saveBitMap = win32ui.CreateBitmap()

    gx, gy, gs = grab_info
    gw = gs
    gh = gs

    saveBitMap.CreateCompatibleBitmap(mfcDC, gw, gh)

    saveDC.SelectObject(saveBitMap)

    saveDC.BitBlt((0, 0), (gw, gh), mfcDC, (gx, gy), win32con.SRCCOPY)

    signed_ints_array = saveBitMap.GetBitmapBits(True)
    img = np.frombuffer(signed_ints_array, dtype='uint8')
    img.shape = (gh, gw, 4)
    img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)

    win32gui.DeleteObject(saveBitMap.GetHandle())
    mfcDC.DeleteDC()
    saveDC.DeleteDC()

    return img


if __name__ == '__main__':
    MoniterDev = win32api.EnumDisplayMonitors(None, None)

    cv2.waitKey(1)
    while True:
        img = win32_capture((853, 293, 853))
        cv2.imshow('test', img)
        cv2.waitKey(1)
