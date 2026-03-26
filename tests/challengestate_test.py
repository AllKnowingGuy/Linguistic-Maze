import pytest
import sys
import os
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.playstates.challengestate import *


TEST_CHALLENGE_PATH = Path('../assets/data/challenges/level_0/monster_esperanto.json')


class TestChallengeStateInit:
    """Проверки инициализации испытания"""
    def test_init_creates_challenge(self):
        challenge = ChallengeState()
        assert challenge.challenge is None
        assert challenge.score == 0
        assert challenge.submitted is False
        assert challenge.finished is False

    def test_init_has_nav_buttons(self):
        challenge = ChallengeState()
        assert challenge.back_button is not None
        assert challenge.forth_button is not None
        assert challenge.submit_button is not None

    def test_init_creates_dicts(self):
        challenge = ChallengeState()
        assert isinstance(challenge.choice_buttons_sets, dict)
        assert isinstance(challenge.input_texts, dict)

class TestSetupChallenge:
    """Проверки создания испытания"""

    def test_setup_challenge_loads_from_json(self):
        challenge = ChallengeState()
        result = challenge.setup_challenge(TEST_CHALLENGE_PATH)

        assert result is not None
        assert challenge.challenge is not None

    def test_setup_challenge_resets_data(self):
        challenge = ChallengeState()
        challenge.score = 5
        challenge.submitted = True
        challenge.current_window_ind = 10

        challenge.setup_challenge(TEST_CHALLENGE_PATH)

        assert challenge.score == 0
        assert challenge.submitted is False
        assert challenge.current_window_ind == 0

    def test_setup_challenge_resets_answers(self):
        challenge = ChallengeState()
        challenge.input_texts = {67: 'fake_answer'}
        challenge.choice_buttons_sets = {999: []}

        challenge.setup_challenge(TEST_CHALLENGE_PATH)

        assert 'fake_key' not in challenge.input_texts
        assert 999 not in challenge.choice_buttons_sets

class TestChallengeStateCard:
    """Проверки окна заданий"""
    def test_change_card_forth(self):
        challenge = ChallengeState()
        challenge.setup_challenge(TEST_CHALLENGE_PATH)
        original_ind = challenge.current_window_ind

        challenge.change_card()

        assert challenge.current_window_ind > original_ind
        assert challenge.playing_text is True
        assert challenge.text_cursor == 0

    def test_change_card_back(self):
        challenge = ChallengeState()
        challenge.setup_challenge(TEST_CHALLENGE_PATH)
        challenge.current_window_ind = 2

        challenge.change_card(back = True)

        assert challenge.current_window_ind == 1
        assert challenge.playing_text is True
        assert challenge.text_cursor == 0

    def test_forth_button_on_first_window(self):
        challenge = ChallengeState()
        challenge.setup_challenge(TEST_CHALLENGE_PATH)
        challenge.current_window_ind = 0
        challenge.get_window_fields()

        assert challenge.forth_button.state == ButtonState.REGULAR

    def test_no_back_button_on_first_window(self):
        challenge = ChallengeState()
        challenge.setup_challenge(TEST_CHALLENGE_PATH)
        challenge.current_window_ind = 0
        challenge.get_window_fields()

        assert challenge.back_button.state == ButtonState.DISABLED

class TestChallengeStateChooseFrom:
    """Проверки кнопок с выбором ответа"""
    def test_set_choosefrom_creates_buttons(self):
        challenge = ChallengeState()
        challenge.setup_challenge(TEST_CHALLENGE_PATH)

        for i in range(len(challenge.challenge.windows)):
            if challenge.challenge.get_window_action_type(i) == 'choosefrom':
                challenge.current_window_ind = i
                challenge.set_choosefrom_window()
                break
        if challenge.choice_buttons_sets:
            assert challenge.current_window_ind in challenge.choice_buttons_sets
            assert len(challenge.choice_buttons_sets[challenge.current_window_ind]) > 0

