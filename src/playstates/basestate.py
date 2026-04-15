from pathlib import Path

import pygame

from src import assetscreation
from src.level_building.button import Button
from src.level_building.checker import Checker
from src.util import ButtonState


class BaseState:
    """Класс, который наследуется всеми игровыми состояниями"""

    def __init__(self, checker: Checker | None = None):
        self.need_screen_update = False  # Когда этот флаг становится True, экран обновляется и сбрасывает значение
        self.ps_font = assetscreation.load_font(
            Path("assets\\fonts\\BleekerCyrillic.ttf"), size=28
        )
        if checker:
            self.checker = checker

    """
    Переписываемые функции состояния
    """

    def add_sounds_for_volume_change(self):
        """Возврат неменяющихся звуков для внутриигрового изменения громкости"""
        pass

    def handle_input(self, event: pygame.event.Event):
        """
        Обработка нажатия кнопок

        Args:
            event (Event): событие нажатия клавиши
        """
        pass

    def handle_hold_input(self, pressed_keys):
        """Обработка нажатия и удержания кнопок"""
        pass

    def handle_button_release(self, event: pygame.event.Event, pressed_keys):
        """Обработка отпускания кнопок"""
        pass

    def handle_mouse_motion(self, event: pygame.event.Event):
        """
        Обработка позиции курсора мыши

        Args:
            event (Event): событие движения мыши
        """
        pass

    def handle_mouse_click(self, event: pygame.event.Event):
        """
        Обработка щелчка мышью

        Args:
            event (Event): событие щелчка мышью
        """
        pass

    def handle_mouse_release(self, event: pygame.event.Event):
        """
        Обработка отпускания кнопок мыши

        Args:
            event (Event): событие отпускания кнопки мыши
        """
        pass

    def execute_before_draw(self):
        """Отправление команды циклу игры перед отрисовкой"""
        return None

    def draw(self, screen: pygame.Surface):
        """
        Отрисовка того, за что отвечает состояние

        Args:
            screen (Surface): экран-поверхность для отрисовки
        """
        pass

    def execute_after_draw(self):
        """Отправление команды циклу игры после отрисовки"""
        return None

    def update_input_field(
        self, field_text: str, event: pygame.event.Event
    ) -> tuple[str, bool]:
        """
        Обновление текстового поля введённым символом

        Args:
            field_text (str): текст поля ввода
            event (Event): событие нажатия клавиши

        Returns:
            tuple[str, bool]: новый текст поля ввода и отметка о том, был ли изменён текст
        """

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

    def update_button_on_hovering(
        self, button: Button, event: pygame.event.Event
    ) -> bool:
        """
        Подсвечивание кнопки, когда на неё наведён курсор, и снятие подсветки, когда курсор убран

        Args:
            button (Button): кнопка для подсвечивания
            event (Event): событие движения мыши

        Returns:
            bool: была ли обновлена кнопка
        """

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
    ) -> bool:
        """
        Зажатие подсвеченной кнопки, когда происходит щелчок мышью

        Args:
            button (Button): кнопка для анимации зажатия
            buttons_to_unpress (tuple[Button]): кнопки, у которых нужно убрать подсветку

        Returns:
            bool: изменилась ли хотя бы одна кнопка
        """

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
