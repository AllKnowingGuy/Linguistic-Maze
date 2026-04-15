import pygame

from src.util import *  # screw it - Vsevolod


def load_one_graphic_object(
    path: Path, width: float = None, height: float = None
) -> pygame.Surface:
    """Загрузка одного графического спрайта

    Args:
        path (str): путь к файлу, начиная с папки проекта
        width (float): ширина спрайта, если требуется изменение размера
        height (float): высота спрайта, если требуется изменение размера

    Returns:
        Surface: поверхность Pygame с загруженным изображением
    """

    loaded_object = None
    try:
        loaded_object = pygame.image.load(resource_path(path))
        if width and height:
            loaded_object = pygame.transform.scale(loaded_object, (width, height))
    except Exception as e:
        print(f"Ошибка загрузки {path}: {e}")
    return loaded_object


def load_all_graphic_objects(
    root_path: Path,
    path_map: dict[Enum, Path],
    widths_heights_map: dict[Enum, tuple[float, float]] = None,
) -> dict[Enum, pygame.Surface]:
    """Загрузка нескольких графических спрайтов, обычно однотипных

    Обратите внимание: ``path_map`` и ``width_heights_map`` должны использовать один и тот же Enum!

    Args:
        root_path (str): путь к папке, в которой лежат файлы, начиная с папки проекта
        path_map (dict[Enum, str]): словарь пар Enum-путь к файлам, которые требуется загрузить
        widths_heights_map (dict[Enum, tuple[float, float]]): словарь пар Enum-пара чисел к файлам,
         которые требуется загрузить

    Returns:
        dict[Enum, Surface]: словарь Enum-Surface - по одной поверхности с изображением на элемент Enum
    """

    loaded_objects: dict[Enum, pygame.Surface] = {}
    for obj_type, filename in path_map.items():
        filepath = Path(root_path / filename)
        if resource_path(filepath).exists():
            width, height = (
                widths_heights_map[obj_type] if widths_heights_map else (None, None)
            )
            image = load_one_graphic_object(filepath, width, height)
            loaded_objects[obj_type] = image
    return loaded_objects


def load_font(path: Path, size: int = 24) -> pygame.font.Font | None:
    try:
        font = pygame.font.Font(resource_path(path), size)
        return font
    except (pygame.error, AttributeError):
        return None


def load_one_sound_object(path: Path) -> pygame.mixer.Sound | None:
    try:
        sound = pygame.mixer.Sound(resource_path(path))
        return sound
    except (pygame.error, AttributeError):
        return None


def set_music(path: Path):
    try:
        pygame.mixer.music.load(resource_path(path))
    except (pygame.error, AttributeError):
        pass


ROOT_MUSIC_PATH = "assets\\music"
"""Главная папка музыки и звуков"""

"""
Для главного меню
"""

ROOT_MENU_PATH = "assets\\images\\menu"
"""Главная папка изображений меню"""


def add_menu_bg() -> pygame.Surface:
    """Загрузка фона меню

    Returns:
        Surface: фон меню
    """

    bg_path = Path(f"{ROOT_MENU_PATH}\\bg.png")
    return load_one_graphic_object(bg_path, SCREEN_WIDTH, SCREEN_HEIGHT)


def add_menu_loss_bg() -> pygame.Surface:
    """Загрузка фона экрана проигрыша

    Returns:
        Surface: фон экрана проигрыша
    """

    bg_path = Path(f"{ROOT_MENU_PATH}\\lossbg.png")
    return load_one_graphic_object(bg_path, SCREEN_WIDTH, SCREEN_HEIGHT)


def add_menu_win_bg() -> pygame.Surface:
    """Загрузка фона экрана победы

    Returns:
        Surface: фон экрана победы
    """

    bg_path = Path(f"{ROOT_MENU_PATH}\\winbg.png")
    return load_one_graphic_object(bg_path, SCREEN_WIDTH, SCREEN_HEIGHT)


