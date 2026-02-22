class BaseState:
    """Класс, который наследуют все игровые состояния"""
    def __init__(self):
        pass

    """
    Базовые функции состояния
    """

    def handle_input(self, event, pressed_keys):
        """Обработка нажатия кнопок"""
        pass

    def handle_mouse_motion(self, mouse_pos):
        """Обработка позиции курсора мыши"""
        pass

    def handle_mouse_click(self, pressed_buttons):
        """Обработка щелчка мышью"""
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
