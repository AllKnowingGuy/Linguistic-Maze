import random

from src.util import Border
from src.level_building.enemy import Enemy, StationaryEnemy, PatrollingEnemy


class Tile:
    """Класс для хранения координат элемента лабиринта"""

    def __init__(self, x: int = None, y: int = None):
        self.x = x
        self.y = y


class Maze:
    width: int
    height: int
    start: Tile
    end: Tile
    start_door: Tile
    end_door: Tile
    monsters: list[Enemy]

    def __init__(self, width: int = 3, height: int = 3,
                 doors_near_borders: tuple = (Border.WEST, Border.EAST),
                 other_door_coords: tuple[int, int] = (1, 1)):
        self.width = width
        self.height = height

        self.start = Tile()
        self.end = Tile()
        self.start_door = Tile()
        self.end_door = Tile()

        for door_ind, door in enumerate(((self.start, self.start_door), (self.end, self.end_door))):
            if doors_near_borders[door_ind].name == Border.WEST.name:
                door[0].x = 1
                door[1].x = 0
                door[0].y = door[1].y = other_door_coords[door_ind]
            elif doors_near_borders[door_ind].name == Border.EAST.name:
                door[0].x = self.width - 2
                door[1].x = self.width - 1
                door[0].y = door[1].y = other_door_coords[door_ind]
            elif doors_near_borders[door_ind].name == Border.NORTH.name:
                door[0].x = door[1].x = other_door_coords[door_ind]
                door[0].y = 1
                door[1].y = 0
            elif doors_near_borders[door_ind].name == Border.SOUTH.name:
                door[0].x = door[1].x = other_door_coords[door_ind]
                door[0].y = self.height - 2
                door[1].y = self.height - 1

        self.pattern = [[1]]
        self.monsters = []

    def generate_maze(self, more_random: bool = False, curving: bool = False):
        """Генерация лабиринта модифицированным алгоритмом DFS"""
        self.pattern = [[1 for _ in range(self.width)] for _ in range(self.height)]

        # Определение старта и финиша
        self.pattern[self.start.y][self.start.x] = 0

        pile = [(self.start.x, self.start.y, (0, 0))]
        directions = [(0, -2), (-2, 0), (2, 0), (0, 2)]

        while pile:
            if more_random:
                growing_tile = random.choice(pile)
                # TODO: try picking from tiles closer to the end of the pile, not from all tiles
            else:
                growing_tile = pile[-1]
            growing_ind = pile.index(growing_tile)
            x, y, created_from = growing_tile

            unvisited = []
            unfavored_option = None
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if (0 < nx < self.width - 1 and 0 < ny < self.height - 1) and self.pattern[ny][nx] == 1:
                    unvisited.append((nx, ny, dx, dy))
                    if curving and (dx, dy) == created_from:
                        unfavored_option = unvisited.pop()

            if unvisited or unfavored_option:
                if not unvisited:
                    unvisited.append(unfavored_option)
                nx, ny, dx, dy = random.choice(unvisited)
                self.pattern[y + dy // 2][x + dx // 2] = 0
                self.pattern[ny][nx] = 0
                pile.append((nx, ny, (dx, dy)))
            else:
                pile.pop(growing_ind)

        # Добавляем вход и выход
        self.pattern[self.start_door.y][self.start_door.x] = 0
        self.pattern[self.end_door.y][self.end_door.x] = 0

    def place_monsters(self, monsters: dict[str, tuple[int, int, int, int]], moving_monsters: list[str] = None):
        for monster, area in monsters.items():
            monster_x = random.randrange((area[0] // 2) * 2 + 1, (area[2] // 2) * 2 + 2, 2)
            monster_y = random.randrange((area[1] // 2) * 2 + 1, (area[3] // 2) * 2 + 2, 2)
            if moving_monsters and monster in moving_monsters:
                self.monsters.append(PatrollingEnemy(monster_x, monster_y, monster))
            else:
                self.monsters.append(StationaryEnemy(monster_x, monster_y, monster))
