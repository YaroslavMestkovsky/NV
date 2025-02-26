import os
import win32gui
import win32ui
import win32con
from datetime import (
    datetime,
)
from ctypes import (
    windll,
)
from PIL import (
    Image,
)


class ScreenshotManager:
    """Менеджер основной логики получения скриншотов."""

    def __init__(self, logger):
        self.logger = logger
        self.game_window_title = "Warspear Online"
        self.game_window_size = (800, 600)
        self.game_window_handle = self._find_game_window()

        if self.game_window_handle:
            self._resize_game_window()

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

    def take_screenshot(self, screenshot_folder):
        result = None

        if not self.game_window_handle:
            result = None

        try:
            # Получение координат окна игры
            left, top, right, bottom = win32gui.GetWindowRect(self.game_window_handle)
            width, height = right - left, bottom - top

            # Создание контекста устройства
            hdc = win32gui.GetWindowDC(self.game_window_handle)
            dc = win32ui.CreateDCFromHandle(hdc)
            compatible_dc = dc.CreateCompatibleDC()

            # Создание битмапа для захвата
            bitmap = win32ui.CreateBitmap()
            bitmap.CreateCompatibleBitmap(dc, width, height)
            compatible_dc.SelectObject(bitmap)

            # Захват содержимого окна
            windll.user32.PrintWindow(self.game_window_handle, compatible_dc.GetSafeHdc(), 2)

            # Сохранение битмапа во временный файл BMP
            bmp_filename = os.path.join(screenshot_folder, "temp_screenshot.bmp")
            bitmap.SaveBitmapFile(compatible_dc, bmp_filename)

            # Конвертация BMP в PNG
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            png_filename = os.path.join(screenshot_folder, f"screenshot_{timestamp}.png")

            with Image.open(bmp_filename) as img:
                img.save(png_filename, "PNG")

            # Удаление временного BMP-файла
            os.remove(bmp_filename)

            # Очистка ресурсов
            dc.DeleteDC()
            compatible_dc.DeleteDC()
            win32gui.ReleaseDC(self.game_window_handle, hdc)
            win32gui.DeleteObject(bitmap.GetHandle())

            self.logger.log(f"Скриншот сохранён: {png_filename}")
            result = png_filename
        except Exception as e:
            self.logger.log(f"Ошибка при создании скриншота: {e}")

        return result
