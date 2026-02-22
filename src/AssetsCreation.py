import os
import pygame

from src.Util import WallPattern, SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE


"""
Для MazeState
"""


def load_entrance_exit_tiles():
    """Загрузка кастомных изображений для входа и выхода"""

    # Загрузка изображения входа
    entrance_path = '../assets/tiles/entrance.png'
    entrance_tile = None
    try:
        entrance_tile = pygame.image.load(entrance_path)
        entrance_tile = pygame.transform.scale(entrance_tile, (TILE_SIZE, TILE_SIZE))
        print("Загружен entrance.png")
    except Exception as e:
        print(f"Ошибка загрузки entrance.png: {e}")

    # Загрузка изображения выхода
    exit_path = '../assets/tiles/exit.png'
    exit_tile = None
    try:
        exit_tile = pygame.image.load(exit_path)
        exit_tile = pygame.transform.scale(exit_tile, (TILE_SIZE, TILE_SIZE))
        print("Загружен exit.png")
    except Exception as e:
        print(f"Ошибка загрузки exit.png: {e}")
        # TODO: maybe remove try-except and let players use their brain

    return entrance_tile, exit_tile


def load_player_tile():
    """Загрузка тайла игрока"""
    player_path = '../assets/tiles/player.png'
    player_tile = None
    try:
        player_tile = pygame.image.load(player_path)
        player_tile = pygame.transform.scale(player_tile, (TILE_SIZE, TILE_SIZE))
        print("Загружен player.png")
    except Exception as e:
        print(f"Ошибка загрузки player.png: {e}")
    return player_tile


def load_floor_tile():
    """Загрузка тайла пола"""
    floor_path = '../assets/tiles/floor.png'
    floor_tile = None
    try:
        floor_tile = pygame.image.load(floor_path)
        floor_tile = pygame.transform.scale(floor_tile, (TILE_SIZE, TILE_SIZE))
        print("Загружен floor.png")
    except Exception as e:
        print(f"Ошибка загрузки floor.png: {e}")
    return floor_tile


def load_wall_tiles():
    """Загрузка тайлов стен"""
    tiles_path = '../assets/tiles/walls'
    wall_tiles = {}

    tile_files = {
        WallPattern.SINGLE: 'wall_single.png',
        WallPattern.STRAIGHT: 'wall_straight.png',
        WallPattern.STRAIGHT_SOUTH: 'wall_straight_south.png',
        WallPattern.CORNER: 'wall_corner.png',
        WallPattern.CORNER_SOUTH: 'wall_corner_south.png'
    }

    for pattern, filename in tile_files.items():
        filepath = os.path.join(tiles_path, filename)

        if os.path.exists(filepath):
            try:
                image = pygame.image.load(filepath)
                image = pygame.transform.scale(image, (TILE_SIZE, TILE_SIZE))
                wall_tiles[pattern] = image
                print(f"Загружен {filename}")
            except Exception as e:
                print(f"Ошибка загрузки {filename}: {e}")

    return wall_tiles


"""
Для DialogueState
"""


def load_dialogue_bg():
    """Загрузка фона диалога"""
    bg_path = '../assets/dialogue/bg.png'
    dialogue_bg = None
    try:
        dialogue_bg = pygame.image.load(bg_path)
        dialogue_bg = pygame.transform.scale(dialogue_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
        print("Загружен bg.png")
    except Exception as e:
        print(f"Ошибка загрузки bg.png: {e}")
    return dialogue_bg


def load_dialogue_box():
    """Загрузка диалоговой плашки"""
    box_path = '../assets/dialogue/box.png'
    dialogue_box = None
    try:
        dialogue_box = pygame.image.load(box_path)
        dialogue_box = pygame.transform.scale(dialogue_box, (SCREEN_WIDTH, SCREEN_HEIGHT // 2))
        print("Загружен box.png")
    except Exception as e:
        print(f"Ошибка загрузки box.png: {e}")
    return dialogue_box


def load_player_speak_sprite():
    """Загрузка диалоговой плашки"""
    player_path = '../assets/dialogue/student.png' # TODO: rename (or not)
    player_speaks = None
    try:
        player_speaks = pygame.image.load(player_path)
        player_speaks = pygame.transform.scale(player_speaks, (300, 400))
        print("Загружен student.png")
    except Exception as e:
        print(f"Ошибка загрузки student.png: {e}")
    return player_speaks


def load_character_speak_sprite():
    """Загрузка диалоговой плашки"""
    char_path = '../assets/dialogue/monster.png' # TODO: make the function scan the folder with characters (like in wall loading)
    char_speaks = None
    try:
        char_speaks = pygame.image.load(char_path)
        char_speaks = pygame.transform.scale(char_speaks, (300, 400))
        print("Загружен monster.png")
    except Exception as e:
        print(f"Ошибка загрузки monster.png: {e}")
    return char_speaks


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
