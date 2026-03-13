import os
import pygame

from src.Util import * # screw it - Vsevolod


def load_one_object(path: str, width: float = None, height: float = None):
    loaded_object = None
    try:
        loaded_object = pygame.image.load(path)
        if width and height:
            loaded_object = pygame.transform.scale(loaded_object, (width, height))
        print(f"Загружен {path}")
    except Exception as e:
        print(f"Ошибка загрузки {path}: {e}")
    return loaded_object


def load_all_objects(root_path: str,
                     path_map: dict[Enum, str],
                     widths_heights_map: dict[Enum, tuple[float, float]] = None):
    loaded_objects = {}
    for obj_type, filename in path_map.items():
        filepath = os.path.join(root_path, filename)
        if os.path.exists(filepath):
            width, height = widths_heights_map[obj_type] if widths_heights_map else (None, None)
            image = load_one_object(filepath, width, height)
            loaded_objects[obj_type] = image
    return loaded_objects


"""
Для MazeState
"""


ROOT_MAZE_PATH = '..\\assets\\images\\maze_tiles'


def add_entrance_exit_tiles(level=1):
    """Загрузка изображений входа и выхода"""

    entrance_path = f'{ROOT_MAZE_PATH}\\level_{level}\\entrance.png'
    exit_path = f'{ROOT_MAZE_PATH}\\level_{level}\\exit.png'

    entrance_tile = load_one_object(entrance_path, TILE_SIZE, TILE_SIZE)
    exit_tile = load_one_object(exit_path, TILE_SIZE, TILE_SIZE)

    return entrance_tile, exit_tile


def add_player_tile():
    """Загрузка тайла игрока"""
    player_path = f'{ROOT_MAZE_PATH}\\player\\player.png'
    return load_one_object(player_path, PLAYER_SIZE, PLAYER_SIZE)


def add_player_walk():
    """Загрузка тайлов анимации игрока"""
    frames = []
    for i in range(1,5):
        frame_path = f'{ROOT_MAZE_PATH}\\player\\walk{i}.png'
        frame = load_one_object(frame_path, PLAYER_SIZE, PLAYER_SIZE)
        if frame:
            frames.append(frame)
    return frames


def add_floor_tile(level=1):
    """Загрузка тайла пола"""
    floor_path = f'{ROOT_MAZE_PATH}\\level_{level}\\floor.png'
    return load_one_object(floor_path, TILE_SIZE, TILE_SIZE)


def add_wall_tiles(level=1):
    """Загрузка тайлов стен"""
    tiles_path = f'{ROOT_MAZE_PATH}\\level_{level}\\walls'
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


def add_enemy_tile(level=1):
    """Загрузка спрайта врага по уровню"""
    enemy_path = f'{ROOT_MAZE_PATH}\\level_{level}\\enemy.png'
    return load_one_object(enemy_path, TILE_SIZE, TILE_SIZE)


"""
Для DialogueState
"""


ROOT_DIALOGUE_PATH = '..\\assets\\images\\dialogue'


def add_dialogue_bg(rel_path: str | None = None):
    """Загрузка фона диалога"""
    if rel_path:
        bg_path = f'{ROOT_DIALOGUE_PATH}\\backgrounds\\{rel_path}'
    else:
        bg_path = f'{ROOT_DIALOGUE_PATH}\\backgrounds\\bg.png'
    return load_one_object(bg_path, SCREEN_WIDTH, SCREEN_HEIGHT)