def add_start_buttons() -> dict[Enum, pygame.Surface]:
    """Загрузка всех вариантов кнопки старта игры

    Returns:
        dict[Enum, Surface]: изображения стартовой кнопки по состояниям
    """

    buttons_path = Path(f"{ROOT_MENU_PATH}\\start_button")
    button_files = {
        ButtonState.REGULAR: Path("start_button.png"),
        ButtonState.HOVERED: Path("start_button_hovered.png"),
        ButtonState.PRESSED: Path("start_button_pressed.png"),
    }
    button_sizes = {
        ButtonState.REGULAR: (START_BUTTON_WIDTH, START_BUTTON_HEIGHT),
        ButtonState.HOVERED: (START_BUTTON_WIDTH, START_BUTTON_HEIGHT),
        ButtonState.PRESSED: (START_BUTTON_WIDTH, START_BUTTON_HEIGHT),
    }
    return load_all_graphic_objects(buttons_path, button_files, button_sizes)


def add_setting_sections_buttons() -> (
    tuple[dict[Enum, pygame.Surface], dict[Enum, pygame.Surface]]
):
    """Загрузка всех вариантов двух кнопок меню настроек

    Returns:
        tuple[dict[Enum, Surface], dict[Enum, Surface]]: изображения кнопок по состояниям
    """

    button_sizes = {
        ButtonState.REGULAR: (BIND_BUTTON_WIDTH, BIND_BUTTON_HEIGHT),
        ButtonState.HOVERED: (BIND_BUTTON_WIDTH, BIND_BUTTON_HEIGHT),
        ButtonState.PRESSED: (BIND_BUTTON_WIDTH, BIND_BUTTON_HEIGHT),
    }

    buttons_path_left = Path(f"{ROOT_MENU_PATH}\\left_settings_button")
    buttons_path_right = Path(f"{ROOT_MENU_PATH}\\right_settings_button")
    button_files_left = {
        ButtonState.REGULAR: Path("left_settings_button.png"),
        ButtonState.HOVERED: Path("left_settings_button_hovered.png"),
        ButtonState.PRESSED: Path("left_settings_button_pressed.png"),
    }
    button_files_right = {
        ButtonState.REGULAR: Path("right_settings_button.png"),
        ButtonState.HOVERED: Path("right_settings_button_hovered.png"),
        ButtonState.PRESSED: Path("right_settings_button_pressed.png"),
    }

    return (
        load_all_graphic_objects(buttons_path_left, button_files_left, button_sizes),
        load_all_graphic_objects(buttons_path_right, button_files_right, button_sizes),
    )


def add_bind_buttons(name: str) -> dict[Enum, pygame.Surface]:
    """Загрузка всех вариантов одной из кнопок настройки управления

    Args:
        name (str): название настройки управления

    Returns:
        dict[Enum, Surface]: изображения кнопки по состояниям
    """

    buttons_path = Path(f"{ROOT_MENU_PATH}\\keybind_buttons\\{name}_button")
    button_files = {
        ButtonState.REGULAR: Path(f"{name}_button.png"),
        ButtonState.HOVERED: Path(f"{name}_button_hovered.png"),
        ButtonState.PRESSED: Path(f"{name}_button_pressed.png"),
    }
    button_sizes = {
        ButtonState.REGULAR: (BIND_BUTTON_WIDTH, BIND_BUTTON_HEIGHT),
        ButtonState.HOVERED: (BIND_BUTTON_WIDTH, BIND_BUTTON_HEIGHT),
        ButtonState.PRESSED: (BIND_BUTTON_WIDTH, BIND_BUTTON_HEIGHT),
    }
    return load_all_graphic_objects(buttons_path, button_files, button_sizes)


def set_menu_music():
    """Установка музыки главного меню"""

    set_music(Path(f"{ROOT_MUSIC_PATH}\\Menu.wav"))


def set_gameover_music():
    """Установка музыки проигрыша"""

    set_music(Path(f"{ROOT_MUSIC_PATH}\\Gameover.wav"))


def add_enter_maze_sound():
    return load_one_sound_object(Path(f"{ROOT_MUSIC_PATH}\\Start Game.wav"))


