import random
from src.util import TILE_SIZE


class Enemy:
    """Родительский класс для всех врагов"""

    def __init__(self, x: int, y: int, enemy_name: str = 'enemy'):
        self.x = x
        self.y = y
        self.enemy_name = enemy_name
        self.active = True

    def check_collision(self, player_tile_x: int, player_tile_y: int):
        """Проверка столкновения с игроком"""
        return self.active and self.x == player_tile_x and self.y == player_tile_y

    def deactivate(self):
        """Исчезновение врага после выполнения его задания"""
        self.active = False


class StationaryEnemy(Enemy):
    """Враги, стоящие на месте"""

    def __init__(self, x: int, y: int, enemy_name: str = 'enemy_stationary'):
        super().__init__(x, y, enemy_name)


class PatrollingEnemy(Enemy):
    """Враги, движущиеся по лабиринту"""

    def __init__(self, x: int, y: int, enemy_name: str = 'enemy_moving'):
        super().__init__(x, y, enemy_name)

        self.pixel_x = x * TILE_SIZE + TILE_SIZE // 2
        self.pixel_y = y * TILE_SIZE + TILE_SIZE // 2

        self.is_moving = False
        self.move_x = 0
        self.move_y = 0
        self.remaining_steps = 0
        self.direction_x = 0
        self.direction_y = 0

        self.is_resting = True
        self.break_timer = 0
        self.break_duration = 2000

        self.steps_per_tile = 15 # Сколько шагов сделает враг на одной клетке
        self.max_tiles = 5   # Максимум клеток, которых можно пройти за раз

        self.tiles_to_move = 0
        self.tiles_moved = 0


    def get_directions(self, maze):
        """Сбор возможных направлений движения"""

        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]

        available_directions = []

        for dx, dy in directions:
            new_x = self.x + dx
            new_y = self.y + dy

            if (0 <= new_x < maze.width and
                    0 <= new_y < maze.height and
                    maze.pattern[new_y][new_x] == 0):
                available_directions.append((dx, dy))

        return available_directions

    def get_max_distance(self, maze):
        """Максимальное количество клеток на выбранном направлении"""
        distance = 0
        x, y = self.x + self.direction_x, self.y + self.direction_y
        while (0 <= x < maze.width and 0 <= y < maze.height
               and maze.pattern[y][x] == 0):
            distance += 1
            x += self.direction_x
            y += self.direction_y
        return distance


    def start_rest(self):
        """Период ожидания врага"""
        self.is_moving = False
        self.is_resting = True
        self.break_timer = 0
        self.move_x = 0
        self.move_y = 0
        self.remaining_steps = 0

    def move(self, maze):
        """Движение в случайном направлении"""
        directions = self.get_directions(maze)
        if not directions:
            return

        self.direction_x, self.direction_y = random.choice(directions)

        max_distance = self.get_max_distance(maze)

        self.tiles_to_move = random.randint(1, min(max_distance, self.max_tiles))
        self.tiles_moved = 0

        step_size = TILE_SIZE / self.steps_per_tile
        self.move_x = self.direction_x * step_size
        self.move_y = self.direction_y * step_size
        self.remaining_steps = self.steps_per_tile
        self.is_moving = True
        self.is_resting = False



    def update(self, maze, dt: int):
        """Обновление состояния врага каждый кадр"""

        if not self.active:
            return

        if self.is_resting:
            self.break_timer += dt
            if self.break_timer >= self.break_duration:
                self.move(maze)
            return

        if self.is_moving and self.remaining_steps > 0:
            self.pixel_x += self.move_x
            self.pixel_y += self.move_y
            self.remaining_steps -= 1

            if self.remaining_steps == 0:
                self.x += self.direction_x
                self.y += self.direction_y
                self.tiles_moved += 1

                if self.tiles_moved >= self.tiles_to_move:
                    self.start_rest()
                else:
                    new_x, new_y = self.x + self.direction_x, self.y + self.direction_y
                    if (0 <= new_x < maze.width and 0 <= new_y < maze.height and
                    maze.pattern[new_y][new_x] == 0):
                        self.remaining_steps = self.steps_per_tile
                    else:
                        self.start_rest()

    def get_pixel_position(self):
        """Возвращение позиции в пикселях для отрисовки"""
        return (self.pixel_x - TILE_SIZE // 2, self.pixel_y - TILE_SIZE // 2)
