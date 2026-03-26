import pytest
import sys
import os
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.playstates.mazestate import *
from src.level_building.enemy import Enemy
from src.util import Border, TILE_SIZE, PLAYER_SIZE


TEST_MONSTER_DATA = {"monster_esperanto": (1, 1, 1, 1)}


class TestMazeStateInit:
    """Проверки инициализации MazeState"""
    def test_creates_maze(self):
        maze = MazeState()
        assert maze is not None
        assert maze.maze is None

    def test_sets_default_player_pos(self):
        maze = MazeState()
        assert maze.player_pos == [int(1.5 * TILE_SIZE), int(1.5 * TILE_SIZE)]


class TestSetupMaze:
    """Проверки создания лабиринта"""
    def test_setup_maze(self):
        maze = MazeState()
        result = maze.setup_maze(width=5, height=5)

        assert result is not None
        assert result.height == 5
        assert result.width == 5

    def test_creates_enemies(self):
        maze = MazeState()
        maze.setup_maze(monster_dict=TEST_MONSTER_DATA)

        assert len(maze.maze.monsters) > 0
        assert isinstance(maze.maze.monsters[0], Enemy)

    def test_sets_player(self):
        maze = MazeState()
        maze.setup_maze()

        assert maze.player_pos[0] > 0
        assert maze.player_pos[1] > 0


class TestMazeStateEnemies:
    """Проверки врагов"""

    def test_check_enemy_collision_none(self):
        maze = MazeState()
        maze.setup_maze()

        maze.player_pos = [0,0]

        result = maze.check_enemy_collision()
        assert result is None

    def test_check_enemy_collision(self):
        maze = MazeState()
        maze.setup_maze(monster_dict=TEST_MONSTER_DATA)

        if maze.maze.monsters:
            enemy = maze.maze.monsters[0]
            maze.player_pos = [enemy.x * TILE_SIZE, enemy.y * TILE_SIZE]

            result = maze.check_enemy_collision()

            assert result is not None
            assert result.x == enemy.x
            assert result.y == enemy.y

    def test_enemy_in_correct_pos(self):
        maze = MazeState()
        maze.setup_maze(monster_dict=TEST_MONSTER_DATA)

        if maze.maze.monsters:
            enemy = maze.maze.monsters[0]
            assert 0 <= enemy.x < maze.maze.width
            assert 0 <= enemy.y < maze.maze.height


class TestMazeStateAnimations:
    """Проверка работы анимаций"""

    def test_update_animation_when_not_moving(self):
        maze = MazeState()
        maze.setup_maze()
        maze.is_moving = False
        start_image = maze.current_player_image

        maze.update_animation()

        assert maze.current_player_image == start_image

    def test_update_animation_changes_when_moving(self):
        maze = MazeState()
        maze.setup_maze()
        maze.is_moving = True
        start_image = maze.current_player_image

        with patch('pygame.time.get_ticks') as mock_time:
            mock_time.return_value = 1000
            maze.last_animation_time = 0
            maze.animation_speed = 100

            maze.update_animation()

            assert maze.current_player_image != start_image


class TestMazeStateMovement:
    """Проверки движения игрока"""

    @patch('pygame.key.get_pressed')
    def test_moves_left(self, mock_keys):
        maze = MazeState()
        maze.setup_maze(width=50, height=50)
        original_x = maze.player_pos[0]

        up_bind, down_bind, left_bind, right_bind = Config().get_maze_controls()

        pressed = {
            pygame.K_LEFT: 1,
            pygame.K_RIGHT: 0,
            pygame.K_UP: 0,
            pygame.K_DOWN: 0,
            left_bind: 0,
            right_bind: 0,
            up_bind: 0,
            down_bind: 0
        }
        mock_keys.return_value = pressed

        maze.handle_hold_input(mock_keys.return_value)

        assert maze.player_pos[0] < original_x
        assert maze.facing_left is True
        assert maze.is_moving is True

    @patch('pygame.key.get_pressed')
    def test_moves_up(self, mock_keys):
        maze = MazeState()
        maze.setup_maze(width=50, height=50)
        original_y = maze.player_pos[1]

        up_bind, down_bind, left_bind, right_bind = Config().get_maze_controls()

        pressed = {
            pygame.K_LEFT: 0,
            pygame.K_RIGHT: 0,
            pygame.K_UP: 1,
            pygame.K_DOWN: 0,
            left_bind: 0,
            right_bind: 0,
            up_bind: 0,
            down_bind: 0
        }
        mock_keys.return_value = pressed

        maze.handle_hold_input(mock_keys.return_value)

        assert maze.player_pos[1] < original_y
        assert maze.is_moving is True


class TestMazeStateWin:
    """Проверки победы"""

    def test_check_win_returns_none_when_no_win(self):
        maze = MazeState()
        maze.setup_maze()

        assert maze.check_win() is False