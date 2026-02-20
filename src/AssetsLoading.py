import os
import pygame

from src.Util import WallPattern


# Константы
TILE_SIZE = 25 # чем меньше, тем мельче клетки, и тем больше их может уместиться на экране


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
        WallPattern.STRAIGHT_VERTICAL: 'wall_straight_vertical.png',
        WallPattern.STRAIGHT_HORIZONTAL: 'wall_straight_horizontal.png',
        WallPattern.CORNER_BOTTOM: 'wall_corner_bottom.png',  # Базовый: пол снизу и справа
        WallPattern.CORNER_TOP: 'wall_corner_top.png',  # Базовый: пол сверху и справа
        WallPattern.T_SHAPE_NORTH: 'wall_t_up.png',
        WallPattern.T_SHAPE_SOUTH: 'wall_t_down.png',
        WallPattern.T_SHAPE_SIDE: 'wall_t_side.png',
        WallPattern.CROSS: 'wall_cross.png',
        WallPattern.DEAD_END_NORTH: 'wall_dead_end_up.png',
        WallPattern.DEAD_END_OTHER: 'wall_dead_end_other.png',
        WallPattern.SINGLE: 'wall_single.png'
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
