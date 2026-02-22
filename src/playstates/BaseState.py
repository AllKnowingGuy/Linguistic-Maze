class BaseState:
    """Класс, который наследуют все игровые состояния"""
    def __init__(self):
        pass

    """
    Базовые функции состояния
    """

    def handle_input(self, keys):
        """Обработка нажатия кнопок"""
        pass

    def execute_before_draw(self):
        """Отправление особой команды циклу игры"""
        return None

    def draw(self, screen):
        """Отрисовка {того, за что отвечает состояние}"""
        pass

    def execute_after_draw(self):
        """Отправление особой команды циклу игры"""
        return None