def add_victory_sound():
    return load_one_sound_object(Path(f"{ROOT_MUSIC_PATH}\\Victory.wav"))


def add_maze_enter_sound():
    return load_one_sound_object(Path(f"{ROOT_MUSIC_PATH}\\Start Game.wav"))


"""
Для MazeState
"""

ROOT_MAZE_PATH = "assets\\images\\maze_tiles"
"""Главная папка изображений лабиринта"""


def add_entrance_exit_tiles(level: int = 0) -> tuple[pygame.Surface, pygame.Surface]:
    """Загрузка изображений входа и выхода

    Args:
        level (int): уровень, для которого выбирается тематика

    Returns:
        tuple[Surface, Surface]: изображения дверей входа и выхода соответственно
    """

    entrance_path = Path(f"{ROOT_MAZE_PATH}\\level_{level}\\entrance.png")
    exit_path = Path(f"{ROOT_MAZE_PATH}\\level_{level}\\exit.png")

    entrance_tile = load_one_graphic_object(entrance_path, TILE_SIZE, TILE_SIZE)
    exit_tile = load_one_graphic_object(exit_path, TILE_SIZE, TILE_SIZE)

    return entrance_tile, exit_tile


def add_player_tile(player_name: str = "student") -> pygame.Surface:
    """Загрузка тайла игрока с учетом выбранного имени

    Returns:
        Surface: изображение стоящего игрока
    """

    player_path = Path(f"{ROOT_MAZE_PATH}\\player\\{player_name}\\player.png")
    return load_one_graphic_object(player_path, PLAYER_SIZE, PLAYER_SIZE)


def add_player_walk(player_name: str = "student") -> list[pygame.Surface]:
    """Загрузка тайлов анимации игрока с учетом выбранного имени

    Returns:
        list[Surface]: изображения идущего игрока
    """

    frames = []
    for i in range(1, 5):
        frame_path = Path(f"{ROOT_MAZE_PATH}\\player\\{player_name}\\walk{i}.png")
        frame = load_one_graphic_object(frame_path, PLAYER_SIZE, PLAYER_SIZE)
        if frame:
            frames.append(frame)
    return frames


def add_floor_tile(level: int = 0) -> pygame.Surface:
    """Загрузка тайла пола

    Args:
        level (int): уровень, для которого выбирается тематика

    Returns:
        Surface: изображение пола лабиринта
    """

    floor_path = Path(f"{ROOT_MAZE_PATH}\\level_{level}\\floor.png")
    return load_one_graphic_object(floor_path, TILE_SIZE, TILE_SIZE)


def add_wall_tiles(level: int = 0) -> dict[Enum, pygame.Surface]:
    """Загрузка тайлов стен

    Args:
        level (int): уровень, для которого выбирается тематика

    Returns:
        dict[Enum, Surface]: изображения стен по типам (база и границы)
    """

    tiles_path = Path(f"{ROOT_MAZE_PATH}\\level_{level}\\walls")
    tile_files = {
        WallPattern.SINGLE: Path("wall_single.png"),
        WallPattern.STRAIGHT: Path("wall_straight.png"),
        WallPattern.STRAIGHT_SOUTH: Path("wall_straight_south.png"),
        WallPattern.CORNER: Path("wall_corner.png"),
        WallPattern.CORNER_SOUTH: Path("wall_corner_south.png"),
    }
    tile_sizes = {
        WallPattern.SINGLE: (TILE_SIZE, TILE_SIZE),
        WallPattern.STRAIGHT: (TILE_SIZE, TILE_SIZE),
        WallPattern.STRAIGHT_SOUTH: (TILE_SIZE, TILE_SIZE),
        WallPattern.CORNER: (TILE_SIZE, TILE_SIZE),
        WallPattern.CORNER_SOUTH: (TILE_SIZE, TILE_SIZE),
    }
    return load_all_graphic_objects(tiles_path, tile_files, tile_sizes)