def add_dialogue_box():
    """Загрузка диалоговой плашки"""
    box_path = f'{ROOT_DIALOGUE_PATH}\\box.png'
    return load_one_object(box_path, SCREEN_WIDTH, SCREEN_HEIGHT // 2)


def add_left_speak_sprite(rel_path: str | None = None):
    """Загрузка главного героя"""
    if rel_path:
        player_path = f'{ROOT_DIALOGUE_PATH}\\protagonists\\{rel_path}'
    else:
        player_path = f'{ROOT_DIALOGUE_PATH}\\protagonists\\student.png'
    return load_one_object(player_path, 300, 300)


def add_right_speak_sprite(rel_path: str | None = None):
    """Загрузка собеседника"""
    if rel_path:
        char_path = f'{ROOT_DIALOGUE_PATH}\\{rel_path}'
        # doesn't start from monsters to be able to load students as right speakers - Vsevolod
    else:
        char_path = f'{ROOT_DIALOGUE_PATH}\\monsters\\level_0\\monster.png'
    return load_one_object(char_path, 300, 300)


def add_dialogue_choice_buttons():
    """Загрузка всех вариантов кнопки"""
    buttons_path = f'{ROOT_DIALOGUE_PATH}\\choice_button'
    button_files = {
        ButtonState.REGULAR: 'choice_button.png',
        ButtonState.HOVERED: 'choice_button_hovered.png',
        ButtonState.PRESSED: 'choice_button_pressed.png'
    }
    button_sizes = {
        ButtonState.REGULAR: (CHOICE_BUTTON_SIZE, CHOICE_BUTTON_SIZE),
        ButtonState.HOVERED: (CHOICE_BUTTON_SIZE, CHOICE_BUTTON_SIZE),
        ButtonState.PRESSED: (CHOICE_BUTTON_SIZE, CHOICE_BUTTON_SIZE)
    }
    return load_all_objects(buttons_path, button_files, button_sizes)


"""
Для ChallengeState
"""


ROOT_CHALLENGE_PATH = '..\\assets\\images\\challenge'
QUESTION_CARD_WIDTH = SCREEN_WIDTH - 200
QUESTION_CARD_HEIGHT = SCREEN_HEIGHT - 100
STAMP_WIDTH = 150
STAMP_HEIGHT = 90
TIP_CARD_WIDTH = SCREEN_WIDTH - 700
TIP_CARD_HEIGHT = SCREEN_HEIGHT - 500


def add_challenge_bg():
    """Загрузка фона испытания"""
    bg_path = f'{ROOT_CHALLENGE_PATH}\\bg.png'
    return load_one_object(bg_path, SCREEN_WIDTH, SCREEN_HEIGHT)


def add_question_card():
    """Загрузка карточки задания"""
    card_path = f'{ROOT_CHALLENGE_PATH}\\card.png'
    return load_one_object(card_path, QUESTION_CARD_WIDTH, QUESTION_CARD_HEIGHT)


def add_window_image(rel_path: str):
    """Загрузка изображения, которое требует файл испытания"""
    image_path = f'{ROOT_CHALLENGE_PATH}\\{rel_path}'
    return load_one_object(image_path)


def add_challenge_choice_buttons():
    """Загрузка всех вариантов кнопки выбора"""
    buttons_path = f'{ROOT_CHALLENGE_PATH}\\choice_button'
    button_files = {
        ButtonState.REGULAR: 'choice_button.png',
        ButtonState.HOVERED: 'choice_button_hovered.png',
        ButtonState.PRESSED: 'choice_button_pressed.png'
    }
    button_sizes = {
        ButtonState.REGULAR: (CHOICE_BUTTON_SIZE, CHOICE_BUTTON_SIZE),
        ButtonState.HOVERED: (CHOICE_BUTTON_SIZE, CHOICE_BUTTON_SIZE),
        ButtonState.PRESSED: (CHOICE_BUTTON_SIZE, CHOICE_BUTTON_SIZE)
    }
    return load_all_objects(buttons_path, button_files, button_sizes)


def add_back_buttons():
    """Загрузка всех вариантов кнопки возврата"""
    buttons_path = f'{ROOT_CHALLENGE_PATH}\\back_button'
    button_files = {
        ButtonState.REGULAR: 'back_button.png',
        ButtonState.HOVERED: 'back_button_hovered.png',
        ButtonState.PRESSED: 'back_button_pressed.png'
    }
    button_sizes = {
        ButtonState.REGULAR: (CHAL_BUTTON_WIDTH, CHAL_BUTTON_HEIGHT),
        ButtonState.HOVERED: (CHAL_BUTTON_WIDTH, CHAL_BUTTON_HEIGHT),
        ButtonState.PRESSED: (CHAL_BUTTON_WIDTH, CHAL_BUTTON_HEIGHT)
    }
    return load_all_objects(buttons_path, button_files, button_sizes)


def add_forth_buttons():
    """Загрузка всех вариантов кнопки продолжения"""
    buttons_path = f'{ROOT_CHALLENGE_PATH}\\forth_button'
    button_files = {
        ButtonState.REGULAR: 'forth_button.png',
        ButtonState.HOVERED: 'forth_button_hovered.png',
        ButtonState.PRESSED: 'forth_button_pressed.png'
    }
    button_sizes = {
        ButtonState.REGULAR: (CHAL_BUTTON_WIDTH, CHAL_BUTTON_HEIGHT),
        ButtonState.HOVERED: (CHAL_BUTTON_WIDTH, CHAL_BUTTON_HEIGHT),
        ButtonState.PRESSED: (CHAL_BUTTON_WIDTH, CHAL_BUTTON_HEIGHT)
    }
    return load_all_objects(buttons_path, button_files, button_sizes)


def add_submit_buttons():
    """Загрузка всех вариантов кнопки сдачи ответов"""
    buttons_path = f'{ROOT_CHALLENGE_PATH}\\submit_button'
    button_files = {
        ButtonState.REGULAR: 'submit_button.png',
        ButtonState.HOVERED: 'submit_button_hovered.png',
        ButtonState.PRESSED: 'submit_button_pressed.png'
    }
    button_sizes = {
        ButtonState.REGULAR: (CHAL_BUTTON_WIDTH, CHAL_BUTTON_HEIGHT),
        ButtonState.HOVERED: (CHAL_BUTTON_WIDTH, CHAL_BUTTON_HEIGHT),
        ButtonState.PRESSED: (CHAL_BUTTON_WIDTH, CHAL_BUTTON_HEIGHT)
    }
    return load_all_objects(buttons_path, button_files, button_sizes)


def add_judgement_stamps():
    """Загрузка штампов "Верно" и "Неверно" """

    correct_path = f'{ROOT_CHALLENGE_PATH}\\correct.png'
    incorrect_path = f'{ROOT_CHALLENGE_PATH}\\incorrect.png'

    correct_stamp = load_one_object(correct_path, STAMP_WIDTH, STAMP_HEIGHT)
    incorrect_stamp = load_one_object(incorrect_path, STAMP_WIDTH, STAMP_HEIGHT)

    return correct_stamp, incorrect_stamp


def add_tip_card():
    """Загрузка карточки комментария"""
    card_path = f'{ROOT_CHALLENGE_PATH}\\tip_card.png'
    return load_one_object(card_path, TIP_CARD_WIDTH, TIP_CARD_HEIGHT)


def add_transitions():
    """Загрузка заставок начала, ответов и итога"""
    start_path = f'{ROOT_CHALLENGE_PATH}\\transitions\\start.png'
    check_path = f'{ROOT_CHALLENGE_PATH}\\transitions\\check.png'
    end_path = f'{ROOT_CHALLENGE_PATH}\\transitions\\end.png'

    start_cover = load_one_object(start_path, SCREEN_WIDTH, SCREEN_HEIGHT)
    check_cover = load_one_object(check_path, SCREEN_WIDTH, SCREEN_HEIGHT)
    end_cover = load_one_object(end_path, SCREEN_WIDTH, SCREEN_HEIGHT)

    return start_cover, check_cover, end_cover


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
