import pygame

from src.levelBuilding import Maze
from src.Util import Command, WallPattern, Border, TILE_SIZE, PLAYER_SIZE
from src import AssetsCreation
from src.AssetsCreation import Transformer
from src.playstates.BaseState import BaseState


# Трансформер спрайтов
transformer = Transformer()


# Константы
HALF_PLAYER = PLAYER_SIZE / 2


class MazeState(BaseState):
    maze: Maze.Maze
    player_pos: list[int] # в целых пикселях, так как дроби в Python дают огромные погрешности
    current_level: int

    def __init__(self):
        """Загрузка изображений для отрисовки и создание кеша трансформированных изображений"""

        # Inheritance is so stupid, the super class contains literally nothing - Vsevolod
        super().__init__()

        # Текущий уровень
        self.current_level = 1

        # Тайлы для основания и границ стен. Используют именно current level
        self.wall_tiles = AssetsCreation.add_wall_tiles(self.current_level)

        # Тайл для пола. Используется именно current level
        self.floor_tile = AssetsCreation.add_floor_tile(self.current_level)

        # Тайлы для входа и выхода. Используется именно current level
        self.entrance_tile, self.exit_tile = AssetsCreation.add_entrance_exit_tiles(self.current_level)

        # Тайл для игрока. Используется именно current level
        self.player_tile = AssetsCreation.add_player_tile(self.current_level)

        # Кэш для стен
        self.wall_cache = {}

    def set_level(self, level):
        """Устанавливает уровень и перезагружает изображения"""
        self.current_level = level
        self.reload_tiles()
        if hasattr(self, 'maze') and self.maze is not None: # Checks if the maze was succsesfully created I guess IM not sure
            self.precalculate_walls()

    def reload_tiles(self):
        """Перезагрузка изображений для текущего уровня"""
        self.wall_tiles = AssetsCreation.add_wall_tiles(self.current_level)
        self.floor_tile = AssetsCreation.add_floor_tile(self.current_level)
        self.entrance_tile, self.exit_tile = AssetsCreation.add_entrance_exit_tiles(self.current_level)
        self.player_tile = AssetsCreation.add_player_tile(self.current_level)
        self.wall_cache.clear()

    def setup_maze(self, width: int = 3, height: int = 3,
                   doors_near_borders: tuple = (Border.WEST, Border.EAST),
                   other_door_coords: tuple[int, int] = (1, 1),
                   more_random: bool = False, curving: bool = False):
        """Задание структурных данных лабиринта и его генерация, задание позиции игрока"""
        # TODO: enable switching to a preloaded maze and specifying player position

        self.maze = Maze.Maze(width, height, doors_near_borders, other_door_coords)
        self.maze.generate_maze(more_random, curving)
        self.player_pos = [int((self.maze.start.x + 0.5) * TILE_SIZE),
                           int((self.maze.start.y + 0.5) * TILE_SIZE)]

        # Кеширование стен для отрисовки
        self.wall_cache.clear()
        self.precalculate_walls()

        return self.maze

    def check_win(self):
        # Проверка победы
        return (self.maze.end_door.x <= self.player_pos[0] // TILE_SIZE <= self.maze.end_door.x + 1
                and self.maze.end_door.y <= self.player_pos[1] // TILE_SIZE <= self.maze.end_door.y + 1)

    """
    Функции модификации и кеширования тайлов
    """

    def get_wall_patterns_and_transforms(self, x, y):
        """Определение паттерна стены и необходимых трансформаций"""

        def is_floor(nx, ny):
            if 0 <= nx < self.maze.width and 0 <= ny < self.maze.height:
                return self.maze.pattern[ny][nx] == 0
            return False

        # Проверяем соседей
        north = is_floor(x, y - 1)
        south = is_floor(x, y + 1)
        west = is_floor(x - 1, y)
        east = is_floor(x + 1, y)
        north_west = is_floor(x - 1, y - 1)
        north_east = is_floor(x + 1, y - 1)
        south_west = is_floor(x - 1, y + 1)
        south_east = is_floor(x + 1, y + 1)

        # Задаём хранение слоев и их трансформаций
        x_flips = [False]
        rotations = [0]
        patterns = [WallPattern.SINGLE]

        # Определяем паттерн и трансформации
        if north:  # Проход сверху
            patterns.append(WallPattern.STRAIGHT)
            x_flips.append(False)
            rotations.append(0)
        if east:  # Проход справа
            patterns.append(WallPattern.STRAIGHT)
            x_flips.append(False)
            rotations.append(90)
        if west:  # Проход слева
            patterns.append(WallPattern.STRAIGHT)
            x_flips.append(False)
            rotations.append(270)
        if south:  # Проход снизу (ОПРЕДЕЛЯЕМ В ПОСЛЕДНЮЮ ОЧЕРЕДЬ!)
            patterns.append(WallPattern.STRAIGHT_SOUTH)
            x_flips.append(False)
            rotations.append(0)

        if north_west and not (north or west):
            patterns.append(WallPattern.CORNER)
            x_flips.append(False)
            rotations.append(0)
        if north_east and not (north or east):
            patterns.append(WallPattern.CORNER)
            x_flips.append(True)
            rotations.append(0)
        if south_west and not (south or west):
            patterns.append(WallPattern.CORNER_SOUTH)
            x_flips.append(False)
            rotations.append(0)
        if south_east and not (south or east):
            patterns.append(WallPattern.CORNER_SOUTH)
            x_flips.append(True)
            rotations.append(0)

        return patterns, x_flips, rotations

    def get_transformed_tile(self, patterns, x_flips=(False,), rotations=(0,)):
        """Получение трансформированного тайла (сначала отражение, потом поворот)"""
        layers = []

        # Трансформация границ (сначала применяем отражение, потом поворот)
        for p_id, pattern in enumerate(patterns):
            if p_id == 0:
                # Копирование основания стены, чтобы границы всех стен не наложились на одну
                base_tile_copy = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                base_tile_copy.blit(self.wall_tiles[patterns[p_id]], (0, 0))
                layers.append(base_tile_copy)
            else:
                tile = self.wall_tiles[patterns[p_id]]
                if rotations[p_id] == 0:
                    layers.append(transformer.get_flipped(tile, x_flips[p_id]))
                else:
                    flipped = transformer.get_flipped(tile, x_flips[p_id])
                    rotated = transformer.get_rotated(flipped, rotations[p_id])
                    layers.append(rotated)

                # Наложение границ на основание стены
                layers[0].blit(layers[p_id], (0, 0))

        return layers[0]

    def precalculate_walls(self):
        """Предварительный расчёт всех стен для оптимизации"""
        for y in range(self.maze.height):
            for x in range(self.maze.width):
                if self.maze.pattern[y][x] == 1:
                    cache_key = (x, y)
                    patterns, x_flips, rotations = self.get_wall_patterns_and_transforms(x, y)
                    self.wall_cache[cache_key] = self.get_transformed_tile(patterns, x_flips, rotations)

    """
    Переписанные функции состояния
    """

    def handle_hold_input(self, pressed_keys):
        """Обработка кнопок перемещения"""
        # TODO: for real make keybind customization
        new_pos = list(self.player_pos)
        move_by = 3

        if pressed_keys[pygame.K_LEFT] or pressed_keys[pygame.K_a]:
            new_pos[0] -= move_by
        if pressed_keys[pygame.K_RIGHT] or pressed_keys[pygame.K_d]:
            new_pos[0] += move_by
        if pressed_keys[pygame.K_UP] or pressed_keys[pygame.K_w]:
            new_pos[1] -= move_by
        if pressed_keys[pygame.K_DOWN] or pressed_keys[pygame.K_s]:
            new_pos[1] += move_by

        nx, ny = new_pos
        if 0 <= nx < self.maze.width * TILE_SIZE - PLAYER_SIZE and 0 <= ny < self.maze.height * TILE_SIZE - PLAYER_SIZE:
            x_relative = nx % TILE_SIZE
            y_relative = ny % TILE_SIZE
            nx_tile = nx // TILE_SIZE
            ny_tile = ny // TILE_SIZE
            nx_tile_neighbor = (nx_tile - 1 if x_relative < HALF_PLAYER
                       else nx_tile + 1 if x_relative > TILE_SIZE - HALF_PLAYER
                       else nx_tile)
            ny_tile_neighbor = (ny_tile - 1 if y_relative < HALF_PLAYER
                       else ny_tile + 1 if y_relative > TILE_SIZE - HALF_PLAYER
                       else ny_tile)
            for x in (nx_tile_neighbor, nx_tile):
                if not self.maze.pattern[self.player_pos[1] // TILE_SIZE][int(x)] == 0:
                    new_pos[0] = self.player_pos[0]
                    break
            for y in (ny_tile_neighbor, ny_tile):
                if not self.maze.pattern[int(y)][self.player_pos[0] // TILE_SIZE] == 0:
                    new_pos[1] = self.player_pos[1]
                    break
            self.player_pos = new_pos

        return (Command.CHECK_PROGRESS, None),

    def draw(self, screen):
        """Отрисовка лабиринта"""

        # TODO: make camera move along with the character for mazes that exceed screen bounds

        # Отрисовываем пол и стены
        for y in range(self.maze.height):
            for x in range(self.maze.width):
                if self.maze.pattern[y][x] == 1:
                    # в этой клетке стена
                    cache_key = (x, y)
                    screen.blit(self.wall_cache[cache_key], (x * TILE_SIZE, y * TILE_SIZE))
                else:
                    # в этой клетке пол
                    screen.blit(self.floor_tile, (x * TILE_SIZE, y * TILE_SIZE))

        # Отрисовываем вход и выход
        self.draw_exits(screen)

        # Отрисовываем игрока (поверх всего!)
        screen.blit(self.player_tile, ((self.player_pos[0]) - HALF_PLAYER, (self.player_pos[1]) - HALF_PLAYER))

    """
    Вспомогательные функции для отрисовки
    """

    def draw_exits(self, screen):
        """Отрисовка входа и выхода с использованием кастомных тайлов"""

        # Отрисовка входа
        screen.blit(self.entrance_tile,
                         (self.maze.start_door.x * TILE_SIZE, self.maze.start_door.y * TILE_SIZE))

        # Отрисовка выхода
        screen.blit(self.exit_tile,
                         (self.maze.end_door.x * TILE_SIZE, self.maze.end_door.y * TILE_SIZE))

    """
    def show_win_message(self, screen):
        width = screen.get_width()
        height = screen.get_height()

        font = pygame.font.Font(None, 48)
        text = font.render("ПОБЕДА! ПРОДОЛЖЕНИЕ СЛЕДУЕТ...", True, (255, 255, 0))
        text_rect = text.get_rect(center=(width // 2, height // 2))

        overlay = pygame.Surface((width, height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # Показываем тайл выхода в сообщении
        exit_rect = self.exit_tile.get_rect(center=(width // 2, height // 2 - TILE_SIZE))
        screen.blit(self.exit_tile, exit_rect)

        screen.blit(text, text_rect)
        pygame.display.flip()

        pygame.time.wait(1500)
    """
