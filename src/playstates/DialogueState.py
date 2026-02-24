import pygame
from enum import Enum

from src import AssetsCreation
from src.levelBuilding import Dialogue
from src.Util import SCREEN_WIDTH, SCREEN_HEIGHT, CHOICE_BUTTON_SIZE, Command, ButtonType
from src.playstates.BaseState import BaseState


# Константы
PLAYING_FPS = 60 # требуется для быстрого отображения диалога
PHRASE_END_HOLD = 150 # задержка после конца фразы
SENTENCE_END_HOLD = 350 # задержка после конца предложения

TEXT_X = 100
TEXT_Y = SCREEN_HEIGHT // 2 + 100
CHOICE_BUTTON_X = 100
CHOICE_BUTTON_Y = SCREEN_HEIGHT // 2 + 160
CHOICE_BUTTON_DIST = CHOICE_BUTTON_SIZE + 10


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
    current_line_ind: int
    playing_line: bool = False
    line_cursor: int
    cursor_sym: str

    def __init__(self):
        """Загрузка изображений для отрисовки и создание шрифтов"""
        super().__init__()

        # Атрибуты, меняющиеся с каждой строчкой диалогового файла
        self.finished = False

        self.now_speaking = Speaker.NO_ONE
        self.awaiting = Awaiting.CONTINUE
        self.current_line = ''

        self.current_choice_options = []
        self.choice_button_states = [] # необходимо очищать каждый раз, когда нажимается кнопка

        self.current_input_text = ''

        # Фон диалога
        self.dialogue_bg = AssetsCreation.add_dialogue_bg()

        # Плашка диалога
        self.dialogue_box = AssetsCreation.add_dialogue_box()

        # Игрок
        self.left_speaker = AssetsCreation.add_player_speak_sprite()

        # Собеседник
        self.right_speaker = AssetsCreation.add_character_speak_sprite()

        # Кнопки выбора
        self.choice_buttons = AssetsCreation.add_choice_buttons()

        # Шрифт диалога
        # TODO: it's probably better to create this in Main where Pygame is initiated
        self.dialogue_font = pygame.font.Font(None, 35)

    def setup_dialogue(self, lines: list[str], character: str = 'foobar', starts_challenge: str = None):
        self.dialogue = Dialogue.Dialogue(lines, character, starts_challenge)
        self.finished = False
        self.current_line_ind = 0
        self.get_line_fields()

        # Когда диалог создаётся, то можно сразу начинать его выводить
        self.playing_line = True
        self.line_cursor = 0
        self.cursor_sym = ''

    def advance(self, jump_to: int = None):
        if jump_to:
            self.current_line_ind = jump_to
        else:
            self.current_line_ind += 1
        self.get_line_fields()
        if not self.finished:
            self.playing_line = True
            self.line_cursor = 0

    def get_line_fields(self):
        if self.finished or self.current_line_ind >= len(self.dialogue.lines):
            self.finished = True
            return

        char = self.dialogue.get_line_speaker(self.current_line_ind)
        action = self.dialogue.get_line_action(self.current_line_ind)
        self.current_line = self.dialogue.get_line_text(self.current_line_ind)

        if char == 'left':
            self.now_speaking = Speaker.LEFT
        elif char == 'right':
            self.now_speaking = Speaker.RIGHT
        elif char == 'nochar':
            self.now_speaking = Speaker.NO_ONE
        else:
            raise ValueError('Invalid dialogue format or this character cannot be processed')

        if action == 'savetyped':
            self.awaiting = Awaiting.INPUT
            # our_answer = self.input_line()
            # while not len(our_answer.strip()):
            #     self.output_line('Пожалуйста, введите что-нибудь внятное: ')
            #     our_answer = self.input_line()
            # self.dialogue.choice_dict[real_text] = our_answer #TODO: better save naming

        elif action[:10] == 'choosefrom' and action[10] == '{' and action[-1] == '}':
            self.current_choice_options = action[11:-1].split(', ')
            for _ in self.current_choice_options:
                self.choice_button_states.append(ButtonType.REGULAR)
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

    """
    Переписанные функции состояния
    """

    def handle_input(self, event, pressed_keys):
        """Обработка ввода с клавиатуры и нажатия Enter для продолжения"""

        if not self.finished and not self.playing_line and not self.awaiting.name == Awaiting.CHOOSE.name:
            if event.key == pygame.K_RETURN:
                self.advance()
                # TODO: implement input saving in input mode
            elif self.awaiting.name == Awaiting.INPUT.name:
                if event.key == pygame.K_BACKSPACE:
                    self.current_input_text = self.current_input_text[:-1]
                else:
                    self.current_input_text = self.current_input_text + event.unicode

    def handle_mouse_motion(self, mouse_pos):
        """Обработка наведения курсора на кнопки выбора"""

        if not self.playing_line and self.awaiting.name == Awaiting.CHOOSE.name:
            for b_ind, b_state in enumerate(self.choice_button_states):
                real_y = CHOICE_BUTTON_Y + CHOICE_BUTTON_DIST * b_ind

                if (CHOICE_BUTTON_X <= mouse_pos[0] <= CHOICE_BUTTON_X + CHOICE_BUTTON_SIZE
                         and real_y <= mouse_pos[1] <= real_y + CHOICE_BUTTON_SIZE):
                    # Когда курсор поверх кнопки - подсвечиваем
                    self.choice_button_states[b_ind] = ButtonType.HOVERED
                else:
                    # Когда убираем курсор - убираем подсветку
                    self.choice_button_states[b_ind] = ButtonType.REGULAR

    def handle_mouse_click(self, pressed_buttons):
        """Обработка нажатия на кнопки выбора"""

        for b_ind, b_state in enumerate(self.choice_button_states):
            if pressed_buttons[0] and b_state == ButtonType.HOVERED:
                # TODO: rework to not press the button by running into it with LMB pressed
                # self.choice_button_states[b_ind] = ButtonType.PRESSED
                self.advance()  # TODO: implement choice saving
                self.choice_button_states.clear()

    def draw(self, screen):
        """Отрисовка диалога"""

        # Создаём фон
        screen.blit(self.dialogue_bg, (0, 0))

        # Отрисовываем участников диалога
        if self.now_speaking == Speaker.LEFT:
            screen.blit(self.left_speaker, (100, 50))
        elif self.now_speaking == Speaker.RIGHT:
            screen.blit(self.right_speaker, (SCREEN_WIDTH - 100 - self.right_speaker.get_width(), 50))

        # Отрисовываем плашку диалога (поверх участников!)
        screen.blit(self.dialogue_box, (0, SCREEN_HEIGHT // 2))

        # Отрисовываем текст
        self.draw_text_by_letter(screen)

        # Отрисовываем, когда персонаж прекращает "говорить"
        if not self.playing_line:

            # Отрисовываем кнопки выбора (если они есть)
            if self.awaiting.name == Awaiting.CHOOSE.name:
                for b_ind in range(len(self.current_choice_options)):

                    # Сами кнопки
                    screen.blit(self.choice_buttons[self.choice_button_states[b_ind]],
                                (CHOICE_BUTTON_X, CHOICE_BUTTON_Y + CHOICE_BUTTON_DIST * b_ind))

                    # Текст кнопок
                    input_text_sprite = self.dialogue_font.render(self.current_choice_options[b_ind], True, (0, 0, 0))
                    screen.blit(input_text_sprite,
                                (CHOICE_BUTTON_X + CHOICE_BUTTON_DIST, CHOICE_BUTTON_Y + CHOICE_BUTTON_DIST * b_ind))

            # Отрисовываем вводимый текст (если можно вводить)
            if self.awaiting.name == Awaiting.INPUT.name:
                input_text_sprite = self.dialogue_font.render(' - ' + self.current_input_text, True, (0, 0, 0))
                screen.blit(input_text_sprite, (TEXT_X, TEXT_Y + 100))

    def execute_after_draw(self):
        """Регулировка скорости печатания и пауз по аналогии с паузами в речи"""
        # TODO: what if we put special symbols in the dialogue that won't be printed but will change talking speed?
        if self.playing_line:
            # TODO: try avoiding time.wait
            if self.cursor_sym in '.?!':
                return Command.WAIT, SENTENCE_END_HOLD
            elif self.cursor_sym in ':;': # i thought it would look fine with commas - Vsevolod
                return Command.WAIT, PHRASE_END_HOLD
        return None

    """
    Вспомогательные функции для отрисовки
    """

    def draw_text_by_letter(self, screen):
        if self.line_cursor == len(self.current_line):
            self.playing_line = False
        else:
            # TODO: couldn't find anywhere better to extract the latest symbol, but maybe I should
            self.cursor_sym = self.current_line[self.line_cursor]
            self.line_cursor += 1

        text_sprite = self.dialogue_font.render(self.current_line[:self.line_cursor], True, (0, 0, 0))
        screen.blit(text_sprite, (TEXT_X, TEXT_Y))
