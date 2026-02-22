import pygame
from enum import Enum

from src import AssetsCreation
from src.levelBuilding import Dialogue
from src.Util import SCREEN_WIDTH, SCREEN_HEIGHT, Command
from src.playstates.BaseState import BaseState


# Константы
PLAYING_FPS = 60 # требуется для быстрого отображения диалога
PHRASE_END_HOLD = 150 # задержка после конца фразы
SENTENCE_END_HOLD = 350 # задержка после конца предложения


class Awaiting(Enum):
    CONTINUE = 1
    CHOOSE = 2
    INPUT = 3


class Speaker(Enum):
    NO_ONE = 1
    LEFT = 2
    RIGHT = 3


# Code that might be too useful to remove - Vsevolod
"""
# Поле ввода
input_rect = pygame.Rect(30, SCREEN_HEIGHT // 2 + 30, 140, 32)
text_surface = base_font.render(user_text, True, (255, 255, 255))
"""

"""
stopped = False
user_text = ''
while not stopped:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            # Check for backspace
            if event.key == pygame.K_BACKSPACE:
                user_text = user_text[:-1]
            # Check for enter
            elif event.key == pygame.K_RETURN:
                stopped = True
            # Unicode standard is used for string formation
            else:
                user_text += event.unicode
        draw()
return user_text
"""


class DialogueState(BaseState):
    dialogue: Dialogue.Dialogue
    current_line: int
    playing_line: bool = False
    line_cursor: int
    cursor_sym: str

    def __init__(self):
        """Загрузка изображений для отрисовки и создание шрифтов"""
        super().__init__()

        self.now_speaking = Speaker.NO_ONE
        self.awaiting = Awaiting.CONTINUE

        # Фон диалога
        self.dialogue_bg = AssetsCreation.load_dialogue_bg()

        # Плашка диалога
        self.dialogue_box = AssetsCreation.load_dialogue_box()

        # Игрок
        self.left_speaker = AssetsCreation.load_player_speak_sprite()

        # Собеседник
        self.right_speaker = AssetsCreation.load_character_speak_sprite()

        # Шрифт диалога
        # TODO: it's probably better to create this in Main where Pygame is initiated
        self.dialogue_font = pygame.font.Font(None, 35)

    def setup_dialogue(self, lines: list[str], character: str = 'foobar', starts_challenge: str = None):
        self.dialogue = Dialogue.Dialogue(lines, character, starts_challenge)
        self.current_line = 0
        self.playing_line = True # Когда диалог создаётся, то можно сразу начинать его выводить
        self.line_cursor = 0
        self.cursor_sym = ''

    # TODO: the following functions are obsolete and are being reworked

    def input_line(self):  # TODO: implement graphic module inputting
        return input()

    def get_line(self):
        char, action, real_text = self.dialogue.lines[self.current_line].split('\t')
        if char == 'left':
            self.now_speaking = Speaker.LEFT
            # self.output_line('Студент: ')
            # pygame.time.wait(SENTENCE_END_HOLD)
        elif char == 'right':
            self.now_speaking = Speaker.RIGHT
            # self.output_line(self.dialogue.character + ': ')
            # pygame.time.wait(SENTENCE_END_HOLD)
        elif char == 'nochar':
            self.now_speaking = Speaker.NO_ONE
        else:
            raise ValueError('Invalid dialogue format or this character cannot be processed')
        # self.output_line(real_text)

        if action == 'savetyped':
            self.awaiting = Awaiting.INPUT
            # our_answer = self.input_line()
            # while not len(our_answer.strip()):
            #     self.output_line('Пожалуйста, введите что-нибудь внятное: ')
            #     our_answer = self.input_line()
            # self.dialogue.choice_dict[real_text] = our_answer #TODO: better save naming

        elif action[:10] == 'choosefrom' and action[10] == '{' and action[-1] == '}':
            choices = action[11:-1].split(', ')
            self.awaiting = Awaiting.CHOOSE
            # self.output_line('\n')
            # for chid, choice in enumerate(choices):
            #     self.output_line(str(chid + 1) + ': ' + choice + '\n')
            # our_choice = ''
            # while not our_choice.isdigit(): #TODO: check if the digit is no larger than the number of choices
            #     self.output_line('Пожалуйста, введите цифру ответа: ')
            #     our_choice = self.input_line()
            # self.dialogue.choice_dict[real_text] = our_choice #TODO: better save naming

        else:
            self.awaiting = Awaiting.CONTINUE
            # self.input_line()

        # return self.dialogue.choice_dict

    """
    Переписанные функции состояния
    """

    def handle_input(self, keys):
        """Обработка ввода с клавиатуры и нажатия Enter для продолжения"""

        if not self.playing_line and keys[pygame.K_RETURN]:
            self.current_line += 1
            self.playing_line = True
            self.line_cursor = 0

    def draw(self, screen):
        """Отрисовка диалога"""

        screen.blit(self.dialogue_bg, (0, 0))

        who_speaks = self.dialogue.get_line_speaker(self.current_line)
        if who_speaks:
            if who_speaks == 'left': # TODO: maybe check this earlier and assign to a parameter
                screen.blit(self.left_speaker, (100, 50))
            elif who_speaks == 'right':
                screen.blit(self.right_speaker, (SCREEN_WIDTH - 100 - self.right_speaker.get_width(), 50))

        screen.blit(self.dialogue_box, (0, SCREEN_HEIGHT // 2)) # плашка должна быть поверх участников диалога
        to_print = self.dialogue.get_line_text(self.current_line)
        if to_print:
            self.draw_text_by_letter(to_print, screen)

    def execute_after_draw(self):
        if self.playing_line:
            # TODO: try avoiding usage of time.wait
            if self.cursor_sym in '.?!':
                return Command.WAIT, SENTENCE_END_HOLD
            elif self.cursor_sym in ':;': # i thought it would look fine with commas - Vsevolod
                return Command.WAIT, PHRASE_END_HOLD
            else:
                return Command.SET_FPS, PLAYING_FPS
        else:
            return Command.SET_FPS, 10

    """
    Вспомогательные функции для отрисовки
    """

    def draw_text_by_letter(self, text, screen):
        if self.line_cursor == len(text):
            self.playing_line = False
        else:
            # TODO: found nowhere better to extract the latest symbol, but maybe I should
            self.cursor_sym = text[self.line_cursor]
            self.line_cursor += 1

        text_sprite = self.dialogue_font.render(text[:self.line_cursor], True, (0, 0, 0))
        screen.blit(text_sprite, (100, SCREEN_HEIGHT // 2 + 100))
