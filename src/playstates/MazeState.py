import pygame

from src.levelBuilding import Maze
from src.levelBuilding.Enemy import Enemy, StationaryEnemy
from src.Util import Command, WallPattern, Border, TILE_SIZE, PLAYER_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT
from src import AssetsCreation
from src.AssetsCreation import Transformer
from src.playstates.BaseState import BaseState


# Трансформер спрайтов
transformer = Transformer()


# Константы
HALF_PLAYER = PLAYER_SIZE / 2
HALF_WIDTH = SCREEN_WIDTH / 2
HALF_HEIGHT = SCREEN_HEIGHT / 2


class MazeState(BaseState):
    maze: Maze.Maze | None
    player_pos: list[int]
    current_level: int

    def __init__(self):
        """Загрузка изображений для отрисовки и создание кеша трансформированных изображений"""

        super().__init__()

        """Параметры по умолчанию"""
        self.maze = None

        # Позиция игрока
        self.player_pos = [int(1.5 * TILE_SIZE), int(1.5 * TILE_SIZE)]

        # Текущий уровень
        self.current_level = 0

        # Тайлы для основания и границ стен. Используют именно current level
        self.wall_tiles = AssetsCreation.add_wall_tiles(self.current_level)

        # Тайл для пола. Используется именно current level
        self.floor_tile = AssetsCreation.add_floor_tile(self.current_level)

        # Тайлы для входа и выхода. Используется именно current level
        self.entrance_tile, self.exit_tile = AssetsCreation.add_entrance_exit_tiles(self.current_level)

        # Тайл для игрока
        self.player_tile = AssetsCreation.add_player_tile()

        # Список спрайтов ходьбы персонажа
        self.player_walk_frames = AssetsCreation.add_player_walk()

        # Тайл для монстра
        self.enemy_tile = AssetsCreation.add_enemy_tile(self.current_level)

        # Кэш для стен
        self.wall_cache = {}

        # Параметры анимации персонажа
        self.animation_index = 0 # Номер кадра анимации из списка
        self.last_animation_time = pygame.time.get_ticks()
        self.animation_speed = 200
        self.is_moving = False
        self.facing_left = False
        self.current_player_image = self.player_tile

        # Параметры темноты
        self.darkness_enabled = True # Если темнота будет мешать тестированию других вещей, ее можно убрать
        self.darkness_alpha = 255
        self.light_radius = 200

        self.darkness_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

        # Список врагов лабиринта
        self.enemies = []

    def update_animation(self):
        """Обновление кадров анимации"""

        current_time = pygame.time.get_ticks()

        if self.is_moving and self.player_walk_frames:
            if current_time - self.last_animation_time > self.animation_speed:
                self.animation_index = (self.animation_index + 1) % len(self.player_walk_frames) # 0->1->2->3->0
                self.last_animation_time = current_time
            self.current_player_image = self.player_walk_frames[self.animation_index]
        else:
            self.current_player_image = self.player_tile
            self.animation_index = 0

        if self.facing_left:
            self.current_player_image = transformer.get_flipped(self.current_player_image, True)

    def apply_darkness(self, screen):
        """Наложение темноты на экран"""

        if not self.darkness_enabled:
            return

        self.darkness_surface.fill((0, 0, 0, 0))
        pygame.draw.rect(self.darkness_surface, (0, 0, 0, self.darkness_alpha),
                         (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

        # Кружок света вокруг игрока - зависит от положения камеры
        player_screen_x, player_screen_y = self.apply_shift(
            self.player_pos[0] - HALF_PLAYER,
            self.player_pos[1] - HALF_PLAYER
        )
        player_center_x = player_screen_x + HALF_PLAYER
        player_center_y = player_screen_y + HALF_PLAYER

        # "Плавный" переход от света к темноте путем создания нескольких кружков разных радиусов (от центра к краям)
        pygame.draw.circle(self.darkness_surface, (0, 0, 0, self.darkness_alpha - 30),
                           (player_center_x, player_center_y),
                           self.light_radius)

        pygame.draw.circle(self.darkness_surface, (0, 0, 0, self.darkness_alpha // 2),
                           (player_center_x, player_center_y),
                           self.light_radius - 20)

        pygame.draw.circle(self.darkness_surface, (0, 0, 0, 0),
                           (player_center_x, player_center_y),
                           self.light_radius - 40)

        screen.blit(self.darkness_surface, (0,0))

    def set_level(self, level: int):
        """Задание уровня и перезагрузка изображений"""

        self.current_level = level
        self.reload_tiles()
        if self.maze is not None:
            self.precalculate_walls()

    def reload_tiles(self):
        """Перезагрузка изображений для текущего уровня"""

        self.wall_tiles = AssetsCreation.add_wall_tiles(self.current_level)
        self.floor_tile = AssetsCreation.add_floor_tile(self.current_level)
        self.entrance_tile, self.exit_tile = AssetsCreation.add_entrance_exit_tiles(self.current_level)
        self.player_tile = AssetsCreation.add_player_tile()
        self.enemy_tile = AssetsCreation.add_enemy_tile(self.current_level)
        self.wall_cache.clear()

    def setup_maze(self, width: int = 3, height: int = 3,
                   doors_near_borders: tuple[Border, Border] = (Border.WEST, Border.EAST),
                   other_door_coords: tuple[int, int] = (1, 1),
                   more_random: bool = False, curving: bool = False):
        """
        Задание структурных данных лабиринта и его генерация, задание позиции игрока

        Args:
            width (int): Ширина лабиринта (должна быть нечётным числом!)
            height (int): Высота лабиринта (должна быть нечётным числом!)
            doors_near_borders (tuple[Border]): Границы лабиринта, в которых расположены двери входа и выхода соответственно
            other_door_coords (tuple[int, int]): Определяющие координаты дверей входа и выхода (если дверь в северной или южной стене - координата X, иначе - координата Y)
            more_random (bool): Должен ли лабиринт генерироваться по альтернативному алгоритму для увеличения ветвления
            curving (bool): Должен ли лабиринт избегать генерации прямых коридоров, если это возможно
        """
        # TODO: maybe enable switching to a preloaded maze and specifying player position

        self.maze = Maze.Maze(width, height, doors_near_borders, other_door_coords)
        self.maze.generate_maze(more_random, curving)
        self.player_pos = [int((self.maze.start.x + 0.5) * TILE_SIZE),
                           int((self.maze.start.y + 0.5) * TILE_SIZE)]

        # Кеширование стен для отрисовки
        self.wall_cache.clear()
        self.precalculate_walls()

        # Очищаем список врагов
        self.enemies.clear()

        # Тестовый враг перед выходом
        enemy_x = self.maze.end.x
        enemy_y = self.maze.end.y

        # Проверяем возможность создать тут врага
        if (0 <= enemy_x < self.maze.width) and (self.maze.pattern[enemy_y][enemy_x] == 0):
            enemy = StationaryEnemy(enemy_x, enemy_y, "enemy_at_exit")
            self.enemies.append(enemy)
            print(f"Создан враг на ({enemy_x}, {enemy_y})")
        else:
            print(f"Не удалось создать врага: клетка ({enemy_x}, {enemy_y}) недоступна")

        return self.maze

    def check_enemy_collision(self) -> Enemy | None:
        # Проверяет столкновение врага и героя
        player_tile_x = self.player_pos[0] // TILE_SIZE
        player_tile_y = self.player_pos[1] // TILE_SIZE

        for enemy in self.enemies:
            if enemy.check_collision(player_tile_x, player_tile_y):
                return enemy

        return None

    def check_win(self):
        # Проверка победы
        return (self.maze.end_door.x <= self.player_pos[0] // TILE_SIZE < self.maze.end_door.x + 1
                and self.maze.end_door.y <= self.player_pos[1] // TILE_SIZE < self.maze.end_door.y + 1)

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
        if north: # "Верхняя" граница стены
            patterns.append(WallPattern.STRAIGHT)
            x_flips.append(False)
            rotations.append(0)
        if east: # Правая граница стены
            patterns.append(WallPattern.STRAIGHT)
            x_flips.append(False)
            rotations.append(90)
        if west: # Левая граница стены
            patterns.append(WallPattern.STRAIGHT)
            x_flips.append(False)
            rotations.append(270)
        if south: # "Нижняя" граница стены (ОПРЕДЕЛЯЕМ В ПОСЛЕДНЮЮ ОЧЕРЕДЬ, ТАК КАК ОНА ОСОБАЯ!)
            patterns.append(WallPattern.STRAIGHT_SOUTH)
            x_flips.append(False)
            rotations.append(0)

        if north_west and not (north or west): # "Верхний" левый угол стены
            patterns.append(WallPattern.CORNER)
            x_flips.append(False)
            rotations.append(0)
        if north_east and not (north or east): # "Верхний" правый угол стены
            patterns.append(WallPattern.CORNER)
            x_flips.append(True)
            rotations.append(0)
        if south_west and not (south or west): # "Нижний" левый угол стены
            patterns.append(WallPattern.CORNER_SOUTH)
            x_flips.append(False)
            rotations.append(0)
        if south_east and not (south or east): # "Нижний" правый угол стены
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
        move_by = PLAYER_SIZE // 6 # would you know how tired I am of floats - Vsevolod
        moving = False

        if pressed_keys[pygame.K_LEFT] or pressed_keys[pygame.K_a]:
            new_pos[0] -= move_by
            self.facing_left = True
            moving = True
        if pressed_keys[pygame.K_RIGHT] or pressed_keys[pygame.K_d]:
            new_pos[0] += move_by
            self.facing_left = False
            moving = True
        if pressed_keys[pygame.K_UP] or pressed_keys[pygame.K_w]:
            new_pos[1] -= move_by
            moving = True
        if pressed_keys[pygame.K_DOWN] or pressed_keys[pygame.K_s]:
            new_pos[1] += move_by
            moving = True

        self.is_moving = moving

        if (0 <= new_pos[0] < self.maze.width * TILE_SIZE - PLAYER_SIZE
            and 0 <= new_pos[1] < self.maze.height * TILE_SIZE - PLAYER_SIZE):
            self.move_player(new_pos)

            # Столкновение с врагом
            enemy = self.check_enemy_collision()
            if enemy:
                self.is_moving = False

        return (Command.CHECK_PROGRESS, None),

    def handle_button_release(self, event, pressed_keys):
        """Сброс анимации движения при отпуске всех кнопок"""
        # TODO: KEYBIND CUSTOMIZATION
        if not any(key in pressed_keys for key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN,
                                                   pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s)):
            self.is_moving = False

    def draw(self, screen):
        """Отрисовка лабиринта"""

        # Обновляем анимацию перед отрисовкой лабиринта
        self.update_animation()

        # Отрисовываем пол и стены
        for y in range(self.maze.height):
            for x in range(self.maze.width):
                if self.maze.pattern[y][x] == 1:
                    # в этой клетке стена
                    cache_key = (x, y)
                    screen.blit(self.wall_cache[cache_key], self.apply_shift(x * TILE_SIZE, y * TILE_SIZE))
                else:
                    # в этой клетке пол
                    screen.blit(self.floor_tile, self.apply_shift(x * TILE_SIZE, y * TILE_SIZE))

        # Отрисовываем вход и выход
        self.draw_exits(screen)

        # Отрисовываем игрока (поверх всего! + с текущим кадром анимации)
        screen.blit(self.current_player_image,
                    self.apply_shift((self.player_pos[0]) - HALF_PLAYER, (self.player_pos[1]) - HALF_PLAYER))

        # Отрисовываем врагов
        for enemy in self.enemies:
            if enemy.active:
                screen.blit(self.enemy_tile, self.apply_shift(enemy.x * TILE_SIZE, enemy.y * TILE_SIZE))

        # Накладываем темноту поверх всего-всего
        self.apply_darkness(screen)

    """
    Вспомогательные функции для обработки нажатых кнопок
    """

    def move_player(self, new_pos):
        """Перемещение игрока на одну из возможных позиций для текущих нажатых кнопок"""

        # Новые и предыдущие координаты игрока
        nx, ny = new_pos
        px, py = self.player_pos

        # Нахождение текущей и соседней (если необходимо) клеток по позиции игрока для новых координат
        nx_tile = nx // TILE_SIZE
        ny_tile = ny // TILE_SIZE
        nx_tile_neighbor = (nx_tile - 1 if nx % TILE_SIZE < HALF_PLAYER
                            else nx_tile + 1 if nx % TILE_SIZE > TILE_SIZE - HALF_PLAYER
                            else nx_tile)
        ny_tile_neighbor = (ny_tile - 1 if ny % TILE_SIZE < HALF_PLAYER
                            else ny_tile + 1 if ny % TILE_SIZE > TILE_SIZE - HALF_PLAYER
                            else ny_tile)

        # То же самое для предыдущих координат
        px_tile = px // TILE_SIZE
        py_tile = py // TILE_SIZE
        px_tile_neighbor = (px_tile - 1 if px % TILE_SIZE < HALF_PLAYER
                            else px_tile + 1 if px % TILE_SIZE > TILE_SIZE - HALF_PLAYER
                            else px_tile)
        py_tile_neighbor = (py_tile - 1 if py % TILE_SIZE < HALF_PLAYER
                            else py_tile + 1 if py % TILE_SIZE > TILE_SIZE - HALF_PLAYER
                            else py_tile)

        # Проверка соседних клеток для движения: по X и Y -> по X -> по Y (чтобы игрок не "приклеивался" к стенам)
        for bunch in ((nx_tile, nx_tile_neighbor, ny_tile, ny_tile_neighbor, nx, ny),
                      (nx_tile, nx_tile_neighbor, py_tile, py_tile_neighbor, nx, py),
                      (px_tile, px_tile_neighbor, ny_tile, ny_tile_neighbor, px, ny)):
            if self.check_new_pos(bunch[0], bunch[1], bunch[2], bunch[3]):
                self.player_pos = [bunch[4], bunch[5]]
                return

    def check_new_pos(self, x_tile, x_tile_neighbor, y_tile, y_tile_neighbor):
        """Проверка окружения позиции, в которую собирается переместиться игрок"""

        for x in (x_tile_neighbor, x_tile):
            for y in (y_tile_neighbor, y_tile):
                if not self.maze.pattern[int(y)][int(x)] == 0:
                    break
            else:
                continue
            break
        else:
            return True
        return False

    """
    Вспомогательные функции для отрисовки
    """

    def draw_exits(self, screen):
        """Отрисовка входа и выхода с использованием кастомных тайлов"""

        # Отрисовка входа
        screen.blit(self.entrance_tile,
                    self.apply_shift(self.maze.start_door.x * TILE_SIZE, self.maze.start_door.y * TILE_SIZE))

        # Отрисовка выхода
        screen.blit(self.exit_tile,
                    self.apply_shift(self.maze.end_door.x * TILE_SIZE, self.maze.end_door.y * TILE_SIZE))

    def apply_shift(self, x, y):
        east_x_margin = self.maze.width * TILE_SIZE - HALF_WIDTH
        south_y_margin = self.maze.height * TILE_SIZE - HALF_HEIGHT
        x_shift = (self.player_pos[0] if self.player_pos[0] < east_x_margin else east_x_margin) - HALF_WIDTH
        y_shift = (self.player_pos[1] if self.player_pos[1] < south_y_margin else south_y_margin) - HALF_HEIGHT
        return x - (x_shift if x_shift > 0 else 0), y - (y_shift if y_shift > 0 else 0)
