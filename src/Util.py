from enum import Enum

"""
Для всей игры
"""

SCREEN_WIDTH = 1050 # при текущих ширине экрана и размере клеток ширина лабиринта должна быть 25 и больше
SCREEN_HEIGHT = 630 # при текущих высоте экрана и размере клеток высота лабиринта должна быть 15 и больше


class StateType(Enum):
    """Типы состояний, в которых находится игра"""
    MAZE = 1
    DIALOGUE = 2
    CHALLENGE = 3


class Command(Enum):
    """Команды циклу игры"""
    STOP = 1 # Прекратить себя
    WAIT = 2 # Временно перестать обновляться
    SET_FPS = 3 # Изменить частоту обновления
    CHECK_PROGRESS = 4 # Проверить и обновить прогресс


"""
Для Maze и MazeState
"""

TILE_SIZE = 45
PLAYER_SIZE = 34 # при расчёте позиции игрока делится пополам, поэтому лучше брать чётные числа
# TODO: maybe make the player rectangular and not square?


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


"""
Для DialogueState и ChallengeState
"""

CHOICE_BUTTON_SIZE = 30
CHAL_BUTTON_WIDTH = 150
CHAL_BUTTON_HEIGHT = 90


class ButtonState(Enum):
    """Состояния кнопки"""
    REGULAR = 1
    HOVERED = 2
    PRESSED = 3
    DISABLED = 4


class Awaiting(Enum):
    """Действия игрока на определённом этапе"""
    CONTINUE = 1
    CHOOSE = 2
    INPUT = 3

