import pygame

from src.levelBuilding import Maze
from src.Util import WallPattern, Border
from src import AssetsLoading


# Константы
TILE_SIZE = 25 # чем меньше, тем мельче клетки, и тем больше их может уместиться на экране


class MazeState:
    maze: Maze.Maze
    player_pos: list[int]

    def __init__(self):
        """Загрузка изображений для отрисовки и создание кеша трансформированных изображений"""

        # Базовые тайлы
        self.base_tiles = AssetsLoading.load_wall_tiles()
        self.floor_tile = AssetsLoading.load_floor_tile()

        # Тайлы для входа и выхода
        self.entrance_tile, self.exit_tile = AssetsLoading.load_entrance_exit_tiles()

        # Тайл для игрока
        self.player_tile = AssetsLoading.load_player_tile()

        # Кэш для отражённых тайлов
        self.flipped_tiles_cache = {}

        # Кэш для повёрнутых тайлов
        self.rotated_tiles_cache = {}

        # Кэш для стен
        self.wall_cache = {}

    def setup_maze(self, width: int = 3, height: int = 3,
                   doors_near_borders: tuple = (Border.WEST, Border.EAST),
                   other_door_coords: tuple[int, int] = (1, 1),
                   more_random: bool = False, curving: bool = False):
        """Инициация структурных данных лабиринта и его генерация, задание позиции игрока"""

        self.maze = Maze.Maze(width, height, doors_near_borders, other_door_coords)
        self.maze.generate_maze(more_random, curving)
        self.player_pos = [self.maze.start.x, self.maze.start.y]

    def check_win(self):
        # Проверка победы
        return self.player_pos[0] == self.maze.end_door.x and self.player_pos[1] == self.maze.end_door.y

    """
    Функции модификации и кеширования тайлов
    """

    def get_flipped_tile(self, pattern, flip_x=False, flip_y=False):
        """Получение отражённого тайла с кэшированием"""
        cache_key = (pattern, flip_x, flip_y)

        if cache_key not in self.flipped_tiles_cache:
            base_tile = self.base_tiles[pattern]
            if flip_x or flip_y:
                transformed = pygame.transform.flip(base_tile, flip_x, flip_y)
                self.flipped_tiles_cache[cache_key] = transformed
            else:
                self.flipped_tiles_cache[cache_key] = base_tile

        return self.flipped_tiles_cache[cache_key]

    def get_rotated_wall(self, pattern, rotation):
        """Получение повёрнутого тайла стены с кэшированием"""
        cache_key = (pattern, rotation)

        if cache_key not in self.rotated_tiles_cache:
            base_tile = self.base_tiles[pattern]
            if rotation != 0:
                rotated = pygame.transform.rotate(base_tile, rotation)
                rotated_rect = rotated.get_rect(center=(TILE_SIZE // 2, TILE_SIZE // 2))
                final_tile = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                final_tile.blit(rotated, rotated_rect)
                self.rotated_tiles_cache[cache_key] = final_tile
            else:
                self.rotated_tiles_cache[cache_key] = base_tile

        return self.rotated_tiles_cache[cache_key]

    def get_wall_pattern_and_transforms(self, x, y):
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

        # Считаем количество проходов
        count = sum([north, south, west, east])

        flip_x = False
        flip_y = False
        rotation = 0
        pattern = WallPattern.SINGLE

        # Определяем паттерн и трансформации
        if count == 0:
            pattern = WallPattern.SINGLE

        elif count == 1:
            # Тупик
            if south:  # Проход снизу - стена смотрит вверх
                pattern = WallPattern.DEAD_END_NORTH
            elif north:  # Проход сверху - стена смотрит вниз
                pattern = WallPattern.DEAD_END_OTHER
                rotation = 180
            elif east:  # Проход справа - стена смотрит влево
                pattern = WallPattern.DEAD_END_OTHER
                rotation = 90
            elif west:  # Проход слева - стена смотрит вправо
                pattern = WallPattern.DEAD_END_OTHER
                rotation = 270

        elif count == 2:
            # Проверяем, прямая это или угол
            if (north and south) or (west and east):
                # Прямая стена
                if north and south:
                    pattern = WallPattern.STRAIGHT_VERTICAL
                else:  # west and east
                    pattern = WallPattern.STRAIGHT_HORIZONTAL
            else:
                # Угол - определяем тип и отражения
                if south and east:  # Пол снизу и справа
                    pattern = WallPattern.CORNER_BOTTOM
                    flip_x, flip_y = False, False
                elif south and west:  # Пол снизу и слева
                    pattern = WallPattern.CORNER_BOTTOM
                    flip_x = True  # Отражаем по горизонтали
                elif north and east:  # Пол сверху и справа
                    pattern = WallPattern.CORNER_TOP
                    flip_x, flip_y = False, False
                elif north and west:  # Пол сверху и слева
                    pattern = WallPattern.CORNER_TOP
                    flip_x = True  # Отражаем по горизонтали

        elif count == 3:
            # Т-образная
            if not north:
                pattern = WallPattern.T_SHAPE_NORTH
            elif not south:
                pattern = WallPattern.T_SHAPE_SOUTH
            elif not east:
                pattern = WallPattern.T_SHAPE_SIDE
            elif not west:
                pattern = WallPattern.T_SHAPE_SIDE
                flip_x = True  # Отражаем по горизонтали для лева

        elif count == 4:
            pattern = WallPattern.CROSS

        return pattern, flip_x, flip_y, rotation

    def get_transformed_tile(self, pattern, flip_x=False, flip_y=False, rotation=0):
        """Получение трансформированного тайла (сначала отражение, потом поворот)"""
        if rotation == 0:
            return self.get_flipped_tile(pattern, flip_x, flip_y)
        else:
            # Для поворота сначала применяем отражение, потом поворот
            flipped = self.get_flipped_tile(pattern, flip_x, flip_y)
            cache_key = (pattern, flip_x, flip_y, rotation)

            if cache_key not in self.rotated_tiles_cache:
                rotated = pygame.transform.rotate(flipped, rotation)
                rotated_rect = rotated.get_rect(center=(TILE_SIZE // 2, TILE_SIZE // 2))
                final_tile = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                final_tile.blit(rotated, rotated_rect)
                self.rotated_tiles_cache[cache_key] = final_tile

            return self.rotated_tiles_cache[cache_key]

    def precalculate_walls(self):
        """Предварительный расчёт всех стен для оптимизации"""
        for y in range(self.maze.height):
            for x in range(self.maze.width):
                if self.maze.pattern[y][x] == 1:
                    cache_key = (x, y)
                    pattern, flip_x, flip_y, rotation = self.get_wall_pattern_and_transforms(x, y)
                    self.wall_cache[cache_key] = self.get_transformed_tile(pattern, flip_x, flip_y, rotation)

    """
    Базовые функции состояния
    """

    def handle_input(self, keys):
        """Обработка ввода с клавиатуры"""
        new_pos = list(self.player_pos)

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            new_pos[0] -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            new_pos[0] += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            new_pos[1] -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            new_pos[1] += 1

        nx, ny = new_pos
        if (0 <= nx < self.maze.width and 0 <= ny < self.maze.height) and self.maze.pattern[ny][nx] == 0:
            self.player_pos = new_pos

    def draw(self, screen):
        """Отрисовка лабиринта"""

        # Отрисовываем пол
        for y in range(self.maze.height):
            for x in range(self.maze.width):
                screen.blit(self.floor_tile, (x * TILE_SIZE, y * TILE_SIZE))

        # Отрисовываем стены
        for y in range(self.maze.height):
            for x in range(self.maze.width):
                if self.maze.pattern[y][x] == 1:
                    cache_key = (x, y)
                    if cache_key not in self.wall_cache:
                        pattern, flip_x, flip_y, rotation = self.get_wall_pattern_and_transforms(x, y)
                        self.wall_cache[cache_key] = self.get_transformed_tile(pattern, flip_x, flip_y, rotation)

                    screen.blit(self.wall_cache[cache_key], (x * TILE_SIZE, y * TILE_SIZE))

        # Отрисовываем игрока
        screen.blit(self.player_tile,
                         (self.player_pos[0] * TILE_SIZE,
                          self.player_pos[1] * TILE_SIZE))

        # Отрисовываем вход и выход
        self.draw_exits(screen)

        if self.check_win():
            self.show_win_message(screen)

    """
    Вспомогательные функции для прорисовки
    """

    def draw_exits(self, screen):
        """Отрисовка входа и выхода с использованием кастомных тайлов"""

        # Отрисовка входа
        screen.blit(self.entrance_tile,
                         (self.maze.start_door.x * TILE_SIZE, self.maze.start_door.y * TILE_SIZE))

        # Отрисовка выхода
        screen.blit(self.exit_tile,
                         (self.maze.end_door.x * TILE_SIZE, self.maze.end_door.y * TILE_SIZE))

    def show_win_message(self, screen):
        """Показ сообщения о победе"""
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

        # Temporarily disabled this for multimodule game testing - Vsevolod
        """
        # Создание нового лабиринта
        other_side_border: dict[str, str] = {'LEFT': 'RIGHT', 'UP': 'DOWN', 'RIGHT': 'LEFT', 'DOWN': 'UP'}
        start_near_border = random.choice(list(other_side_border.keys()))

        other_start_coord = random.randint(1,
                                           (self.maze.width
                                            if start_near_border in ('LEFT', 'RIGHT')
                                            else self.maze.height) - 2)
        if other_start_coord % 2 == 0: other_start_coord -= 1
        other_end_coord = random.randint(1,
                                        (self.maze.width
                                        if start_near_border in ('LEFT', 'RIGHT')
                                        else self.maze.height) - 2)
        if other_end_coord % 2 == 0: other_end_coord -= 1

        self.maze = Maze.Maze(self.maze.width, self.maze.height,
                              (start_near_border, other_side_border[start_near_border]),
                              (other_start_coord, other_end_coord))
        self.maze = self.maze.generate_maze(more_random=True)
        self.player_pos = [self.maze.start.x, self.maze.start.y]

        self.wall_cache.clear()
        """