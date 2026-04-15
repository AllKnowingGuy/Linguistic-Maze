import random

from src.util import TILE_SIZE


def can_move_to(
    new_x: int,
    new_y: int,
    width: int,
    height: int,
    pattern: list[list[int]],
    start_door_x: int,
    start_door_y: int,
    end_door_x: int,
    end_door_y: int,
) -> bool:
    return (
        (0 <= new_x < width and 0 <= new_y < height)
        and pattern[new_y][new_x] == 0
        and not (new_x == start_door_x and new_y == start_door_y)
        and not (new_x == end_door_x and new_y == end_door_y)
    )


class Enemy:
    """Родительский класс для всех врагов"""

    def __init__(self, x: int, y: int, enemy_name: str = "enemy"):
        self.x = x
        self.y = y
        self.enemy_name = enemy_name
        self.active = True

    def check_collision(self, player_tile_x: int, player_tile_y: int) -> bool:
        """Проверка столкновения с игроком"""

        return self.active and self.x == player_tile_x and self.y == player_tile_y

    def deactivate(self):
        """Исчезновение врага после выполнения его задания или завершения диалога"""

        self.active = False


class StationaryEnemy(Enemy):
    """Враги, стоящие на месте"""

    def __init__(self, x: int, y: int, enemy_name: str = "enemy_stationary"):
        super().__init__(x, y, enemy_name)


class PatrollingEnemy(Enemy):
    """Враги, движущиеся по лабиринту"""

    def __init__(self, x: int, y: int, enemy_name: str = "enemy_moving"):
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

        self.steps_per_tile = 15  # Сколько шагов сделает враг на одной клетке
        self.max_tiles = 6  # Максимум клеток, которых можно пройти за раз

        self.tiles_to_move = 0
        self.tiles_moved = 0

    def get_directions(
        self,
        width: int,
        height: int,
        pattern: list[list[int]],
        start_door_x: int,
        start_door_y: int,
        end_door_x: int,
        end_door_y: int,
    ) -> list[tuple[int, int]]:
        """Сбор возможных направлений движения"""

        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]

        available_directions: list[tuple[int, int]] = []

        for dx, dy in directions:
            new_x = self.x + dx
            new_y = self.y + dy

            if can_move_to(
                new_x,
                new_y,
                width,
                height,
                pattern,
                start_door_x,
                start_door_y,
                end_door_x,
                end_door_y,
            ):
                available_directions.append((dx, dy))

        return available_directions

    def get_max_distance(
        self,
        width: int,
        height: int,
        pattern: list[list[int]],
        start_door_x: int,
        start_door_y: int,
        end_door_x: int,
        end_door_y: int,
    ) -> int:
        """Максимальное количество клеток на выбранном направлении"""

        distance = 0
        x, y = self.x + self.direction_x, self.y + self.direction_y
        while can_move_to(
            x,
            y,
            width,
            height,
            pattern,
            start_door_x,
            start_door_y,
            end_door_x,
            end_door_y,
        ):
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

    def move(
        self,
        width: int,
        height: int,
        pattern: list[list[int]],
        start_door_x: int,
        start_door_y: int,
        end_door_x: int,
        end_door_y: int,
    ):
        """Движение в случайном направлении"""

        directions = self.get_directions(
            width, height, pattern, start_door_x, start_door_y, end_door_x, end_door_y
        )
        if not directions:
            return

        self.direction_x, self.direction_y = random.choice(directions)

        max_distance = self.get_max_distance(
            width, height, pattern, start_door_x, start_door_y, end_door_x, end_door_y
        )

        self.tiles_to_move = random.randrange(
            2, min(max_distance, self.max_tiles) + 1, 2
        )
        self.tiles_moved = 0

        step_size = TILE_SIZE / self.steps_per_tile
        self.move_x = self.direction_x * step_size
        self.move_y = self.direction_y * step_size
        self.remaining_steps = self.steps_per_tile
        self.is_moving = True
        self.is_resting = False

    def update(
        self,
        width: int,
        height: int,
        pattern: list[list[int]],
        start_door_x: int,
        start_door_y: int,
        end_door_x: int,
        end_door_y: int,
        dt: int,
    ) -> bool:
        """Обновление состояния врага каждый кадр"""

        if not self.active:
            return False

        if self.is_resting:
            self.break_timer += dt
            if self.break_timer >= self.break_duration:
                self.move(
                    width,
                    height,
                    pattern,
                    start_door_x,
                    start_door_y,
                    end_door_x,
                    end_door_y,
                )
                return True
            return False

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
                    if can_move_to(
                        new_x,
                        new_y,
                        width,
                        height,
                        pattern,
                        start_door_x,
                        start_door_y,
                        end_door_x,
                        end_door_y,
                    ):
                        self.remaining_steps = self.steps_per_tile
                    else:
                        self.start_rest()
        return True

    def get_pixel_position(self) -> tuple[int, int]:
        """Возвращение позиции в пикселях для отрисовки"""

        return self.pixel_x - TILE_SIZE // 2, self.pixel_y - TILE_SIZE // 2
