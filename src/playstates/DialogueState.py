import pygame
from enum import Enum
from math import ceil

from src import AssetsCreation
from src.Config import Config
from src.levelBuilding import Dialogue
from src.levelBuilding.Button import Button
from src.Util import SCREEN_WIDTH, SCREEN_HEIGHT, CHOICE_BUTTON_SIZE, Command, ButtonState, Awaiting
from src.playstates.BaseState import BaseState

# Константы
TEXT_X = 100
TEXT_Y = SCREEN_HEIGHT // 2 + 100
CHOICE_BUTTON_X = 100
CHOICE_BUTTON_Y = SCREEN_HEIGHT // 2 + 160
CHOICE_BUTTON_DIST_X = CHOICE_BUTTON_SIZE + 490  # расстояние между кнопками выбора по горизонтали
CHOICE_BUTTON_DIST_Y = CHOICE_BUTTON_SIZE + 10  # расстояние между кнопками выбора по вертикали


class Speaker(Enum):
    NO_ONE = 1
    LEFT = 2
    RIGHT = 3


class DialogueState(BaseState):
    dialogue: Dialogue.Dialogue | None
    finished: bool

    current_line_ind: int
    current_line: str
    current_line_jump: int | None

    now_speaking: Speaker
    awaiting: Awaiting
    current_bg: pygame.Surface | None

    playing_line: bool = False
    line_cursor: int

    choice_buttons: list[Button]
    choice_jumps: list[int | None]

    def __init__(self):
        """Задание некоторых атрибутов, загрузка изображений для отрисовки и создание шрифтов"""
        super().__init__()

        """Параметры по умолчанию"""
        self.dialogue = None

        self.finished = False
        self.trying_to_finish = False
        self.current_line_ind = 0

        # Данные текущей строчки
        self.current_line = ''
        self.now_speaking = Speaker.NO_ONE
        self.awaiting = Awaiting.CONTINUE
        self.current_line_jump = None

        # Данные анимации текста
        self.playing_line = True
        self.line_cursor = 0

        # Кнопки выбора
        self.choice_buttons = []  # необходимо очищать каждый раз, когда нажимаем кнопку
        self.choice_jumps = []

        # Текст поля ввода
        self.current_input_text = ''  # необходимо очищать каждый раз, когда нажимаем Enter

        """Управление"""
        self.stop_anim_bind, self.advance_bind = Config().get_dialogue_controls()

        """Графика"""
        # Базовый фон диалога
        self.base_dialogue_bg = AssetsCreation.add_dialogue_bg()
        self.current_bg = None

        # Фон-скриншот предыдущего кадра
        self.need_screenshot = False
        self.screenshot_bg = None
        self.ssbg_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.ssbg_overlay.set_alpha(64)
        self.ssbg_overlay.fill((0, 0, 0))

        # Плашка диалога
        self.dialogue_box = AssetsCreation.add_dialogue_box()

        # Студент
        self.left_speaker = AssetsCreation.add_left_speak_sprite()
        # TODO: don't load if the left speaker never speaks

        # Собеседник
        self.right_speaker = None

        # Спрайты кнопок выбора
        self.choice_button_sprites = AssetsCreation.add_dialogue_choice_buttons()

        # Шрифт диалога и выводимые тексты
        self.dialogue_font = pygame.font.Font(None, 35)
        self.current_line_sprite = None
        self.left_speaker_name_sprite = None
        self.right_speaker_name_sprite = None
        self.input_text_sprite = None
        self.button_text_sprites = []
        self.prepare_text = self.dialogue_font.render('Приготовьтесь...', True, (0, 0, 0))

        # Кеш редко меняющегося содержимого дисплея
        self.need_cache = False
        self.bg_chars_box_cache = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

        """Музыка"""
        self.start_music_time = 0

    def setup_dialogue(self, json_path: str):
        """Задание структурных данных диалога, сброс параметров проигрывания"""

        self.dialogue = Dialogue.Dialogue(json_path)
        self.finished = False
        self.current_line_ind = 0

        # Очистка кнопок выбора и поля ввода
        self.choice_buttons = []
        self.choice_jumps = []
        self.current_input_text = ''

        # Установка базового заднего фона (может быть изменён по мере прочтения строчек)
        self.current_bg = self.base_dialogue_bg

        # Получение данных первой строчки
        self.get_line_fields()

        # Создание именных плашек говорящих
        self.left_speaker_name_sprite = self.dialogue_font.render(self.dialogue.left_character, True, (0, 0, 0))
        self.right_speaker_name_sprite = self.dialogue_font.render(self.dialogue.right_character, True, (0, 0, 0))

        # Установка спрайта собеседника (если указан в файле диалога и если собеседник вообще есть)
        if self.dialogue.right_character_path:
            self.right_speaker = AssetsCreation.add_right_speak_sprite(self.dialogue.right_character_path)
        elif self.dialogue.right_character:
            self.right_speaker = AssetsCreation.add_right_speak_sprite()

        # Данные анимации текста
        self.line_cursor = 10 ** 10  # чтобы анимация не играла, пока диалог ещё не показывается

        # Если диалог зловещий - ставим музыку монстра, иначе музыку из файла диалога, если она указана
        if self.dialogue.ominous:
            AssetsCreation.set_dialogue_music('Monster.wav')
        elif self.dialogue.music_path:
            AssetsCreation.set_dialogue_music(self.dialogue.music_path)

        # Запрос на обновление экрана
        self.need_screen_update = True

        return self.dialogue

    def start_playing(self):
        self.playing_line = True
        self.line_cursor = 0

        # Ставим музыку диалога
        if self.dialogue.ominous or self.dialogue.music_path:  # временно за неимением лучшего
            pygame.mixer.music.play(-1)
            self.start_music_time = pygame.time.get_ticks()

    def advance(self, jump_to: int = None):
        """Продвижение диалога на одну строчку или на определённую позицию"""

        if jump_to:
            if jump_to == -1:
                self.trying_to_finish = True
                self.need_screen_update = True
                return
            self.current_line_ind = jump_to
        else:
            self.current_line_ind += 1
        self.get_line_fields()

        if not self.finished and not self.trying_to_finish:
            self.playing_line = True
            self.line_cursor = 0

        self.need_screen_update = True

    def get_line_fields(self):
        """Получение данных из строчки диалогового файла"""

        # Если диалог завершён - не пытаемся извлечь данные
        if self.finished or self.trying_to_finish:
            return

        # Когда перебрали все строчки, завершаем диалог
        elif self.current_line_ind >= len(self.dialogue.lines):
            self.current_line_ind = len(self.dialogue.lines) - 1
            self.trying_to_finish = True
            return

        # Извлекаем текст
        self.current_line = self.dialogue.get_line_text(self.current_line_ind)

        # Извлекаем метаданные
        self.current_line_jump = self.dialogue.get_line_jump(self.current_line_ind)

        side = self.dialogue.get_line_speaker(self.current_line_ind)
        action_type = self.dialogue.get_line_action_type(self.current_line_ind)
        new_bg = self.dialogue.get_line_bgswitch(self.current_line_ind)

        # Преобразуем данные в формат, поддерживаемый DialogueState

        # Если линию произносит один из участников
        if side:
            if side == 'left':
                self.now_speaking = Speaker.LEFT
            elif side == 'right':
                self.now_speaking = Speaker.RIGHT
            else:
                raise ValueError(f'This side cannot be processed: {side}')
        else:
            self.now_speaking = Speaker.NO_ONE

        # Если строчка требует действия от игрока
        if action_type:
            # Если нужно ввести текст
            if action_type == 'savetyped':
                self.awaiting = Awaiting.INPUT
                self.input_text_sprite = self.dialogue_font.render(' - Ввод: ', True, (0, 0, 0))
            # Если нужно нажать на кнопку
            elif action_type == 'choosefrom':
                self.awaiting = Awaiting.CHOOSE
                self.set_choosefrom_line()
            else:
                raise ValueError(f'This action cannot be processed: {action_type}')
        else:
            self.awaiting = Awaiting.CONTINUE

        # Если строчка меняет задний фон
        if new_bg:
            #self.current_bg.set_alpha(255)

            # Фон-скриншот
            if new_bg == 'PREVSCREEN':
                self.need_screenshot = True

            # Загружаемый фон
            else:
                newly_loaded_bg = AssetsCreation.add_dialogue_bg(new_bg)
                if newly_loaded_bg:
                    self.current_bg = newly_loaded_bg
                else:
                    # Если не получилось загрузить фон диалога - ставим стандартный
                    self.current_bg = self.base_dialogue_bg

        # Запрашиваем обновление редко меняющихся элементов экрана
        self.need_cache = True

    def set_choosefrom_line(self):
        # Получаем варианты ответа и создаём список кнопок
        current_choice_options = self.dialogue.get_line_choose_options(self.current_line_ind)
        number_of_options = len(current_choice_options)

        # Создаём объекты кнопок, сразу указывая их расположение
        for opt_ind, opt in enumerate(current_choice_options):
            if number_of_options < 4:
                # Кнопки в один столбик
                self.choice_buttons.append(
                    Button(
                        CHOICE_BUTTON_X,
                        CHOICE_BUTTON_Y + CHOICE_BUTTON_DIST_Y * opt_ind,
                        CHOICE_BUTTON_SIZE,
                        CHOICE_BUTTON_SIZE,
                        opt)
                )
            else:
                # Кнопки в два столбика
                self.choice_buttons.append(
                    Button(
                        CHOICE_BUTTON_X + CHOICE_BUTTON_DIST_X * (opt_ind >= number_of_options / 2),
                        CHOICE_BUTTON_Y + CHOICE_BUTTON_DIST_Y * (opt_ind % ceil(number_of_options / 2)),
                        CHOICE_BUTTON_SIZE,
                        CHOICE_BUTTON_SIZE,
                        opt)
                )
            self.button_text_sprites.append(self.dialogue_font.render(opt, True, (0, 0, 0)))
            # Sorry Button text attribute, but rerendering you every time costs FPS - Vsevolod

        # Получаем индексы строчек, на которые нас перемещают определённые кнопки
        self.choice_jumps = self.dialogue.get_line_choose_jumps(self.current_line_ind)

    def finish(self):
        if self.dialogue.ominous:
            if 0 <= (pygame.time.get_ticks() - self.start_music_time) % 2000 < 5:  # FPS are imperfect - Vsevolod
                self.finished = True
                self.trying_to_finish = False
                self.need_screen_update = True
        else:
            self.finished = True
            self.trying_to_finish = False
            self.need_screen_update = True

    """
    Переписанные функции состояния
    """

    def handle_input(self, event):
        """Обработка ввода с клавиатуры и нажатия клавиш продолжения диалога и прекращения анимации"""

        # Вывод всего сообщения сразу
        if self.playing_line and event.unicode == chr(self.stop_anim_bind):
            self.line_cursor = len(self.current_line)

        # Ограничения: диалог не завершён и не печатается, не требуется нажать на кнопку мышкой
        elif (not self.finished
              and not self.trying_to_finish
              and not self.playing_line
              and not self.awaiting.name == Awaiting.CHOOSE.name):

            # Когда есть поле ввода
            if self.awaiting.name == Awaiting.INPUT.name:

                # Нажатие Enter (настройки не влияют!)
                if event.key == pygame.K_RETURN:

                    # Ограничение: не продвигаемся, если ничего не ввели или ввели только проблелы
                    if self.current_input_text.strip():
                        self.dialogue.saved_inputs[self.current_line] = self.current_input_text.strip()
                        self.current_input_text = ''
                        self.advance(self.current_line_jump)
                        return (Command.CHECK_PROGRESS, None),

                # Нажатие других кнопок
                else:
                    self.current_input_text, updated = self.update_input_field(self.current_input_text, event)
                    if updated:
                        self.input_text_sprite = self.dialogue_font.render(' - Ввод: ' + self.current_input_text,
                                                                           True,
                                                                           (0, 0, 0))

            # Когда поля ввода нет (настройки ВЛИЯЮТ)
            elif event.unicode == chr(self.advance_bind):
                self.advance(self.current_line_jump)
                return (Command.CHECK_PROGRESS, None),

        return None  # bruuuh - Vsevolod

    def handle_mouse_motion(self, event):
        """Обработка наведения курсора на кнопки выбора"""

        # Ограничения: диалог не завершён и не печатается, нужно нажать кнопку мышкой, никакая кнопка не зажата
        if (not self.finished
                and not self.trying_to_finish
                and not self.playing_line
                and self.awaiting.name == Awaiting.CHOOSE.name
                and not ButtonState.PRESSED in [btn.state for btn in self.choice_buttons]):

            for btn in self.choice_buttons:
                self.update_button_on_hovering(btn, event)

    def handle_mouse_click(self, event):
        """Обработка нажатия на кнопки выбора"""

        if not self.playing_line and self.awaiting.name == Awaiting.CHOOSE.name and event.button == pygame.BUTTON_LEFT:
            for btn in self.choice_buttons:
                if self.update_buttons_on_press(btn):
                    return

    def handle_mouse_release(self, event):
        """Обработка отпуска ЛКМ после щелчка по кнопке выбора"""

        if (not self.playing_line
                and self.awaiting.name == Awaiting.CHOOSE.name
                and event.button == pygame.BUTTON_LEFT
                and ButtonState.PRESSED in [btn.state for btn in self.choice_buttons]):

            for btn_ind, btn in enumerate(self.choice_buttons):
                if btn.is_hovered(event.pos) and btn.state == ButtonState.PRESSED:
                    # Когда курсор поверх нажатой кнопки - отпуск активирует действие
                    self.dialogue.saved_choices[self.current_line] = btn.text
                    self.advance(self.choice_jumps[btn_ind]) if self.choice_jumps else self.advance()

                    self.choice_buttons.clear()  # сбрасываем кнопки: на следующей строчке будут другие (если будут)
                    self.choice_jumps.clear()  # сбрасываем прыжки по диалогу для кнопок

                    return (Command.CHECK_PROGRESS, None),
            else:
                # Когда отпустили курсор не над нажатой кнопкой - все кнопки становятся неподсвеченными
                for btn in self.choice_buttons:
                    btn.state = ButtonState.REGULAR
            self.need_screen_update = True
        return None

    def execute_before_draw(self):
        if self.trying_to_finish:
            self.finish()
        elif self.finished:
            pygame.mixer.music.stop()
            return (Command.CHECK_PROGRESS, None),
        return None

    def draw(self, screen):
        """Отрисовка диалога"""

        # ТОЛЬКО ЕСЛИ ЧТО-ТО ИЗМЕНИЛОСЬ НА ЭКРАНЕ
        if self.need_screen_update:

            # Заново вносим кешируемые элементы, когда мы на новой строчке
            if self.need_cache:

                # Получаем скриншот предыдущего кадра, когда требуется
                if self.need_screenshot:
                    self.screenshot_bg = screen.copy()
                    self.current_bg = self.screenshot_bg
                    self.need_screenshot = False

                # Создаём фон
                self.bg_chars_box_cache.blit(self.current_bg, (0, 0))
                if self.current_bg is self.screenshot_bg:
                    self.bg_chars_box_cache.blit(self.ssbg_overlay, (0, 0))

                # Отрисовываем участников диалога
                if self.now_speaking == Speaker.LEFT:
                    self.bg_chars_box_cache.blit(self.left_speaker, (100, 100))
                    name_sprite = self.left_speaker_name_sprite
                elif self.now_speaking == Speaker.RIGHT:
                    self.bg_chars_box_cache.blit(self.right_speaker,
                                                 (SCREEN_WIDTH - 100 - self.right_speaker.get_width(), 100))
                    name_sprite = self.right_speaker_name_sprite
                else:
                    name_sprite = None

                # Отрисовываем плашку диалога (поверх участников!)
                self.bg_chars_box_cache.blit(self.dialogue_box, (0, SCREEN_HEIGHT // 2))

                # Отрисовываем имя текущего говорящего
                if name_sprite:
                    self.bg_chars_box_cache.blit(name_sprite, (TEXT_X, TEXT_Y - 50))

                self.need_cache = False

            # Достаём кешированные элементы, пока мы на одной и той же строчке
            screen.blit(self.bg_chars_box_cache, (0, 0))

            # Отрисовываем текст
            self.draw_text_by_letter(screen)

            # Отрисовываем, когда персонаж прекращает "говорить"
            if not self.playing_line:

                # Отрисовываем кнопки выбора (если они есть)
                if self.awaiting.name == Awaiting.CHOOSE.name:
                    for btn_ind, btn in enumerate(self.choice_buttons):
                        # Сами кнопки
                        screen.blit(self.choice_button_sprites[btn.state], (btn.x, btn.y))

                        # Текст кнопок
                        screen.blit(self.button_text_sprites[btn_ind], (btn.x + btn.width + 10, btn.y))

                # Отрисовываем вводимый текст (если можно вводить)
                elif self.awaiting.name == Awaiting.INPUT.name:
                    # TODO: make BG for input field?
                    screen.blit(self.input_text_sprite, (TEXT_X, TEXT_Y + 100))

            # Отрисовываем текст ожидания (если есть музыка монстра)
            if self.dialogue.ominous and self.trying_to_finish:
                screen.blit(self.prepare_text, (SCREEN_WIDTH - 300, SCREEN_HEIGHT - 100))

            # БЛОКИРУЕМ ПОВТОРНУЮ ОТРИСОВКУ ДО ОБНОВЛЕНИЯ ЭЛЕМЕНТОВ
            if not self.playing_line:
                self.need_screen_update = False

            # Сообщаем об изменениях функции главного цикла
            return (Command.UPDATE_DISPLAY, None),

        return None

    """
    Вспомогательные функции для отрисовки
    """

    def draw_text_by_letter(self, screen):
        """Приятный глазу эффект выведения текста по буковке"""

        if self.playing_line:
            if self.line_cursor >= len(self.current_line):
                self.playing_line = False
                # Перерисовываем текст-изображение в последний раз
                self.current_line_sprite = self.dialogue_font.render(self.current_line[:int(self.line_cursor)],
                                                                     True,
                                                                     (0, 0, 0))
            else:
                cursor_sym = self.current_line[max(int(self.line_cursor) - 1, 0)]
                # TODO: what if we put special unprintable symbols in the dialogue that will change talking speed?
                if cursor_sym in '.?!':
                    self.line_cursor += 0.02
                elif cursor_sym in ':;':
                    self.line_cursor += 0.03
                else:
                    self.line_cursor += 0.4
                # Перерисовываем текст-изображение только тогда, когда он выводится
                self.current_line_sprite = self.dialogue_font.render(self.current_line[:int(self.line_cursor)],
                                                                     True,
                                                                     (0, 0, 0))
        screen.blit(self.current_line_sprite, (TEXT_X, TEXT_Y))
