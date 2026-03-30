from enum import Enum

"""
Для всей игры
"""

SCREEN_WIDTH = 1280  # при текущих ширине экрана и размере клеток ширина лабиринта должна быть 29 и больше
SCREEN_HEIGHT = 720  # при текущих высоте экрана и размере клеток высота лабиринта должна быть 17 и больше


FILENAME_DISPLAY_PROTAG_DICT = {
    "anya": "Аня",
    "denis": "Денис",
    "lera": "Лера",
    "danya": "Даня",
}


class StateType(Enum):
    """Типы состояний, в которых находится игра"""

    MAZE = 1
    DIALOGUE = 2
    CHALLENGE = 3
    MENU = 4


class Command(Enum):
    """Команды циклу игры"""

    STOP = 1  # Прекратить себя
    WAIT = 2  # Временно перестать обновляться
    SET_FPS = 3  # Изменить частоту обновления
    CHECK_PROGRESS = 4  # Проверить и обновить прогресс
    UPDATE_DISPLAY = 5  # Обновить дисплей игры (не влияет на счётчик FPS)


def get_centered_point(length: float, is_height: bool = False):
    if is_height:
        return SCREEN_HEIGHT / 2 - length / 2
    else:
        return SCREEN_WIDTH / 2 - length / 2


"""
Для MenuState
"""

START_BUTTON_WIDTH = 150
START_BUTTON_HEIGHT = 90
BIND_BUTTON_WIDTH = 113
BIND_BUTTON_HEIGHT = 90


"""
Для Maze и MazeState (а также StoryScript и AssetsCreation)
"""

TILE_SIZE = 45
PLAYER_SIZE = (
    34  # при расчёте позиции игрока делится пополам, поэтому лучше брать чётные числа
)


# TODO: maybe make the player rectangular and not square?


class WallPattern(Enum):
    """Базовые паттерны стен"""

    SINGLE = 1  # Основание стены
    STRAIGHT = 2  # Стена вдоль границы
    STRAIGHT_SOUTH = 3  # Стена вдоль "нижней" границы
    CORNER = 4  # Угол стены (для соединения перпендикулярных стен)
    CORNER_SOUTH = 5  # Угол стены вдоль "нижней" границы


class Border(Enum):
    """Границы лабиринта"""

    NORTH = "NORTH"  # "Верхняя" граница
    WEST = "WEST"  # Левая граница
    EAST = "EAST"  # Правая граница
    SOUTH = "SOUTH"  # "Нижняя" граница


"""
Для DialogueState и ChallengeState (а также AssetsCreation)
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
