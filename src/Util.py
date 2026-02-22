from enum import Enum


SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 650
TILE_SIZE = 25


class Command(Enum):
    """Команды циклу игры"""
    STOP = 1 # Прекратить себя
    WAIT = 2 # Временно перестать реагировать
    SET_FPS = 3 # Изменить частоту реагирования


class WallPattern(Enum):
    """Базовые паттерны стен"""
    SINGLE = 1  # Основание стены
    STRAIGHT = 2 # Стена вдоль границы
    STRAIGHT_SOUTH = 3 # Стена вдоль "нижней" границы
    CORNER = 4 # Угол стены (для соединения перпендикулярных стен)
    CORNER_SOUTH = 5  # Угол стены вдоль "нижней" границы


class Border(Enum):
    """Границы лабиринта"""
    NORTH = 'NORTH'  # "Верхняя" граница
    WEST = 'WEST'  # Левая граница
    EAST = 'EAST'  # Правая граница
    SOUTH = 'SOUTH'  # "Нижняя" граница
