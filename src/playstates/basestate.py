import pygame

from src.level_building.button import Button
from src.util import ButtonState


class BaseState:
    """Класс, который наследуется всеми игровыми состояниями"""

    def __init__(self):
        self.need_screen_update = False  # Когда этот флаг становится True, экран обновляется и сбрасывает значение

    """
    Переписываемые функции состояния
    """

    def handle_input(self, event: pygame.event.Event):
        """Обработка нажатия кнопок"""
        pass

    def handle_hold_input(self, pressed_keys):
        """Обработка нажатия и удержания кнопок"""
        pass

    def handle_button_release(self, event: pygame.event.Event, pressed_keys):
        """Обработка отпускания кнопок"""
        pass

    def handle_mouse_motion(self, event: pygame.event.Event):
        """Обработка позиции курсора мыши"""
        pass

    def handle_mouse_click(self, event: pygame.event.Event):
        """Обработка щелчка мышью"""
        pass

    def handle_mouse_release(self, event: pygame.event.Event):
        """Обработка отпускания кнопок мыши"""
        pass

    def execute_before_draw(self):
        """Отправление особой команды циклу игры"""
        return None

    def draw(self, screen: pygame.Surface):
        """Отрисовка {того, за что отвечает состояние}"""
        pass

    def execute_after_draw(self):
        """Отправление особой команды циклу игры"""
        return None

    def update_input_field(self, field_text: str, event: pygame.event.Event):
        """Обновление текстового поля введённым символом"""

        updated = True
        if event.key == pygame.K_BACKSPACE:
            field_text = field_text[:-1]
        elif (
            event.unicode
            and 31 < ord(event.unicode)
            and ord(event.unicode) not in (127,)
        ):
            # TODO: uhh find all unrenderable characters?? idk ;(
            field_text += event.unicode
        else:
            updated = False

        if updated:
            self.need_screen_update = True
        return field_text, updated

    def update_button_on_hovering(self, button: Button, event: pygame.event.Event):
        """Подсвечивание кнопки, когда на неё наведён курсор, и снятие подсветки, когда курсор убран"""

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
            self.need_screen_update = True
        return updated

    def update_buttons_on_press(
        self, button: Button, buttons_to_unpress: tuple[Button] = None
    ):
        """Зажатие подсвеченной кнопки, когда происходит щелчок мышью"""

        if button.state == ButtonState.HOVERED:
            button.state = ButtonState.PRESSED
            # Отжатие других кнопок (если необходимо)
            if buttons_to_unpress:
                for unpress_button in buttons_to_unpress:
                    unpress_button.state = (
                        ButtonState.REGULAR
                        if not unpress_button is button
                        else ButtonState.PRESSED
                    )
            self.need_screen_update = True
            return True
        else:
            return False
