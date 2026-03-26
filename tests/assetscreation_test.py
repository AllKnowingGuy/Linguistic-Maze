import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) # Imports weren't working unless I use this as a path - Nikita

from src.assetscreation import *
from src.util import TILE_SIZE, PLAYER_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, ButtonState, WallPattern


class TestLoadOneObject:
    """Тесты для функции load_one_object из assetscreation.py"""
    def test_load_existing_file(self):
        """Проверка загрузки существующего файла"""
        result = load_one_object(
            Path('../assets/images/maze_tiles/player/player.png'), PLAYER_SIZE, PLAYER_SIZE)
        assert result is not None
        assert isinstance(result, pygame.Surface)

    def test_load_nonexistent_file(self):
        """Проверка загрузки несуществующего файла"""
        result = load_one_object(Path('fake.png'), PLAYER_SIZE, PLAYER_SIZE)
        assert result is None


class TestLoadAllObjects:
    """Тесты для функции load_all_objects"""

    def test_load_all_objects(self):
        result = load_all_objects(Path('../assets/images/maze_tiles/level_0/walls'),
                                  {WallPattern.SINGLE: Path('wall_single.png')},
                                  {WallPattern.SINGLE: (TILE_SIZE, TILE_SIZE)})
        assert isinstance(result, dict)
        assert WallPattern.SINGLE in result


class TestMazeAssets:
    """Тесты для загрузки тайлов лабиринта"""

    def test_add_player_tile(self):
        result = add_player_tile()
        assert isinstance(result, pygame.Surface)
        assert result.get_size() == (PLAYER_SIZE, PLAYER_SIZE)

    def test_add_player_walk(self):
        result = add_player_walk()
        assert isinstance(result, list)
        assert len(result) == 4
        for frame in result:
            assert isinstance(frame, pygame.Surface)
            assert frame.get_size() == (PLAYER_SIZE, PLAYER_SIZE)

    def test_add_floor_tile(self):
        result = add_floor_tile()
        assert isinstance(result, pygame.Surface)
        assert result.get_size() == (TILE_SIZE, TILE_SIZE)

    def test_add_enemy_tile(self):
        result = add_enemy_tile()
        assert isinstance(result, pygame.Surface)
        assert result.get_size() == (TILE_SIZE, TILE_SIZE)

    def test_add_entrance_exit_tiles(self):
        entrance_tile, exit_tile = add_entrance_exit_tiles()
        assert isinstance(entrance_tile, pygame.Surface)
        assert isinstance(exit_tile, pygame.Surface)
        assert entrance_tile.get_size() == (TILE_SIZE, TILE_SIZE)
        assert exit_tile.get_size() == (TILE_SIZE, TILE_SIZE)

    def test_add_wall_tiles(self):
        result = add_wall_tiles()
        assert isinstance(result, dict)
        assert len(result) == 5
        for pattern in WallPattern:
            assert pattern in result
            assert isinstance(result[pattern], pygame.Surface)
            assert result[pattern].get_size() == (TILE_SIZE, TILE_SIZE)

