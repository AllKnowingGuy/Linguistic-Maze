from src.util import ButtonState


class Button:
    """
    Кнопка: структурные параметры и метод проверки наведения курсора на кнопку
    """

    def __init__(self, x: int, y: int, width: int, height: int, text: str):
        """
        Создание кнопки

        Args:
            x (int): координата по оси абсцисс
            y (int): координата по оси ординат
            width (int): ширина кнопки
            height (int): высота кнопки
            text (str): текст кнопки для подписи и/или идентификации
        """

        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.state = (
            ButtonState.REGULAR
        )  # состояние кнопки: обычная, наведённая, нажатая или выключенная

    def is_hovered(self, mouse_pos: list[int] | tuple[int, int]) -> bool:
        """
        Проверка того, что курсор мыши наведён на кнопку

        Args:
            mouse_pos (list[int] | tuple[int, int]): координаты курсора

        Returns:
            bool: наведён курсор или нет
        """

        return (
            self.x <= mouse_pos[0] <= self.x + self.width
            and self.y <= mouse_pos[1] <= self.y + self.height
        )
