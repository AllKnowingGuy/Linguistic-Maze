import os
import pygame

from src.Util import * # screw it - Vsevolod


def load_one_object(path: str, width: float, height: float):
    loaded_object = None
    try:
        loaded_object = pygame.image.load(path)
        loaded_object = pygame.transform.scale(loaded_object, (width, height))
        print(f"Загружен {path}")
    except Exception as e:
        print(f"Ошибка загрузки {path}: {e}")
    return loaded_object


def load_all_objects(root_path: str, path_map: dict[Enum, str], widths_heights_map: dict[Enum, tuple[float, float]]):
    loaded_objects = {}
    for obj_type, filename in path_map.items():
        filepath = os.path.join(root_path, filename)
        if os.path.exists(filepath):
            width, height = widths_heights_map[obj_type]
            image = load_one_object(filepath, width, height)
            loaded_objects[obj_type] = image
    return loaded_objects


"""
Для MazeState
"""


def add_entrance_exit_tiles():
    """Загрузка кастомных изображений для входа и выхода"""

    entrance_path = '../assets/tiles/entrance.png'
    entrance_tile = load_one_object(entrance_path, TILE_SIZE, TILE_SIZE)
    exit_path = '../assets/tiles/exit.png'
    exit_tile = load_one_object(exit_path, TILE_SIZE, TILE_SIZE)

    return entrance_tile, exit_tile


def add_player_tile():
    """Загрузка тайла игрока"""
    player_path = '../assets/tiles/player.png'
    return load_one_object(player_path, TILE_SIZE, TILE_SIZE)


def add_floor_tile():
    """Загрузка тайла пола"""
    floor_path = '../assets/tiles/floor.png'
    return load_one_object(floor_path, TILE_SIZE, TILE_SIZE)


def add_wall_tiles():
    """Загрузка тайлов стен"""
    tiles_path = '../assets/tiles/walls'
    tile_files = {
        WallPattern.SINGLE: 'wall_single.png',
        WallPattern.STRAIGHT: 'wall_straight.png',
        WallPattern.STRAIGHT_SOUTH: 'wall_straight_south.png',
        WallPattern.CORNER: 'wall_corner.png',
        WallPattern.CORNER_SOUTH: 'wall_corner_south.png'
    }
    tile_sizes = {
        WallPattern.SINGLE: (TILE_SIZE, TILE_SIZE),
        WallPattern.STRAIGHT: (TILE_SIZE, TILE_SIZE),
        WallPattern.STRAIGHT_SOUTH: (TILE_SIZE, TILE_SIZE),
        WallPattern.CORNER: (TILE_SIZE, TILE_SIZE),
        WallPattern.CORNER_SOUTH: (TILE_SIZE, TILE_SIZE)
    }
    return load_all_objects(tiles_path, tile_files, tile_sizes)


"""
Для DialogueState
"""


def add_dialogue_bg():
    """Загрузка фона диалога"""
    bg_path = '../assets/dialogue/bg.png'
    return load_one_object(bg_path, SCREEN_WIDTH, SCREEN_HEIGHT)


def add_dialogue_box():
    """Загрузка диалоговой плашки"""
    box_path = '../assets/dialogue/box.png'
    return load_one_object(box_path, SCREEN_WIDTH, SCREEN_HEIGHT // 2)


def add_player_speak_sprite():
    """Загрузка диалоговой плашки"""
    player_path = '../assets/dialogue/student.png' # TODO: rename (or not)
    return load_one_object(player_path, 300, 400)


def add_character_speak_sprite():
    """Загрузка диалоговой плашки"""
    char_path = '../assets/dialogue/monster.png' # TODO: make the function scan the folder with characters (like in wall loading)
    return load_one_object(char_path, 300, 400)


def add_choice_buttons():
    """Загрузка всех вариантов кнопки"""
    buttons_path = '../assets/dialogue/buttons'
    button_files = {
        ButtonType.REGULAR: 'choice_button.png',
        ButtonType.HOVERED: 'choice_button_hovered.png',
        ButtonType.PRESSED: 'choice_button_pressed.png'
    }
    button_sizes = {
        ButtonType.REGULAR: (CHOICE_BUTTON_SIZE, CHOICE_BUTTON_SIZE),
        ButtonType.HOVERED: (CHOICE_BUTTON_SIZE, CHOICE_BUTTON_SIZE),
        ButtonType.PRESSED: (CHOICE_BUTTON_SIZE, CHOICE_BUTTON_SIZE)
    }
    return load_all_objects(buttons_path, button_files, button_sizes)


class Transformer:
    """
    Умеет кешировать отражённые и повёрнутые спрайты. Не требует больше одной инстанции
    """
    flipped_cache = {}
    rotated_cache = {}

    def get_flipped(self, sprite, flip_x=False, flip_y=False):
        """Получение отражённого спрайта"""
        cache_key = (sprite, flip_x, flip_y)

        if cache_key not in self.flipped_cache:
            if flip_x or flip_y:
                flipped = pygame.transform.flip(sprite, flip_x, flip_y)
                self.flipped_cache[cache_key] = flipped
            else:
                self.flipped_cache[cache_key] = sprite

        return self.flipped_cache[cache_key]

    def get_rotated(self, sprite, rotation=0):
        """Получение повёрнутого спрайта"""
        cache_key = (sprite, rotation)

        if cache_key not in self.rotated_cache:
            if rotation != 0:
                rotated = pygame.transform.rotate(sprite, -rotation)
                self.rotated_cache[cache_key] = rotated
            else:
                self.rotated_cache[cache_key] = sprite

        return self.rotated_cache[cache_key]
