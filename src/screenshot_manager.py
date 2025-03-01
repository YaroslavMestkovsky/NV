import os

import numpy as np
import win32gui
import win32ui
import win32con
from datetime import (
    datetime,
)
from PIL import (
    Image,
)


class ScreenshotManager:
    """Менеджер основной логики получения скриншотов."""

    def __init__(self, logger):
        self.logger = logger
        self.game_window_title = "Warspear Online"
        self.game_window_size = (1280, 920)
        self.game_window_handle = self._find_game_window()

        if self.game_window_handle:
            self._resize_game_window()
            self._init_window_rect()

    def _find_game_window(self):
        handle = win32gui.FindWindow(None, self.game_window_title)

        if handle == 0:
            self.logger.log(f"Окно с названием '{self.game_window_title}' не найдено.")
            handle = None
        else:
            self.logger.log(f"Окно игры найдено: {self.game_window_title}")

        return handle

    def _resize_game_window(self):
        left, top, right, bottom = win32gui.GetWindowRect(self.game_window_handle)
        width, height = self.game_window_size

        win32gui.SetWindowPos(
            self.game_window_handle,
            win32con.HWND_TOP,
            left, top, width, height,
            win32con.SWP_SHOWWINDOW,
        )

        self.logger.log(f"Окно игры изменено до размера: {width}x{height}")

    def _init_window_rect(self):
        left, top, right, bottom = win32gui.GetWindowRect(self.game_window_handle)
        self.width, self.height = right - left, bottom - top

        border_pixels = 8
        titlebar_pixels = 30
        bottom_crop_pixels = 15

        self.width -= (border_pixels * 2)
        self.height -= titlebar_pixels - border_pixels + bottom_crop_pixels
        self.cropped_x = border_pixels
        self.cropped_y = titlebar_pixels

    def take_screenshot(self, screenshot_folder):
        if not self.game_window_handle:
            self.logger.log('Не задано окно игры.')

        try:
            wDC = win32gui.GetWindowDC(self.game_window_handle)
            dcObj = win32ui.CreateDCFromHandle(wDC)

            # скриншоты
            cDC = dcObj.CreateCompatibleDC()
            dataBitMap = win32ui.CreateBitmap()
            dataBitMap.CreateCompatibleBitmap(dcObj, self.width, self.height)
            cDC.SelectObject(dataBitMap)
            cDC.BitBlt((0, 0), (self.width, self.height), dcObj, (self.cropped_x, self.cropped_y), win32con.SRCCOPY)

            signedIntsArray = dataBitMap.GetBitmapBits(True)
            img = np.fromstring(signedIntsArray, dtype='uint8')
            img.shape = (self.height, self.width, 4)

            dcObj.DeleteDC()
            cDC.DeleteDC()
            win32gui.ReleaseDC(self.game_window_handle, wDC)
            win32gui.DeleteObject(dataBitMap.GetHandle())

            img = img[..., :3]
            img = np.ascontiguousarray(img)
            im = Image.fromarray(img[..., [2, 1, 0]])

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            png_filename = os.path.join(screenshot_folder, f"screenshot_{timestamp}.png")
            im.save(png_filename)

            self.logger.log(f"Скриншот сохранён: {png_filename}")

        except Exception as e:
            self.logger.log(f"Ошибка при создании скриншота: {e}")