def add_enemy_tile(level: int = 0, enemy_name: str = None) -> pygame.Surface:
    """Загрузка спрайта врага по уровню

    Args:
        level (int): уровень, для которого выбирается тематика
        enemy_name (str | None): имя монстра (если нужен конкретный)

    Returns:
        Surface: изображение врага
    """

    if enemy_name:
        enemy_path = Path(
            f"{ROOT_MAZE_PATH}\\level_{level}\\monsters\\{enemy_name}.png"
        )
        # load_one_object will take care of whether the path exists or not - Vsevolod
    else:
        enemy_path = Path(f"{ROOT_MAZE_PATH}\\level_{level}\\enemy.png")
    return load_one_graphic_object(enemy_path, TILE_SIZE, TILE_SIZE)


def set_maze_music():
    """Установка музыки лабиринта"""

    set_music(Path(f"{ROOT_MUSIC_PATH}\\Maze.wav"))


"""
Для DialogueState
"""

ROOT_DIALOGUE_PATH = "assets\\images\\dialogue"
"""Главная папка изображений диалогов"""


def add_dialogue_bg(rel_path: str | None = None) -> pygame.Surface:
    """Загрузка фона диалога

    Args:
        rel_path (str | None): опциональный относительный путь к изображению фона

    Returns:
        Surface: фон диалога
    """

    if rel_path:
        bg_path = Path(f"{ROOT_DIALOGUE_PATH}\\backgrounds\\{rel_path}")
    else:
        bg_path = Path(f"{ROOT_DIALOGUE_PATH}\\backgrounds\\bg.png")
    return load_one_graphic_object(bg_path, SCREEN_WIDTH, SCREEN_HEIGHT)


