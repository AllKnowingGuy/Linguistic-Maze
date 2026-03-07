class Enemy:
    """Родительский класс для всех врагов"""

    def __init__(self, x:int, y: int, dialogue_id: str = 'enemy'):

        self.x = x
        self.y = y
        self.dialogue_id = dialogue_id
        self.active =  True

    def update(self):
        pass

    def check_collision(self, player_tile_x: int, player_tile_y: int):
        """Проверка столкновения с игроком"""
        return (self.active and self.x==player_tile_x and self.y == player_tile_y)

    def deactivate(self):
        """Исчезновение врага после выполнения его задания"""

class StationaryEnemy(Enemy):
    """Враги, стоящие на месте"""

    def __init__(self, x: int, y:int, dialogue_id: str = 'enemy_stationary'):
        super().__init__(x, y, dialogue_id)

    def update(self):
        pass

class PatrollingEnemy(Enemy):
    pass