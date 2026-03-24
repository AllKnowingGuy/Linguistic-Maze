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
    pass
