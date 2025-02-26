class Logger:
    """Логирование в виджет и в консоль."""

    def __init__(self, log_widget=None):
        self.log_widget = log_widget

    def log(self, message):
        if self.log_widget:
            self.log_widget.append(message)

        print(message)
