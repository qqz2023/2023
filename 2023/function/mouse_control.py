import csv
import os
import sys
from pathlib import Path

from pynput import mouse

from function.mouse_dll.mouse import Mouse

mouse_left_click = False
mouse_right_click = False
grab_size = 640

mouses = mouse.Controller()

FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))
info_dir = os.path.join(ROOT, 'information.csv')
with open(info_dir, 'r', encoding='utf-8', newline='') as fr:
    reader = csv.DictReader(fr)
    for r in reader:
        pass
    screen_size = r['screen_size']
fr.close()

screen_size = screen_size.split('*')
screen_size = (int(screen_size[0]), int(screen_size[1]))

screen_width, screen_height = screen_size
grab = (int((screen_size[0] - grab_size) / 2), int((screen_size[1] - grab_size) / 2), grab_size, grab_size)
grab_x, grab_y, grab_width, grab_height = grab
pos_center = (int(screen_width / 2), int(screen_height / 2))
max_pos = int(pow((pow(pos_center[0], 2) + pow(pos_center[1], 2)), 0.5))
mouse_x, mouse_y = pos_center

mouses = mouse.Controller()


def on_click(x, y, button, pressed):
    global mouse_left_click, mouse_right_click
    if pressed:
        if button == mouse.Button.left:
            mouse_left_click = True
        elif button == mouse.Button.right:
            mouse_right_click = True
    else:
        mouse_left_click = False
        mouse_right_click = False


def track_target_ratio(box_lists):
    pos_min = (0, 0)
    if len(box_lists) != 0:
        dis_min = max_pos
        for _box in box_lists:
            x_target = int(_box[1] * grab_width + grab_x)
            y_target = int(_box[2] * grab_height + grab_y)
            if (x_target - pos_center[0]) ** 2 + (y_target - pos_center[1]) < dis_min ** 2:
                dis_min = (x_target - pos_center[0]) ** 2 + (y_target - pos_center[1])
                pos_min = (x_target - pos_center[0], y_target - pos_center[1])
        return pos_min[0], pos_min[1], 1
    else:
        return 0, 0, 0


def usb_control(conn2):
    listener_mouse = mouse.Listener(on_click=on_click)
    listener_mouse.start()

    while True:

        dicts = conn2.recv()
        box_list = dicts['box_list']

        flag_lock_obj_both = dicts['flag_lock_obj_both']
        flag_lock_obj_left = dicts['flag_lock_obj_left']
        flag_lock_obj_right = dicts['flag_lock_obj_right']

        offset_pixel_center = dicts['offset_pixel_center']
        mouses_offset_ratio = dicts['mouses_offset_ratio']
        offset_pixel_y = dicts['offset_pixel_y']
        out_check = dicts['out_check']

        if out_check:
            break

        pos_min = track_target_ratio(box_list)

        if flag_lock_obj_both:
            if (mouse_left_click and mouse_right_click) and (
                    (pos_min[0] ** 2 + pos_min[1] ** 2) >= offset_pixel_center ** 2) and pos_min[2]:
                Mouse.mouse.move(int(pos_min[0] * mouses_offset_ratio),
                                 int((pos_min[1] + offset_pixel_y) * mouses_offset_ratio))
        else:
            if ((mouse_left_click and flag_lock_obj_left) or (mouse_right_click and flag_lock_obj_right)) and (
                    (pos_min[0] ** 2 + pos_min[1] ** 2) >= offset_pixel_center ** 2) and pos_min[2]:
                Mouse.mouse.move(int(pos_min[0] * mouses_offset_ratio),
                                 int((pos_min[1] + offset_pixel_y) * mouses_offset_ratio))
