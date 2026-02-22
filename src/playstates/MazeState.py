import pygame

from src.levelBuilding import Maze
from src.Util import WallPattern, Border, TILE_SIZE
from src import AssetsCreation
from src.AssetsCreation import Transformer
from src.playstates.BaseState import BaseState


# Трансформер спрайтов
transformer = Transformer()


class MazeState(BaseState):
    maze: Maze.Maze
    player_pos: list[int]

    def __init__(self):
        """Загрузка изображений для отрисовки и создание кеша трансформированных изображений"""

        # Inheritance is so stupid, the super class contains literally nothing - Vsevolod
        super().__init__()

        # Тайлы для основания и границ стен
        self.wall_tiles = AssetsCreation.load_wall_tiles()

        # Тайл для пола
        self.floor_tile = AssetsCreation.load_floor_tile()

        # Тайлы для входа и выхода
        self.entrance_tile, self.exit_tile = AssetsCreation.load_entrance_exit_tiles()

        # Тайл для игрока
        self.player_tile = AssetsCreation.load_player_tile()

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

        # Кеширование стен для отрисовки
        self.wall_cache.clear()
        self.precalculate_walls()

    def check_win(self):
        # Проверка победы
        return self.player_pos[0] == self.maze.end_door.x and self.player_pos[1] == self.maze.end_door.y

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

    def handle_input(self, keys):
        """Обработка кнопок перемещения"""
        # TODO: for real make keybind customization
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

        # TODO: make camera move along with the character for mazes that exceed screen bounds

        # Отрисовываем пол
        for y in range(self.maze.height):
            for x in range(self.maze.width):
                screen.blit(self.floor_tile, (x * TILE_SIZE, y * TILE_SIZE))

        # Отрисовываем стены
        for y in range(self.maze.height):
            for x in range(self.maze.width):
                if self.maze.pattern[y][x] == 1:
                    cache_key = (x, y)
                    screen.blit(self.wall_cache[cache_key], (x * TILE_SIZE, y * TILE_SIZE))

        # Отрисовываем вход и выход
        self.draw_exits(screen)

        # Отрисовываем игрока (поверх всего!)
        screen.blit(self.player_tile,
                         (self.player_pos[0] * TILE_SIZE,
                          self.player_pos[1] * TILE_SIZE))

        if self.check_win():
            self.show_win_message(screen)

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