def add_dialogue_box(alt_version: bool = False) -> pygame.Surface:
    """Загрузка диалоговой плашки

    Args:
        alt_version (bool): нужно ли загрузить альтернативную полупрозрачную плашку

    Returns:
        Surface: диалоговая плашка
    """

    box_path = Path(
        f"{ROOT_DIALOGUE_PATH}\\box.png"
        if not alt_version
        else f"{ROOT_DIALOGUE_PATH}\\box_story.png"
    )
    return load_one_graphic_object(box_path, SCREEN_WIDTH, SCREEN_HEIGHT // 2)


def add_left_speak_sprite(rel_path: str | None = None) -> pygame.Surface:
    """Загрузка персонажа слева

    Args:
        rel_path (str | None): опциональный относительный путь к изображению персонажа

    Returns:
        Surface: портрет персонажа слева
    """

    if rel_path:
        player_path = Path(f"{ROOT_DIALOGUE_PATH}\\protagonists\\{rel_path}")
    else:
        player_path = Path(f"{ROOT_DIALOGUE_PATH}\\protagonists\\student.png")
    return load_one_graphic_object(player_path, 270, 360)


def add_right_speak_sprite(rel_path: str | None = None) -> pygame.Surface:
    """Загрузка персонажа справа

    Args:
        rel_path (str | None): опциональный относительный путь к изображению персонажа

    Returns:
        Surface: портрет персонажа справа
    """

    if rel_path:
        char_path = Path(f"{ROOT_DIALOGUE_PATH}\\{rel_path}")
        # doesn't start from monsters to be able to load students as right speakers - Vsevolod
    else:
        char_path = f"{ROOT_DIALOGUE_PATH}\\monsters\\monster.png"
    return load_one_graphic_object(char_path, 270, 360)


def add_dialogue_choice_buttons() -> dict[Enum, pygame.Surface]:
    """Загрузка всех вариантов кнопки выбора

    Returns:
        dict[Enum, Surface]: изображения кнопки по состояниям
    """

    buttons_path = Path(f"{ROOT_DIALOGUE_PATH}\\choice_button")
    button_files = {
        ButtonState.REGULAR: Path("choice_button.png"),
        ButtonState.HOVERED: Path("choice_button_hovered.png"),
        ButtonState.PRESSED: Path("choice_button_pressed.png"),
    }
    button_sizes = {
        ButtonState.REGULAR: (CHOICE_BUTTON_SIZE, CHOICE_BUTTON_SIZE),
        ButtonState.HOVERED: (CHOICE_BUTTON_SIZE, CHOICE_BUTTON_SIZE),
        ButtonState.PRESSED: (CHOICE_BUTTON_SIZE, CHOICE_BUTTON_SIZE),
    }
    return load_all_graphic_objects(buttons_path, button_files, button_sizes)


def set_dialogue_music(rel_path: str | None = None):
    """Установка музыки диалога"""

    if rel_path:
        set_music(Path(f"{ROOT_MUSIC_PATH}\\{rel_path}"))
    else:
        set_music(Path(f"{ROOT_MUSIC_PATH}\\Intro.wav"))


def add_dialogue_sound(rel_path: str | None = None):
    if not rel_path:
        return None
    return load_one_sound_object(Path(f"{ROOT_MUSIC_PATH}\\{rel_path}"))


"""
Для ChallengeState
"""

ROOT_CHALLENGE_PATH = "assets\\images\\challenge"
QUESTION_CARD_WIDTH = SCREEN_WIDTH - 210
QUESTION_CARD_HEIGHT = SCREEN_HEIGHT - 50
STAMP_WIDTH = 150
STAMP_HEIGHT = 90
TIP_CARD_WIDTH = SCREEN_WIDTH - 600
TIP_CARD_HEIGHT = SCREEN_HEIGHT - 500


def add_challenge_bg():
    """Загрузка фона испытания"""
    bg_path = Path(f"{ROOT_CHALLENGE_PATH}\\bg.png")
    return load_one_graphic_object(bg_path, SCREEN_WIDTH, SCREEN_HEIGHT)


def add_question_card():
    """Загрузка карточки задания"""
    card_path = Path(f"{ROOT_CHALLENGE_PATH}\\card.png")
    return load_one_graphic_object(card_path, QUESTION_CARD_WIDTH, QUESTION_CARD_HEIGHT)


def add_window_image(rel_path: str):
    """Загрузка изображения, которое требует файл испытания"""
    image_path = Path(f"{ROOT_CHALLENGE_PATH}\\{rel_path}")
    return load_one_graphic_object(image_path)


def add_challenge_choice_buttons():
    """Загрузка всех вариантов кнопки выбора"""
    buttons_path = Path(f"{ROOT_CHALLENGE_PATH}\\choice_button")
    button_files = {
        ButtonState.REGULAR: Path("choice_button.png"),
        ButtonState.HOVERED: Path("choice_button_hovered.png"),
        ButtonState.PRESSED: Path("choice_button_pressed.png"),
    }
    button_sizes = {
        ButtonState.REGULAR: (CHOICE_BUTTON_SIZE, CHOICE_BUTTON_SIZE),
        ButtonState.HOVERED: (CHOICE_BUTTON_SIZE, CHOICE_BUTTON_SIZE),
        ButtonState.PRESSED: (CHOICE_BUTTON_SIZE, CHOICE_BUTTON_SIZE),
    }
    return load_all_graphic_objects(buttons_path, button_files, button_sizes)


def add_back_buttons():
    """Загрузка всех вариантов кнопки возврата"""
    buttons_path = Path(f"{ROOT_CHALLENGE_PATH}\\back_button")
    button_files = {
        ButtonState.REGULAR: Path("back_button.png"),
        ButtonState.HOVERED: Path("back_button_hovered.png"),
        ButtonState.PRESSED: Path("back_button_pressed.png"),
    }
    button_sizes = {
        ButtonState.REGULAR: (CHAL_BUTTON_WIDTH, CHAL_BUTTON_HEIGHT),
        ButtonState.HOVERED: (CHAL_BUTTON_WIDTH, CHAL_BUTTON_HEIGHT),
        ButtonState.PRESSED: (CHAL_BUTTON_WIDTH, CHAL_BUTTON_HEIGHT),
    }
    return load_all_graphic_objects(buttons_path, button_files, button_sizes)


def add_forth_buttons():
    """Загрузка всех вариантов кнопки продолжения"""
    buttons_path = Path(f"{ROOT_CHALLENGE_PATH}\\forth_button")
    button_files = {
        ButtonState.REGULAR: Path("forth_button.png"),
        ButtonState.HOVERED: Path("forth_button_hovered.png"),
        ButtonState.PRESSED: Path("forth_button_pressed.png"),
    }
    button_sizes = {
        ButtonState.REGULAR: (CHAL_BUTTON_WIDTH, CHAL_BUTTON_HEIGHT),
        ButtonState.HOVERED: (CHAL_BUTTON_WIDTH, CHAL_BUTTON_HEIGHT),
        ButtonState.PRESSED: (CHAL_BUTTON_WIDTH, CHAL_BUTTON_HEIGHT),
    }
    return load_all_graphic_objects(buttons_path, button_files, button_sizes)


def add_submit_buttons():
    """Загрузка всех вариантов кнопки сдачи ответов"""
    buttons_path = Path(f"{ROOT_CHALLENGE_PATH}\\submit_button")
    button_files = {
        ButtonState.REGULAR: Path("submit_button.png"),
        ButtonState.HOVERED: Path("submit_button_hovered.png"),
        ButtonState.PRESSED: Path("submit_button_pressed.png"),
    }
    button_sizes = {
        ButtonState.REGULAR: (CHAL_BUTTON_WIDTH, CHAL_BUTTON_HEIGHT),
        ButtonState.HOVERED: (CHAL_BUTTON_WIDTH, CHAL_BUTTON_HEIGHT),
        ButtonState.PRESSED: (CHAL_BUTTON_WIDTH, CHAL_BUTTON_HEIGHT),
    }
    return load_all_graphic_objects(buttons_path, button_files, button_sizes)


def add_judgement_stamps():
    """Загрузка штампов "Верно" и "Неверно" """

    correct_path = Path(f"{ROOT_CHALLENGE_PATH}\\correct.png")
    incorrect_path = Path(f"{ROOT_CHALLENGE_PATH}\\incorrect.png")

    correct_stamp = load_one_graphic_object(correct_path, STAMP_WIDTH, STAMP_HEIGHT)
    incorrect_stamp = load_one_graphic_object(incorrect_path, STAMP_WIDTH, STAMP_HEIGHT)

    return correct_stamp, incorrect_stamp


def add_tip_card():
    """Загрузка карточки комментария"""
    card_path = Path(f"{ROOT_CHALLENGE_PATH}\\tip_card.png")
    return load_one_graphic_object(card_path, TIP_CARD_WIDTH, TIP_CARD_HEIGHT)


def add_transitions():
    """Загрузка заставок начала, ответов и итога"""
    start_path = Path(f"{ROOT_CHALLENGE_PATH}\\transitions\\start.png")
    check_path = Path(f"{ROOT_CHALLENGE_PATH}\\transitions\\check.png")
    end_path = Path(f"{ROOT_CHALLENGE_PATH}\\transitions\\end.png")

    start_cover = load_one_graphic_object(start_path, SCREEN_WIDTH, SCREEN_HEIGHT)
    check_cover = load_one_graphic_object(check_path, SCREEN_WIDTH, SCREEN_HEIGHT)
    end_cover = load_one_graphic_object(end_path, SCREEN_WIDTH, SCREEN_HEIGHT)

    return start_cover, check_cover, end_cover


def set_challenge_music():
    set_music(Path(f"{ROOT_MUSIC_PATH}\\Challenge.wav"))


def add_challenge_start_sound():
    return load_one_sound_object(Path(f"{ROOT_MUSIC_PATH}\\Start Challenge.wav"))


def add_challenge_transition_sound():
    return load_one_sound_object(Path(f"{ROOT_MUSIC_PATH}\\Transition.wav"))


def add_roll_sound():
    return load_one_sound_object(Path(f"{ROOT_MUSIC_PATH}\\Roll.wav"))


def add_correct_stamp_sound():
    return load_one_sound_object(Path(f"{ROOT_MUSIC_PATH}\\Correct Stamp.wav"))


def add_incorrect_stamp_sound():
    return load_one_sound_object(Path(f"{ROOT_MUSIC_PATH}\\Incorrect Stamp.wav"))


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
