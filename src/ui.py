from PyQt5.QtWidgets import (
    QWidget,
    QPushButton,
    QVBoxLayout,
    QTextEdit,
)
from PyQt5.QtCore import (
    QTimer,
)


class ScreenshotApp(QWidget):
    """Основной интерфейс."""

    def __init__(self, screenshot_manager, logger):
        super().__init__()
        self.screenshot_manager = screenshot_manager
        self.logger = logger
        self.screenshot_folder = "screenshots"
        self.timer = QTimer()
        self.capture_active = False
        self._init_components()

        self.logger.log_widget = self.log_output

    def _init_components(self):
        # Создание кнопок
        self.start_button = QPushButton('Запуск захвата', self)
        self.stop_button = QPushButton('Остановка захвата', self)
        self.exit_button = QPushButton('Выход', self)

        # Создание текстового поля для лога
        self.log_output = QTextEdit(self)
        self.log_output.setReadOnly(True)

        # Подключение функций к кнопкам
        self.start_button.clicked.connect(self.start_capture)
        self.stop_button.clicked.connect(self.stop_capture)
        self.exit_button.clicked.connect(self.close)

        # Размещение кнопок и текстового поля в layout
        layout = QVBoxLayout()
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.exit_button)
        layout.addWidget(self.log_output)

        # Настройка окна
        self.setLayout(layout)
        self.setWindowTitle('Скриншоты Warspear Online')
        self.setGeometry(300, 300, 400, 300)

    def start_capture(self):
        if not self.capture_active:
            self.capture_active = True
            self.timer.start(3000)  # Запуск таймера с интервалом 3 секунды
            self.logger.log("Захват скриншотов запущен.")
        else:
            self.logger.log("Захват уже запущен.")

    def stop_capture(self):
        if self.capture_active:
            self.capture_active = False
            self.timer.stop()  # Остановка таймера
            self.logger.log("Захват скриншотов остановлен.")
        else:
            self.logger.log("Захват уже остановлен.")

    def take_screenshot(self):
        if self.capture_active:
            self.screenshot_manager.take_screenshot(self.screenshot_folder)
