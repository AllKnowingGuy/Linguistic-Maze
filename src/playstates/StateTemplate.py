"""
Основано на структуре MazeState
"""

import pygame
from src import AssetsCreation
"""
В AssetsLoading нужно будет написать функции для загрузки нужных ассетов,
если вы не переиспользуете ассеты из других состояний
"""


class State:
    def __init__(self):
        pass

    """
    Базовые функции состояния
    """

    def handle_input(self, keys):
        """Обработка ввода с клавиатуры"""
        pass

    def draw(self, screen):
        """Отрисовка {того, за что отвечает состояние}"""
        pass
