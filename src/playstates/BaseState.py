import pygame

from src.Util import ButtonState


class BaseState:
    """Класс, который наследуется всеми игровыми состояниями"""
    def __init__(self):
        self.needs_screen_update = False

    """
    Переписываемые функции состояния
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

    def update_input_field(self, field_text, event):
        updated = True
        if event.key == pygame.K_BACKSPACE:
            field_text = field_text[:-1]
        elif event.key not in (pygame.K_ESCAPE, pygame.K_TAB, pygame.K_DELETE, pygame.K_RETURN):
            field_text += event.unicode
        else:
            updated = False

        if updated:
            self.needs_screen_update = True
        return field_text, updated

    def update_button_on_hovering(self, button, event):
        updated = False
        if button.is_hovered(event.pos):
            if button.state == ButtonState.REGULAR:
                # Когда курсор поверх кнопки в первый раз - подсвечиваем
                button.state = ButtonState.HOVERED
                updated = True
        elif button.state == ButtonState.HOVERED:
            # Когда убираем курсор, но до этого держали над кнопкой - убираем подсветку
            button.state = ButtonState.REGULAR
            updated = True

        if updated:
            self.needs_screen_update = True
        return updated