class TestChallengeStateInput:
    """Проверки ввода текста"""
    def test_input_field_updates_while_typing(self):
        challenge = ChallengeState()
        challenge.setup_challenge(TEST_CHALLENGE_PATH)

        for ind in range(len(challenge.challenge.windows)):
            if challenge.challenge.get_window_action_type(ind) == 'savetyped':
                challenge.current_window_ind = ind
                challenge.get_window_fields()
                break

        test_event = pygame.event.Event(pygame.KEYDOWN, {'unicode': 'a', 'key': pygame.K_a}) # Creating a fake 'a' button press
        challenge.input_texts[challenge.current_window_ind] = ""
        challenge.handle_input(test_event)

        assert 'a' in challenge.input_texts[challenge.current_window_ind]

    def test_input_field_updates_while_erasing(self):
        challenge = ChallengeState()
        challenge.setup_challenge(TEST_CHALLENGE_PATH)

        for ind in range(len(challenge.challenge.windows)):
            if challenge.challenge.get_window_action_type(ind) == 'savetyped':
                challenge.current_window_ind = ind
                challenge.get_window_fields()
                break

        challenge.input_texts[challenge.current_window_ind] = 'test'
        event = pygame.event.Event(pygame.KEYDOWN, {'unicode': '\x08', 'key': pygame.K_BACKSPACE})
        challenge.handle_input(event)

        assert challenge.input_texts[challenge.current_window_ind] == "tes"

class TestChallengeStateSubmit:
    """Проверки отправки ответов"""
    def test_check_save_and_submit_returns_none_when_empty(self):
        challenge = ChallengeState()
        challenge.setup_challenge(TEST_CHALLENGE_PATH)
        challenge.get_window_fields()
        for i in range(len(challenge.challenge.windows) - 1):
            challenge.change_card()
            challenge.get_window_fields()

        result = challenge.check_save_and_submit()

        assert challenge.submitted is False
        assert result is None

class TestChallengeStateMouse:
    """Проверки действий мыши"""

    def test_handle_mouse_motion_updates_button_state(self):
        challenge = ChallengeState()
        challenge.setup_challenge(TEST_CHALLENGE_PATH)
        challenge.current_window_ind = 0
        challenge.get_window_fields()

        button = challenge.forth_button
        button_x, button_y = button.x, button.y

        test_event = pygame.event.Event(pygame.MOUSEMOTION, {'pos': (button_x + 10, button_y + 10)}) # Fake mouse hovering

        challenge.handle_mouse_motion(test_event)

        assert button.state == ButtonState.HOVERED

    def test_mouse_click_changes_card(self):
        challenge = ChallengeState()
        challenge.setup_challenge(TEST_CHALLENGE_PATH)
        challenge.current_window_ind = 0
        challenge.get_window_fields()

        original_ind = 0

        button = challenge.forth_button
        button_x, button_y = button.x, button.y

        test_hover_event = pygame.event.Event(pygame.MOUSEMOTION,{'pos': (button_x + 10, button_y + 10)})  # Fake mouse hovering
        challenge.handle_mouse_motion(test_hover_event)

        # These two events create fake mouse clicking on advance button
        test_press_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                         {'button': pygame.BUTTON_LEFT, 'pos': (button_x + 10, button_y + 10)})
        test_release_event = pygame.event.Event(pygame.MOUSEBUTTONUP,
                                           {'button': pygame.BUTTON_LEFT, 'pos': (button_x + 10, button_y + 10)})

        challenge.handle_mouse_click(test_press_event)
        result = challenge.handle_mouse_release(test_release_event)

        assert challenge.current_window_ind > original_ind
        assert challenge.playing_text is True

    def test_mouse_clicks_on_choice_buttons(self):
        challenge = ChallengeState()
        challenge.setup_challenge(TEST_CHALLENGE_PATH)

        for ind in range(len(challenge.challenge.windows)):
            if challenge.challenge.get_window_action_type(ind) == 'choosefrom':
                challenge.current_window_ind = ind
                challenge.get_window_fields()
                break

        if challenge.choice_buttons_sets:
            button = challenge.choice_buttons_sets[challenge.current_window_ind][0]
            button_x, button_y = button.x, button.y
        else:
            return

        test_hover_event = pygame.event.Event(pygame.MOUSEMOTION, {'pos': (button_x, button_y)})
        challenge.handle_mouse_motion(test_hover_event)
        assert button.state == ButtonState.HOVERED

        test_press_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN,{'button': pygame.BUTTON_LEFT, 'pos': (button_x, button_y)})
        challenge.handle_mouse_click(test_press_event)

        assert button.state == ButtonState.PRESSED












