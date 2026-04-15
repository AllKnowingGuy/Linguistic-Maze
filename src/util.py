import os
import sys
from enum import Enum
from pathlib import Path

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
    WAIT = 2  # Временно перестать обновлять экран
    SET_FPS = 3  # Изменить частоту обновления экрана
    CHECK_PROGRESS = 4  # Проверить и обновить прогресс в StoryScript
    UPDATE_DISPLAY = 5  # Обновить дисплей игры (не влияет на счётчик FPS)
    ADD_SOUNDS = 6  # Добавить звук в кэш для регулировки громкости
    UPDATE_MAIN_SETTINGS = (
        7  # Обновить настройки, которые распространяются на все состояния
    )


def get_centered_point(length: float, is_height: bool = False):
    if is_height:
        return SCREEN_HEIGHT / 2 - length / 2
    else:
        return SCREEN_WIDTH / 2 - length / 2


def resource_path(relative_path: str | Path, return_as_str: bool = False) -> str | Path:
    """Получает путь к файлу. Нужен, чтобы программа видела файлы как в IDE, так и в собранном виде."""
    try:
        # Атрибут _MEIPASS появляется, когда программа собрана PyInstaller
        # В этом случае файлы лежат рядом с exe
        base_path = sys._MEIPASS
    except AttributeError:
        # Если программа запущена как скрипт (python main.py) - файлы ищем в папке с проектом
        base_path = os.path.abspath(".")

    final_path = os.path.join(base_path, relative_path)
    return final_path if return_as_str else Path(final_path)


"""
Для MenuState
"""

START_BUTTON_WIDTH = 300
START_BUTTON_HEIGHT = 350
BIND_BUTTON_WIDTH = 110
BIND_BUTTON_HEIGHT = 110


"""
Для Maze и MazeState (а также StoryScript и assetscreation)
"""

TILE_SIZE = 45
PLAYER_SIZE = (
    34  # при расчёте позиции игрока делится пополам, поэтому лучше брать чётные числа
)


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
Для DialogueState и ChallengeState (а также assetscreation)
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
