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
CHOICE_BUTTON_DIST = CHOICE_BUTTON_SIZE + 10 # расстояние между кнопками выбора


class Awaiting(Enum):
    CONTINUE = 1
    CHOOSE = 2
    INPUT = 3


class Speaker(Enum):
    NO_ONE = 1
    LEFT = 2
    RIGHT = 3


class DialogueState(BaseState):
    dialogue: Dialogue.Dialogue
    finished: bool

    current_line_ind: int
    current_line: str
    now_speaking: Speaker
    awaiting: Awaiting

    playing_line: bool = False
    line_cursor: int
    cursor_sym: str

    current_choice_options: list
    choice_button_states: list

    def __init__(self):
        """Задание некоторых атрибутов, загрузка изображений для отрисовки и создание шрифтов"""
        super().__init__()

        # Состояния кнопок
        self.choice_button_states = [] # необходимо очищать каждый раз, когда нажимаем кнопку

        # Текст поля ввода
        self.current_input_text = '' # необходимо очищать каждый раз, когда нажимаем Enter

        """Графика"""
        # Фон диалога
        self.dialogue_bg = AssetsCreation.add_dialogue_bg()

        # Плашка диалога
        self.dialogue_box = AssetsCreation.add_dialogue_box()

        # Студент
        self.left_speaker = AssetsCreation.add_player_speak_sprite()

        # Собеседник
        self.right_speaker = AssetsCreation.add_character_speak_sprite()

        # Кнопки выбора
        self.choice_buttons = AssetsCreation.add_choice_buttons()

        # Шрифт диалога
        # TODO: it's probably better to create this in Main where Pygame is initiated
        self.dialogue_font = pygame.font.Font(None, 35)

    def setup_dialogue(self, lines: list[str], character: str = 'foobar', starts_challenge: str = None):
        """Задание структурных данных диалога, сброс параметров проигрывания"""
        # TODO: enable switching to a preloaded dialogue and specifying current line index

        self.dialogue = Dialogue.Dialogue(lines, character, starts_challenge)
        self.finished = False
        self.current_line_ind = 0
        self.get_line_fields()

        # Когда диалог создаётся, то можно сразу начинать его выводить
        self.playing_line = True
        self.line_cursor = 0
        self.cursor_sym = ''

        return self.dialogue

    def advance(self, jump_to: int = None):
        """Продвижение диалога на одну строчку или на определённую позицию"""

        if jump_to:
            self.current_line_ind = jump_to
        else:
            self.current_line_ind += 1
        self.get_line_fields()
        if not self.finished:
            self.playing_line = True
            self.line_cursor = 0

    def get_line_fields(self):
        """Получение данных из строчки диалогового файла"""

        # Когда перебрали все строчки, завершаем диалог
        if self.finished or self.current_line_ind >= len(self.dialogue.lines):
            self.finished = True
            return

        # Извлекаем данные
        char = self.dialogue.get_line_speaker(self.current_line_ind)
        action = self.dialogue.get_line_action(self.current_line_ind)
        self.current_line = self.dialogue.get_line_text(self.current_line_ind)

        # Преобразуем данные в формат, поддерживаемый DialogueState
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
        elif action[:10] == 'choosefrom' and action[10] == '{' and action[-1] == '}':
            # получаем варианты ответа и создаём список кнопок
            self.current_choice_options = action[11:-1].split(', ')
            for _ in self.current_choice_options:
                self.choice_button_states.append(ButtonType.REGULAR)
            self.awaiting = Awaiting.CHOOSE
        elif action == 'noaction':
            self.awaiting = Awaiting.CONTINUE
        else:
            raise ValueError('Invalid dialogue format or this action cannot be processed')

    """
    Переписанные функции состояния
    """

    def handle_input(self, event, pressed_keys):
        """Обработка ввода с клавиатуры и нажатия Enter для продолжения"""

        # Ограничения (диалог не завершён и не печатается, не требуется нажать на кнопку мышкой)
        if not self.finished and not self.playing_line and not self.awaiting.name == Awaiting.CHOOSE.name:
            # Нажатие пробела
            if event.key == pygame.K_RETURN:
                if self.awaiting.name == Awaiting.INPUT.name:
                    self.dialogue.saved_inputs[self.current_line] = self.current_input_text
                    self.current_input_text = ''
                self.advance()
                return (Command.CHECK_PROGRESS, None),

            # Нажатие других кнопок (когда есть поле ввода)
            elif self.awaiting.name == Awaiting.INPUT.name:
                if event.key == pygame.K_BACKSPACE:
                    self.current_input_text = self.current_input_text[:-1]
                else:
                    self.current_input_text = self.current_input_text + event.unicode

        return None # bruuuh - Vsevolod

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

        if not self.playing_line and self.awaiting.name == Awaiting.CHOOSE.name:
            for b_ind, b_state in enumerate(self.choice_button_states):
                if pressed_buttons[0] and b_state == ButtonType.HOVERED:
                    # TODO: rework to not press the button by running into it with LMB pressed
                    self.choice_button_states[b_ind] = ButtonType.PRESSED
                    self.dialogue.saved_choices[self.current_line] = self.current_choice_options[b_ind]
                    self.advance()
                    self.choice_button_states.clear() # TODO: clear later to let button press animation play
                    return (Command.CHECK_PROGRESS, None),
        return None

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
                # TODO: make this a separate function and add multi-column placement if more than 3 buttons
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
                # TODO: make BG for input field?
                input_text_sprite = self.dialogue_font.render(' - Ввод: ' + self.current_input_text, True, (0, 0, 0))
                screen.blit(input_text_sprite, (TEXT_X, TEXT_Y + 100))

    def execute_after_draw(self):
        """Регулировка скорости печатания и пауз по аналогии с паузами в речи"""
        # TODO: what if we put special symbols in the dialogue that won't be printed but will change talking speed?

        if self.playing_line:
            # TODO: try avoiding time.wait
            if self.cursor_sym in '.?!':
                return (Command.WAIT, SENTENCE_END_HOLD),
            elif self.cursor_sym in ':;':
                return (Command.WAIT, PHRASE_END_HOLD),
        return None

    """
    Вспомогательные функции для отрисовки
    """

    def draw_text_by_letter(self, screen):
        """Приятный глазу эффект выведения текста по буковке"""

        if self.line_cursor == len(self.current_line):
            self.playing_line = False
        else:
            # TODO: couldn't find anywhere better to extract the latest symbol, but maybe I should
            self.cursor_sym = self.current_line[self.line_cursor]
            self.line_cursor += 1

        text_sprite = self.dialogue_font.render(self.current_line[:self.line_cursor], True, (0, 0, 0))
        screen.blit(text_sprite, (TEXT_X, TEXT_Y))
