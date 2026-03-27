import pygame
from enum import Enum
from math import ceil
from pathlib import Path

from src import assetscreation
from src.config import Config
from src.level_building.dialogue import Dialogue
from src.level_building.button import Button
from src.util import SCREEN_WIDTH, SCREEN_HEIGHT, CHOICE_BUTTON_SIZE, Command, ButtonState, Awaiting
from src.playstates.basestate import BaseState

# Константы
TEXT_X = 100
TEXT_Y = SCREEN_HEIGHT // 2 + 100
TEXT_DIST_Y = 40
CHOICE_BUTTON_X = 100
CHOICE_BUTTON_Y = SCREEN_HEIGHT // 2 + 180
CHOICE_BUTTON_DIST_X = CHOICE_BUTTON_SIZE + 490  # расстояние между кнопками выбора по горизонтали
CHOICE_BUTTON_DIST_Y = CHOICE_BUTTON_SIZE + 7  # расстояние между кнопками выбора по вертикали


class Speaker(Enum):
    NO_ONE = 1
    LEFT = 2
    RIGHT = 3


class DialogueState(BaseState):
    dialogue: Dialogue | None
    finished: bool

    current_line_ind: int
    current_line: list[str]
    current_line_jump: int | None
    advancing: bool
    advance_point: int | None

    now_speaking: Speaker
    awaiting: Awaiting
    current_bg: pygame.Surface | None

    playing_line: bool = False
    line_cursor: int
    line_line: int

    choice_buttons: list[Button]
    choice_jumps: list[int | None]

    left_speaker: pygame.Surface | None
    right_speaker: pygame.Surface | None

    def __init__(self):
        """Задание некоторых атрибутов, загрузка изображений для отрисовки и создание шрифтов"""
        super().__init__()
        self.has_music = False
        self.left_name = "Протагонист"
        self.story_mode = False

        """Параметры по умолчанию"""
        self.dialogue = None

        self.finished = False
        self.trying_to_finish = False
        self.current_line_ind = 0
        self.advancing = False
        self.advance_point = None

        # Данные текущей строчки
        self.current_line = []
        self.now_speaking = Speaker.NO_ONE
        self.awaiting = Awaiting.CONTINUE
        self.current_line_jump = None

        # Данные анимации текста
        self.playing_line = False
        self.line_cursor = 10 ** 10
        self.line_line = 0

        # Кнопки выбора
        self.choice_buttons = []  # необходимо очищать каждый раз, когда нажимаем кнопку
        self.choice_jumps = []

        # Текст поля ввода
        self.current_input_text = ''  # необходимо очищать каждый раз, когда нажимаем Enter

        """Управление"""
        self.stop_anim_bind, self.advance_bind = Config().get_dialogue_controls()

        """Графика"""
        # Базовый фон диалога
        self.base_dialogue_bg = assetscreation.add_dialogue_bg()
        self.current_bg = None

        # Фон-скриншот предыдущего кадра
        self.need_screenshot = False
        self.screenshot_bg = None
        self.ssbg_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.ssbg_overlay.set_alpha(64)
        self.ssbg_overlay.fill((0, 0, 0))

        # Плашки диалога
        self.dialogue_box = assetscreation.add_dialogue_box()
        self.dialogue_box_story = assetscreation.add_dialogue_box(alt_version=True)

        # Студент и собеседник
        self.left_speaker = None
        self.right_speaker = None

        # Спрайты кнопок выбора
        self.choice_button_sprites = assetscreation.add_dialogue_choice_buttons()

        # Шрифт диалога и выводимые тексты
        self.dialogue_font = pygame.font.Font(None, 35)
        self.left_speaker_name_sprite = None
        self.right_speaker_name_sprite = None
        self.input_text_sprite = None
        self.button_text_sprites = [] # тоже необходимо очищать после нажатия кнопки
        self.prepare_text = self.dialogue_font.render('Приготовься...', True, (0, 0, 0))

        # Кеш редко меняющегося содержимого дисплея
        self.need_cache = False
        self.bg_chars_box_cache = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

        """Музыка"""
        self.start_music_time = 0

    def setup_dialogue(self, json_path_or_dialogue_dict: Path | dict[str, ...], prev_challenge_score: int | None = None):
        """Задание структурных данных диалога, сброс параметров проигрывания"""

        self.dialogue = Dialogue(json_path_or_dialogue_dict)
        self.finished = False

        # Прыжок на определённую линию, если диалог идёт после испытания
        if (self.dialogue.respect_checks
                and self.dialogue.respect_jumps
                and prev_challenge_score
                and prev_challenge_score in self.dialogue.respect_checks):
            jump_index = self.dialogue.respect_checks.index(prev_challenge_score)
            self.current_line_ind = self.dialogue.respect_jumps[jump_index]
        else:
            self.current_line_ind = 0

        # Очистка кнопок выбора и поля ввода
        self.choice_buttons = []
        self.choice_jumps = []
        self.current_input_text = ''

        # Установка базового заднего фона (может быть изменён по мере прочтения строчек)
        if self.screenshot_bg:
            self.current_bg = self.screenshot_bg
        else:
            self.current_bg = self.base_dialogue_bg

        # Получение данных первой строчки
        self.get_line_fields()

        # Данные анимации текста
        self.playing_line = False

        # Создание именных плашек говорящих
        if self.dialogue.left_character == "Протагонист":
            self.left_speaker_name_sprite = self.dialogue_font.render(
                self.left_name,
                True,
                (0, 0, 0) if not self.story_mode else (255, 255, 255))
        else:
            self.left_speaker_name_sprite = self.dialogue_font.render(
                self.dialogue.left_character,
                True,
                (0, 0, 0) if not self.story_mode else (255, 255, 255))
        self.right_speaker_name_sprite = self.dialogue_font.render(
            self.dialogue.right_character,
            True,
            (0, 0, 0) if not self.story_mode else (255, 255, 255))

        # Установка спрайта игрока (если тот участвует в диалоге)
        if self.dialogue.left_character and self.dialogue.left_character == "Протагонист":
            self.left_speaker = assetscreation.add_left_speak_sprite()

        # Установка спрайта собеседника (если указан в файле диалога и если собеседник вообще есть)
        if self.dialogue.right_character_path:
            self.right_speaker = assetscreation.add_right_speak_sprite(self.dialogue.right_character_path)
        elif self.dialogue.right_character:
            self.right_speaker = assetscreation.add_right_speak_sprite()

        # Если диалог зловещий - ставим музыку монстра, иначе музыку из файла диалога, если она указана
        if self.dialogue.ominous:
            assetscreation.set_dialogue_music('Monster.wav')
            self.has_music = True
        elif self.dialogue.music_path:
            assetscreation.set_dialogue_music(self.dialogue.music_path)
            self.has_music = True
        else:
            self.has_music = False

        # Запрос на обновление экрана
        self.need_screen_update = True

        # Обновление клавиш продолжения и прекращения анимации (чтобы подтянулись изменения в меню)
        self.stop_anim_bind, self.advance_bind = Config().get_dialogue_controls()

        return self.dialogue

    def start_playing(self):
        self.playing_line = True
        self.line_cursor = 0
        self.line_line = 0

        # Ставим музыку диалога
        if self.dialogue.ominous or self.dialogue.music_path:  # временно за неимением лучшего
            pygame.mixer.music.play(-1)
            self.start_music_time = pygame.time.get_ticks()

    def advance(self, jump_to: int = None):
        """Продвижение диалога на одну строчку или на определённую позицию"""

        # Если указано, на какую конкретно строчку перемещаться
        if not jump_to is None:

            # Завершаем диалог при "прыжке на -1"
            if jump_to == -1:
                self.trying_to_finish = True
                self.need_screen_update = True
                return

            # Иначе - прыгаем на указанную строчку
            self.current_line_ind = jump_to

        # Когда уходим с последней строчки - немедленно завершаем диалог
        elif self.current_line_ind == len(self.dialogue.lines) - 1:
            self.trying_to_finish = True
            self.need_screen_update = True
            return

        # Иначе - переходим на следующую строчку
        else:
            self.current_line_ind += 1

        # Если диалог ещё не завершился - добываем данные строчки
        if not self.finished and not self.trying_to_finish:
            self.get_line_fields()
            self.playing_line = True
            self.line_cursor = 0

        self.need_screen_update = True

    def get_line_fields(self):
        """Получение данных из строчки диалогового файла"""

        # Если диалог завершён - не пытаемся извлечь данные
        if self.finished or self.trying_to_finish:
            return

        # Извлекаем текст
        self.current_line = self.dialogue.get_line_text(self.current_line_ind)
        self.line_line = 0

        # Извлекаем метаданные
        self.current_line_jump = self.dialogue.get_line_jump(self.current_line_ind)

        side = self.dialogue.get_line_speaker(self.current_line_ind)
        action_type = self.dialogue.get_line_action_type(self.current_line_ind)
        new_bg = self.dialogue.get_line_bgswitch(self.current_line_ind)
        new_music = self.dialogue.get_line_musicswitch(self.current_line_ind)

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
                self.input_text_sprite = self.dialogue_font.render(
                    ' - Ввод: ',
                    True,
                    (0, 0, 0) if not self.story_mode else (255, 255, 255))
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

            # Фон-скриншот
            if new_bg == 'PREVSCREEN':
                self.need_screenshot = True

            # Загружаемый фон
            else:
                newly_loaded_bg = assetscreation.add_dialogue_bg(new_bg)
                if newly_loaded_bg:
                    self.current_bg = newly_loaded_bg
                else:
                    # Если не получилось загрузить фон диалога - ставим стандартный
                    self.current_bg = self.base_dialogue_bg

        # Если строчка меняет музыку
        if new_music:

            # Остановка музыки
            if new_music == 'STOP':
                pygame.mixer.music.fadeout(1)
                self.dialogue.ominous = False # Не стоит завершать диалог с меняющейся музыкой "в такт"

            # Загрузка другой музыки
            else:
                assetscreation.set_dialogue_music(new_music)
                pygame.mixer.music.play(-1)

        # Запрашиваем обновление редко меняющихся элементов экрана
        self.need_cache = True

    def set_choosefrom_line(self):
        # Получаем варианты ответа и создаём список кнопок
        current_choice_options = self.dialogue.get_line_choose_options(self.current_line_ind)
        number_of_options = len(current_choice_options)

        # Создаём объекты кнопок, сразу указывая их расположение
        for opt_ind, opt in enumerate(current_choice_options):
            if number_of_options < 5:
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
            self.button_text_sprites.append(self.dialogue_font.render(
                opt,
                True,
                (0, 0, 0) if not self.story_mode else (255, 255, 255)
            ))
            # Sorry Button text attribute, but rerendering you every time costs FPS - Vsevolod

        # Получаем индексы строчек, на которые нас перемещают определённые кнопки
        self.choice_jumps = self.dialogue.get_line_choose_jumps(self.current_line_ind)

    def finish(self):
        if self.dialogue.ominous:
            if 0 <= (pygame.time.get_ticks() - self.start_music_time) % 2000 < 6:  # FPS are imperfect - Vsevolod
                self.finished = True
                self.trying_to_finish = False
                self.need_screen_update = True
        else:
            self.finished = True
            self.trying_to_finish = False
            self.need_screen_update = True
            # print(f"I FINISHED ON LINE {self.current_line_ind} MAN")

    """
    Переписанные функции состояния
    """

    def handle_input(self, event):
        """Обработка ввода с клавиатуры и нажатия клавиш продолжения диалога и прекращения анимации"""

        # Вывод всего сообщения сразу
        if self.playing_line and event.unicode == chr(self.stop_anim_bind):
            self.line_line = len(self.current_line) - 1
            self.line_cursor = len(self.current_line[self.line_line])

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
                        self.dialogue.saved_inputs[self.current_line_ind] = self.current_input_text.strip()
                        self.current_input_text = ''
                        self.advancing = True
                        self.advance_point = self.current_line_jump
                        return (Command.CHECK_PROGRESS, None),

                # Нажатие других кнопок
                else:
                    self.current_input_text, updated = self.update_input_field(self.current_input_text, event)
                    if updated:
                        self.input_text_sprite = self.dialogue_font.render(
                            ' - Ввод: ' + self.current_input_text,
                            True,
                            (0, 0, 0) if not self.story_mode else (255, 255, 255)
                        )

            # Когда поля ввода нет (настройки ВЛИЯЮТ)
            elif event.unicode == chr(self.advance_bind):
                self.advancing = True
                self.advance_point = self.current_line_jump
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
                    self.dialogue.saved_choices[self.current_line_ind] = btn.text
                    self.advancing = True
                    self.advance_point = self.choice_jumps[btn_ind] if self.choice_jumps else None
                    self.choice_buttons.clear()  # сбрасываем кнопки: на следующей строчке будут другие (если будут)
                    self.button_text_sprites.clear()
                    self.choice_jumps.clear()  # сбрасываем прыжки по диалогу для кнопок

                    return (Command.CHECK_PROGRESS, None),
            else:
                # Когда отпустили курсор не над нажатой кнопкой - все кнопки становятся неподсвеченными
                for btn in self.choice_buttons:
                    btn.state = ButtonState.REGULAR
            self.need_screen_update = True
        return None

    def execute_before_draw(self):
        if self.advancing:
            self.advance(self.advance_point)
            self.advancing = False
            self.advance_point = None

        if self.trying_to_finish:
            self.finish()
        elif self.finished:
            if self.has_music:
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
                if self.now_speaking == Speaker.LEFT and self.left_speaker:
                    self.bg_chars_box_cache.blit(self.left_speaker, (100, 30))
                    name_sprite = self.left_speaker_name_sprite
                elif self.now_speaking == Speaker.RIGHT and self.right_speaker:
                    self.bg_chars_box_cache.blit(self.right_speaker,
                                                 (SCREEN_WIDTH - 100 - self.right_speaker.get_width(), 30))
                    name_sprite = self.right_speaker_name_sprite
                else:
                    name_sprite = None

                # Отрисовываем плашку диалога (поверх участников!)
                if self.story_mode:
                    self.bg_chars_box_cache.blit(self.dialogue_box_story, (0, SCREEN_HEIGHT // 2))
                else:
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

                # Отрисовываем респект за строчку
                respect = self.dialogue.get_line_respect_points(self.current_line_ind)
                artifact = self.dialogue.get_line_artifact(self.current_line_ind)
                if respect:
                    announce = self.dialogue_font.render(
                        f'{respect} к респекту!',
                        True,
                        (0, 0, 0) if not self.story_mode else (255, 255, 255))
                    # TODO: play sound because it's cool
                    screen.blit(announce, (SCREEN_WIDTH / 2, SCREEN_HEIGHT - 100))
                elif artifact:
                    announce = self.dialogue_font.render(
                        f'Теперь у вас есть {artifact}!',
                        True,
                        (0, 0, 0) if not self.story_mode else (255, 255, 255))
                    screen.blit(announce, (SCREEN_WIDTH / 2, SCREEN_HEIGHT - 100))

                # Отрисовываем кнопки выбора (если они есть)
                if self.awaiting.name == Awaiting.CHOOSE.name:
                    for btn_ind, btn in enumerate(self.choice_buttons):
                        # Сами кнопки
                        screen.blit(self.choice_button_sprites[btn.state], (btn.x, btn.y))

                        # Текст кнопок
                        screen.blit(self.button_text_sprites[btn_ind], (btn.x + btn.width + 10, btn.y))

                # Отрисовываем вводимый текст (если можно вводить)
                elif self.awaiting.name == Awaiting.INPUT.name:
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

        # Двигаем курсор
        if self.line_cursor >= len(self.current_line[self.line_line]):
            self.line_line += 1
            if self.line_line >= len(self.current_line):
                self.line_line -= 1
                self.playing_line = False
            else:
                self.line_cursor = 0

        else:
            cursor_sym = self.current_line[self.line_line][max(int(self.line_cursor) - 1, 0)]
            # TODO: what if we put special unprintable symbols in the dialogue that will change talking speed?
            if cursor_sym in '.?!':
                self.line_cursor += 0.02
            elif cursor_sym in ':;':
                self.line_cursor += 0.03
            else:
                self.line_cursor += 0.4

        # Выводим "напечатанные" строчки сразу
        for i in range(self.line_line):
            line_sprite = self.dialogue_font.render(
                self.current_line[i],
                True,
                (0, 0, 0) if not self.story_mode else (255, 255, 255)
            )
            screen.blit(line_sprite, (TEXT_X, TEXT_Y + TEXT_DIST_Y * i))

        # "Печатаем" последнюю строчку по букве
        line_sprite = self.dialogue_font.render(
            self.current_line[self.line_line][:int(self.line_cursor)],
            True,
            (0, 0, 0) if not self.story_mode else (255, 255, 255)
        )
        screen.blit(line_sprite, (TEXT_X, TEXT_Y + TEXT_DIST_Y * self.line_line))
