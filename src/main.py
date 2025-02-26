import sys
from PyQt5.QtWidgets import (
    QApplication,
)
from logger import (
    Logger,
)
from screenshot_manager import (
    ScreenshotManager,
)
from ui import (
    ScreenshotApp,
)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Инициализация логгера
    logger = Logger()

    # Инициализация интерфейса
    window = ScreenshotApp(None, logger)
    window.show()

    # Передаем log_widget в логгер
    logger.log_widget = window.log_output

    # Инициализация менеджера скриншотов
    screenshot_manager = ScreenshotManager(logger)

    # Обновляем screenshot_manager в интерфейсе
    window.screenshot_manager = screenshot_manager

    # Подключение таймера к методу take_screenshot
    window.timer.timeout.connect(window.take_screenshot)

    sys.exit(app.exec_())
