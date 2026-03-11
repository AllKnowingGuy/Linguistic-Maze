class BaseState:
    """Класс, который наследуется всеми игровыми состояниями"""
    def __init__(self):
        pass

    """
    Базовые функции состояния
    """

    def handle_input(self, event):
        """Обработка нажатия кнопок"""
        pass

    def handle_hold_input(self, pressed_keys):
        """Обработка нажатия и удержания кнопок"""
        pass

    def handle_button_release(self, event, pressed_keys):
        """Обработка отпускания кнопок"""
        pass

    def handle_mouse_motion(self, event):
        """Обработка позиции курсора мыши"""
        pass

    def handle_mouse_click(self, event):
        """Обработка щелчка мышью"""
        pass

    def handle_mouse_release(self, event):
        """Обработка отпускания кнопок мыши"""
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
