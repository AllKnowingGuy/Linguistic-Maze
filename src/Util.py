from enum import Enum


class WallPattern(Enum):
    """Базовые паттерны стен"""
    SINGLE = 1  # Отдельная стена
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
