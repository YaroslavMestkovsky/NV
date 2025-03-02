import os
import numpy as np
import win32gui
import win32ui
import win32con
from datetime import datetime
from PIL import Image


class ScreenshotManager:
    """Менеджер для захвата скриншотов окна игры с исправлениями."""

    def __init__(self, logger):
        self.logger = logger
        self.game_window_title = "Warspear Online"
        self.game_window_size = (1280, 920)
        self.game_window_handle = self._find_game_window()

        # Кэшированные параметры
        self._cached_params = None

        if self.game_window_handle:
            self._resize_game_window()
            self._init_window_rect()
            self._precalculate_params()

    def _precalculate_params(self):
        """Корректный расчет параметров захвата."""
        self._cached_params = {
            'width': self.width,
            'height': self.height,
            'cropped_x': 8,  # border_pixels
            'cropped_y': 30,  # titlebar_pixels
            'dtype': np.uint8,
            'mode': 'RGB'
        }

    def _find_game_window(self):
        handle = win32gui.FindWindow(None, self.game_window_title)
        if not handle:
            self.logger.log(f"Окно '{self.game_window_title}' не найдено.")
            return None
        self.logger.log(f"Окно игры найдено: {self.game_window_title}")
        return handle

    def _resize_game_window(self):
        rect = win32gui.GetWindowRect(self.game_window_handle)
        win32gui.SetWindowPos(
            self.game_window_handle,
            win32con.HWND_TOP,
            rect[0], rect[1],
            self.game_window_size[0],
            self.game_window_size[1],
            win32con.SWP_SHOWWINDOW
        )
        self.logger.log(f"Размер окна изменен: {self.game_window_size[0]}x{self.game_window_size[1]}")

    def _init_window_rect(self):
        rect = win32gui.GetWindowRect(self.game_window_handle)
        self.width = rect[2] - rect[0]
        self.height = rect[3] - rect[1]

        # Корректировка размеров с учетом рамок (8px с каждой стороны)
        self.width -= 16
        # Корректировка высоты (30px заголовок + 8px снизу)
        self.height -= 38

    def take_screenshot(self, screenshot_folder):
        if not self.game_window_handle or not self._cached_params:
            self.logger.log("Окно игры не инициализировано.")
            return

        wDC = None
        dcObj = None
        cDC = None
        dataBitMap = None

        try:
            # Получаем контекст устройства
            wDC = win32gui.GetWindowDC(self.game_window_handle)
            dcObj = win32ui.CreateDCFromHandle(wDC)
            cDC = dcObj.CreateCompatibleDC()

            # Создаем битмап с корректными размерами
            dataBitMap = win32ui.CreateBitmap()
            dataBitMap.CreateCompatibleBitmap(dcObj, self.width, self.height)
            cDC.SelectObject(dataBitMap)

            # Копируем данные экрана
            cDC.BitBlt(
                (0, 0),
                (self.width, self.height),
                dcObj,
                (self._cached_params['cropped_x'], self._cached_params['cropped_y']),
                win32con.SRCCOPY,
            )

            # Получаем данные битмапа
            bitmap_data = dataBitMap.GetBitmapBits(True)

            # Создаем numpy array с правильными размерами
            img_array = np.frombuffer(bitmap_data, dtype=self._cached_params['dtype'])
            img_array = img_array.reshape((self.height, self.width, 4))

            # Конвертация цветов и удаление альфа-канала
            img_array = img_array[..., [2, 1, 0]][..., :3].copy()

            # Сохранение изображения
            img_path = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            Image.fromarray(
                img_array,
                self._cached_params['mode'],
            ).save(
                os.path.join(screenshot_folder, img_path),
                optimize=True,
                compress_level=3,
            )
            self.logger.log(f'Сохранен скриншот: {img_path}')

        except Exception as e:
            self.logger.log(f"Ошибка захвата: {str(e)}")
        finally:
            # Освобождаем ресурсы в правильном порядке
            if dataBitMap:
                try:
                    win32gui.DeleteObject(dataBitMap.GetHandle())
                except Exception as e:
                    self.logger.log(f"Ошибка удаления битмапа: {str(e)}")
            if cDC:
                try:
                    cDC.DeleteDC()
                except Exception as e:
                    self.logger.log(f"Ошибка удаления cDC: {str(e)}")
            if dcObj:
                try:
                    dcObj.DeleteDC()
                except Exception as e:
                    self.logger.log(f"Ошибка удаления dcObj: {str(e)}")
            if wDC:
                try:
                    win32gui.ReleaseDC(self.game_window_handle, wDC)
                except Exception as e:
                    self.logger.log(f"Ошибка освобождения контекста: {str(e)}")

    def close(self):
        """Очистка ресурсов"""
        self._cached_params = None