class TestDialogueAssets:
    """Тесты для загрузки ресурсов диалогов"""

    def test_add_dialogue_bg(self):
        result = add_dialogue_bg()
        assert isinstance(result, pygame.Surface)
        assert result.get_size() == (SCREEN_WIDTH, SCREEN_HEIGHT)

    def test_add_dialogue_box(self):
        result = add_dialogue_box()
        assert isinstance(result, pygame.Surface)
        assert result.get_size() == (SCREEN_WIDTH, SCREEN_HEIGHT // 2)

    def test_add_left_speaking_sprite(self):
        result = add_left_speak_sprite()
        assert isinstance(result, pygame.Surface)
        assert result.get_size() == (300, 300)

    def test_add_right_speaking_sprite(self):
        result = add_right_speak_sprite()
        assert isinstance(result, pygame.Surface)
        assert result.get_size() == (300, 300)

    def test_add_dialogue_choice_buttons(self):
        result = add_dialogue_choice_buttons()
        assert isinstance(result, dict)
        for state in [ButtonState.REGULAR, ButtonState.HOVERED, ButtonState.PRESSED]:
            assert state in result
            assert isinstance(result[state], pygame.Surface)


class TestMenuAssets:
    """Тесты для загрузки ресурсов меню"""

    def test_add_menu_bg(self):
        result = add_menu_bg()
        assert isinstance(result, pygame.Surface)
        assert result.get_size() == (SCREEN_WIDTH, SCREEN_HEIGHT)

    def test_add_start_buttons(self):
        result = add_start_buttons()
        assert isinstance(result, dict)
        for state in [ButtonState.REGULAR, ButtonState.HOVERED, ButtonState.PRESSED]:
            assert state in result
            assert isinstance(result[state], pygame.Surface)

    def test_add_bind_buttons(self):
        result = add_bind_buttons('move_up')
        assert isinstance(result, dict)
        for state in [ButtonState.REGULAR, ButtonState.HOVERED, ButtonState.PRESSED]:
            assert state in result
            assert isinstance(result[state], pygame.Surface)


class TestChallengeAssets:
    """Тесты для загрузки ресурсов челленжей"""

    def test_add_challenge_bg(self):
        result = add_challenge_bg()
        assert isinstance(result, pygame.Surface)
        assert result.get_size() == (SCREEN_WIDTH, SCREEN_HEIGHT)

    def test_add_question_card(self):
        result = add_question_card()
        assert isinstance(result, pygame.Surface)
        assert result.get_size() == (QUESTION_CARD_WIDTH, QUESTION_CARD_HEIGHT)

    def test_add_challenge_choice_buttons(self):
        result = add_challenge_choice_buttons()
        assert isinstance(result, dict)
        for state in [ButtonState.REGULAR, ButtonState.HOVERED, ButtonState.PRESSED]:
            assert state in result
            assert isinstance(result[state], pygame.Surface)

    def test_add_back_buttons(self):
        result = add_back_buttons()
        assert isinstance(result, dict)

    def test_add_forth_buttons(self):
        result = add_forth_buttons()
        assert isinstance(result, dict)

    def test_add_submit_buttons(self):
        result = add_submit_buttons()
        assert isinstance(result, dict)

    def test_add_judgement_stamps(self):
        correct, incorrect = add_judgement_stamps()
        assert isinstance(correct, pygame.Surface)
        assert isinstance(incorrect, pygame.Surface)

    def test_add_tip_card(self):
        result = add_tip_card()
        assert isinstance(result, pygame.Surface)

    def test_add_transitions(self):
        start, check, end = add_transitions()
        assert isinstance(start, pygame.Surface)
        assert isinstance(check, pygame.Surface)
        assert isinstance(end, pygame.Surface)


class TestTransformer:
    """Тесты для трансформера"""

    def test_get_flipped_returns_surface(self):
        transformer = Transformer()
        test_surface = pygame.Surface((50, 50))

        result = transformer.get_flipped(test_surface, flip_x=True, flip_y=True)
        assert isinstance(result, pygame.Surface)
        assert result.get_size() == (50, 50)

    def test_get_flipped_caches(self):
        transformer = Transformer()
        test_surface = pygame.Surface((50, 50))

        result1 = transformer.get_flipped(test_surface, flip_x=True)
        result2 = transformer.get_flipped(test_surface, flip_x=True)

        assert result1 is result2

    def test_get_rotated_returns_surface(self):
        transformer = Transformer()
        test_surface = pygame.Surface((50, 50))

        result = transformer.get_rotated(test_surface, 90)
        assert isinstance(result, pygame.Surface)

    def test_get_rotated_caches(self):
        transformer = Transformer()
        test_surface = pygame.Surface((50, 50))

        result1 = transformer.get_rotated(test_surface, 90)
        result2 = transformer.get_rotated(test_surface, 90)

        assert result1 is result2



