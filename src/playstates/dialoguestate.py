from enum import Enum
from math import ceil
from pathlib import Path

import pygame

from src import assetscreation
from src.config import Config
from src.level_building.button import Button
from src.level_building.checker import Checker
from src.level_building.dialogue import Dialogue
from src.playstates.basestate import BaseState
from src.util import (
    CHOICE_BUTTON_SIZE,
    FILENAME_DISPLAY_PROTAG_DICT,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    Awaiting,
    ButtonState,
    Command,
)

# Константы
TEXT_X = 100
TEXT_Y = SCREEN_HEIGHT // 2 + 100
TEXT_DIST_Y = 40
CHOICE_BUTTON_X = 100
CHOICE_BUTTON_Y = SCREEN_HEIGHT // 2 + 180
CHOICE_BUTTON_DIST_X = (
    CHOICE_BUTTON_SIZE + 490
)  # расстояние между кнопками выбора по горизонтали
CHOICE_BUTTON_DIST_Y = (
    CHOICE_BUTTON_SIZE + 7
)  # расстояние между кнопками выбора по вертикали
PROTAGS_ORDER = ("Аня", "Денис", "Лера", "Даня")


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
    answer_jumps: list[int | None]

    current_left_speaker: pygame.Surface | None
    current_right_speaker: pygame.Surface | None

    def __init__(self, checker: Checker):
        """Задание некоторых атрибутов, загрузка изображений для отрисовки и создание шрифтов"""
        super().__init__(checker)

        self.story_mode = False
        self.has_music = False
        self.left_real_name = "Протагонист"

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
        self.line_cursor = 10**10
        self.line_line = 0

        # Кнопки выбора
        self.choice_buttons = []  # необходимо очищать каждый раз, когда нажимаем кнопку
        self.answer_jumps = []

        # Текст поля ввода
        self.current_input_text = ""  # тоже необходимо очищать

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
        self.current_left_speaker = None
        self.current_right_speaker = None
        self.dialogue_left_speaker = None
        self.dialogue_right_speaker = None

        # Спрайты кнопок выбора
        self.choice_button_sprites = assetscreation.add_dialogue_choice_buttons()

        # Выводимые тексты
        self.left_speaker_name_sprite = None
        self.right_speaker_name_sprite = None
        self.input_text_sprite = None
        self.button_text_sprites = []  # тоже необходимо очищать после нажатия кнопки
        self.prepare_text = None

        # Кеш редко меняющегося содержимого дисплея
        self.need_cache = False
        self.bg_chars_box_cache = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

        """Музыка и кэш звуков (для изменения громкости)"""
        self.start_music_time = 0
        self.sound_cache = set()

    def render_base_left_name(self):
        if self.dialogue.left_character == "Протагонист":
            self.left_speaker_name_sprite = self.ps_font.render(
                self.left_real_name,
                True,
                (0, 0, 0) if not self.story_mode else (255, 255, 255),
            )
        else:
            self.left_speaker_name_sprite = self.ps_font.render(
                self.dialogue.left_character,
                True,
                (0, 0, 0) if not self.story_mode else (255, 255, 255),
            )

    def render_line_name(
        self, line_name: str, current_protag_ind: int = 0, right: bool = True
    ):
        if line_name[:-1] == "PROTAG" and line_name[-1] in "1234":
            rendered_name = self.ps_font.render(
                PROTAGS_ORDER[(current_protag_ind + int(line_name[-1]) - 1) % 4],
                True,
                (0, 0, 0) if not self.story_mode else (255, 255, 255),
            )
        else:
            rendered_name = self.ps_font.render(
                line_name, True, (0, 0, 0) if not self.story_mode else (255, 255, 255)
            )
        if right:
            self.right_speaker_name_sprite = rendered_name
        else:
            self.left_speaker_name_sprite = rendered_name

    def create_line_sprite(
        self, line_sprite_path: str, current_protag_ind: int = 0, right: bool = True
    ):
        if line_sprite_path[:-1] == "PROTAG" and line_sprite_path[-1] in "1234":
            filename = [
                k
                for k, v in FILENAME_DISPLAY_PROTAG_DICT.items()
                if v
                == PROTAGS_ORDER[
                    (current_protag_ind + int(line_sprite_path[-1]) - 1) % 4
                ]
            ][0]
        else:
            filename = line_sprite_path
        if right:
            self.current_right_speaker = assetscreation.add_right_speak_sprite(filename)
        else:
            self.current_left_speaker = assetscreation.add_left_speak_sprite(filename)

    def setup_dialogue(
        self,
        json_path_or_dialogue_dict: Path | dict[str, ...],
        prev_challenge_score: int | None = None,
    ):
        """Задание структурных данных диалога, сброс параметров проигрывания"""

        self.dialogue = Dialogue(json_path_or_dialogue_dict)
        self.finished = False

        # Очистка кнопок выбора и поля ввода
        self.choice_buttons = []
        self.answer_jumps = []
        self.current_input_text = ""

        # Обновление параметров для диалогов-историй
        if self.dialogue.story_dialogue:
            self.story_mode = True
        else:
            self.story_mode = False
        self.prepare_text = self.ps_font.render(
            "Подожди немножко...",
            True,
            (0, 0, 0) if not self.story_mode else (255, 255, 255),
        )

        # Прыжок на определённую линию, если диалог идёт после испытания
        if (
            self.dialogue.respect_checks
            and self.dialogue.respect_jumps
            and not prev_challenge_score is None
            and prev_challenge_score in self.dialogue.respect_checks
        ):
            jump_index = self.dialogue.respect_checks.index(prev_challenge_score)
            self.current_line_ind = self.dialogue.respect_jumps[jump_index]
        else:
            self.current_line_ind = 0

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
        self.render_base_left_name()
        self.right_speaker_name_sprite = self.ps_font.render(
            self.dialogue.right_character,
            True,
            (0, 0, 0) if not self.story_mode else (255, 255, 255),
        )

        # Установка спрайта игрока (если тот участвует в диалоге)
        if (
            self.dialogue.left_character
            and self.dialogue.left_character == "Протагонист"
        ):
            if self.left_real_name and self.left_real_name != "Протагонист":
                self.current_left_speaker = assetscreation.add_left_speak_sprite(
                    f"{[k for k, v in FILENAME_DISPLAY_PROTAG_DICT.items() if v == self.left_real_name][0]}.png"
                )
            else:
                self.current_left_speaker = assetscreation.add_left_speak_sprite()

        # Установка спрайта собеседника (если указан в файле диалога и если собеседник вообще есть)
        if self.dialogue.right_character_path:
            self.dialogue_right_speaker = self.current_right_speaker = (
                assetscreation.add_right_speak_sprite(
                    self.dialogue.right_character_path
                )
            )
        elif self.dialogue.right_character:
            self.dialogue_right_speaker = self.current_right_speaker = (
                assetscreation.add_right_speak_sprite()
            )

        # Если диалог зловещий - ставим музыку монстра, иначе музыку из файла диалога, если она указана
        if self.dialogue.ominous:
            assetscreation.set_dialogue_music("Monster.wav")
            self.has_music = True
        elif self.dialogue.victorious:
            assetscreation.set_dialogue_music("Outro.wav")
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
        if (
            self.dialogue.ominous
            or self.dialogue.victorious
            or self.dialogue.music_path
        ):
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
        sound = self.dialogue.get_line_sound(self.current_line_ind)

        # Если линию произносит один из участников
        if side:
            if side == "left":
                self.now_speaking = Speaker.LEFT
            elif side == "right":
                self.now_speaking = Speaker.RIGHT
            else:
                raise ValueError(f"This side cannot be processed: {side}")
        else:
            self.now_speaking = Speaker.NO_ONE

        # Меняем персонажей, если требуется
        self.handle_line_speakers()

        # Если строчка требует действия от игрока
        if action_type:
            # Если нужно ввести текст
            if action_type == "savetyped":
                self.awaiting = Awaiting.INPUT
                self.input_text_sprite = self.ps_font.render(
                    " - Ввод: ",
                    True,
                    (0, 0, 0) if not self.story_mode else (255, 255, 255),
                )
                # Получаем индексы строчек, на которые нас перемещают правильный и неправильный ответы
                self.answer_jumps = self.dialogue.get_line_answer_jumps(
                    self.current_line_ind
                )
            # Если нужно нажать на кнопку
            elif action_type == "choosefrom":
                self.awaiting = Awaiting.CHOOSE
                self.set_choosefrom_line()
            else:
                raise ValueError(f"This action cannot be processed: {action_type}")
        else:
            self.awaiting = Awaiting.CONTINUE

        # Если строчка меняет задний фон
        if new_bg:

            # Фон-скриншот
            if new_bg == "PREVSCREEN":
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
            if new_music == "STOP":
                pygame.mixer.music.fadeout(1)
                # Диалог с меняющейся музыкой слишком сложно завершить "в такт"
                self.dialogue.ominous = False
                self.dialogue.victorious = False

            # Загрузка другой музыки
            else:
                assetscreation.set_dialogue_music(new_music)
                pygame.mixer.music.play(-1)

        # Если во время строчки один раз играет звук
        if sound:
            sound_object = assetscreation.add_dialogue_sound(sound)
            self.sound_cache.add(sound_object)
            if sound_object:
                sound_object.play()

        # Запрашиваем обновление редко меняющихся элементов экрана
        self.need_cache = True

    def set_choosefrom_line(self):
        # Получаем варианты ответа и создаём список кнопок
        current_choice_options = self.dialogue.get_line_choose_options(
            self.current_line_ind
        )
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
                        opt,
                    )
                )
            else:
                # Кнопки в два столбика
                self.choice_buttons.append(
                    Button(
                        CHOICE_BUTTON_X
                        + CHOICE_BUTTON_DIST_X * (opt_ind >= number_of_options / 2),
                        CHOICE_BUTTON_Y
                        + CHOICE_BUTTON_DIST_Y
                        * (opt_ind % ceil(number_of_options / 2)),
                        CHOICE_BUTTON_SIZE,
                        CHOICE_BUTTON_SIZE,
                        opt,
                    )
                )
            self.button_text_sprites.append(
                self.ps_font.render(
                    opt, True, (0, 0, 0) if not self.story_mode else (255, 255, 255)
                )
            )
            # Sorry Button text attribute, but rerendering you every time costs FPS - Vsevolod

        # Получаем индексы строчек, на которые нас перемещают определённые кнопки
        self.answer_jumps = self.dialogue.get_line_answer_jumps(self.current_line_ind)

    def handle_line_speakers(self):
        """Обработка данных о персонажах текущей строчки диалогового файла"""

        line_left_char = None
        line_left_sprite_path = None
        line_right_char = None
        line_right_sprite_path = None
        if self.now_speaking.name == Speaker.LEFT.name:
            line_left_char = self.dialogue.get_line_character(self.current_line_ind)
            line_left_sprite_path = self.dialogue.get_line_sprite(self.current_line_ind)
        elif self.now_speaking.name == Speaker.RIGHT.name:
            line_right_char = self.dialogue.get_line_character(self.current_line_ind)
            line_right_sprite_path = self.dialogue.get_line_sprite(
                self.current_line_ind
            )

        current_protag_ind = 0
        if self.left_real_name and self.left_real_name != "Протагонист":
            current_protag_ind = PROTAGS_ORDER.index(self.left_real_name)

        if line_left_char:
            self.render_line_name(line_left_char, current_protag_ind, right=False)
        else:
            self.render_base_left_name()
        if line_right_char:
            self.render_line_name(line_right_char, current_protag_ind, right=True)
        else:
            self.right_speaker_name_sprite = self.ps_font.render(
                self.dialogue.right_character,
                True,
                (0, 0, 0) if not self.story_mode else (255, 255, 255),
            )

        if line_left_sprite_path:
            if (
                    line_right_char
                    and line_left_char[:-1] == "PROTAG"
                    and line_left_char[-1] in "1234"
            ):
                filename = [
                    k
                    for k, v in FILENAME_DISPLAY_PROTAG_DICT.items()
                    if v
                       == PROTAGS_ORDER[
                           (current_protag_ind + int(line_left_char[-1]) - 1) % 4
                           ]
                ][0]
                self.current_left_speaker = assetscreation.add_left_speak_sprite(
                    filename
                )
            else:
                self.current_left_speaker = assetscreation.add_left_speak_sprite(
                    line_left_sprite_path
                )
        else:
            self.current_left_speaker = self.dialogue_left_speaker
        if line_right_sprite_path:
            if (
                    line_right_char
                    and line_right_char[:-1] == "PROTAG"
                    and line_right_char[-1] in "1234"
            ):
                filename = (
                    f"protagonists\\{[k for k, v in FILENAME_DISPLAY_PROTAG_DICT.items()
                                      if v == PROTAGS_ORDER[(current_protag_ind + int(line_right_char[-1]) - 1) % 4]
                                      ][0]}_right.png"
                )
                self.current_right_speaker = assetscreation.add_right_speak_sprite(
                    filename
                )
            else:
                self.current_right_speaker = assetscreation.add_right_speak_sprite(
                    line_right_sprite_path
                )
        else:
            self.current_right_speaker = self.dialogue_right_speaker

    def finish(self):
        if self.dialogue.ominous:
            if (
                0 <= (pygame.time.get_ticks() - self.start_music_time) % 2000 < 6
            ):  # FPS are imperfect - Vsevolod
                self.finished = True
                self.trying_to_finish = False
                self.need_screen_update = True
        elif self.dialogue.victorious:
            if (
                0
                <= (pygame.time.get_ticks() - self.start_music_time) % (36000 / 23)
                < 6
            ):
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
            self.line_line = len(self.current_line) - 1
            self.line_cursor = len(self.current_line[self.line_line])
            return None

        # Ограничения: диалог не завершён и не печатается, не требуется нажать на кнопку мышкой
        if (
            self.finished
            or self.trying_to_finish
            or self.playing_line
            or self.awaiting.name == Awaiting.CHOOSE.name
        ):
            return None

        # Когда есть поле ввода
        if self.awaiting.name == Awaiting.INPUT.name:

            # Нажатие Enter (настройки НЕ ВЛИЯЮТ!)
            if event.key == pygame.K_RETURN:

                # Ограничение: не продвигаемся, если ничего не ввели или ввели только проблелы
                if not self.current_input_text.strip():
                    return None

                self.dialogue.saved_inputs[self.current_line_ind] = (
                    self.current_input_text.strip()
                )
                self.advancing = True

                # Мгновенная проверка введённого ответа (если необходимо)
                supposed_checker = self.dialogue.get_line_checker(self.current_line_ind)
                if supposed_checker:
                    keys = self.dialogue.get_line_check_keys(self.current_line_ind)
                    input_correctness = self.checker.check(
                        self.current_input_text.strip(), keys, supposed_checker
                    )
                    self.advance_point = (
                        self.answer_jumps[not input_correctness]
                        if self.answer_jumps
                        else None
                    )
                else:
                    self.advance_point = self.current_line_jump

                self.current_input_text = ""  # сбрасываем текст поля ввода
                self.answer_jumps.clear()  # сбрасываем прыжки по диалогу
                return ((Command.CHECK_PROGRESS, None),)

            # Нажатие других кнопок
            else:
                self.current_input_text, updated = self.update_input_field(
                    self.current_input_text, event
                )
                if updated:
                    self.input_text_sprite = self.ps_font.render(
                        " - Ввод: " + self.current_input_text,
                        True,
                        (0, 0, 0) if not self.story_mode else (255, 255, 255),
                    )

        # Когда поля ввода нет (настройки ВЛИЯЮТ)
        elif event.unicode == chr(self.advance_bind):
            self.advancing = True
            self.advance_point = self.current_line_jump
            return ((Command.CHECK_PROGRESS, None),)

        return None  # bruuuh - Vsevolod

    def handle_mouse_motion(self, event):
        """Обработка наведения курсора на кнопки выбора"""

        # Ограничения: диалог не завершён и не печатается, нужно нажать кнопку мышкой, никакая кнопка не зажата
        if (
            self.finished
            or self.trying_to_finish
            or self.playing_line
            or not self.awaiting.name == Awaiting.CHOOSE.name
            or ButtonState.PRESSED in [btn.state for btn in self.choice_buttons]
        ):
            return

        for btn in self.choice_buttons:
            self.update_button_on_hovering(btn, event)

    def handle_mouse_click(self, event):
        """Обработка нажатия на кнопки выбора"""

        if (
            self.playing_line
            or not self.awaiting.name == Awaiting.CHOOSE.name
            or not event.button == pygame.BUTTON_LEFT
        ):
            return

        for btn in self.choice_buttons:
            if self.update_buttons_on_press(btn):
                return

    def handle_mouse_release(self, event):
        """Обработка отпуска ЛКМ после щелчка по кнопке выбора"""

        if (
            self.playing_line
            or not self.awaiting.name == Awaiting.CHOOSE.name
            or not event.button == pygame.BUTTON_LEFT
            or not ButtonState.PRESSED in [btn.state for btn in self.choice_buttons]
        ):
            return None

        for btn_ind, btn in enumerate(self.choice_buttons):
            if btn.is_hovered(event.pos) and btn.state == ButtonState.PRESSED:
                # Когда курсор поверх нажатой кнопки - отпуск активирует действие
                self.dialogue.saved_choices[self.current_line_ind] = btn.text
                self.advancing = True
                self.advance_point = (
                    self.answer_jumps[btn_ind] if self.answer_jumps else None
                )
                self.choice_buttons.clear()  # сбрасываем кнопки: на следующей строчке будут другие (если будут)
                self.button_text_sprites.clear()
                self.answer_jumps.clear()  # сбрасываем прыжки по диалогу для кнопок

                return ((Command.CHECK_PROGRESS, None),)
        else:
            # Когда отпустили курсор не над нажатой кнопкой - почти все кнопки становятся неподсвеченными
            for btn in self.choice_buttons:
                if not btn.is_hovered(event.pos):
                    btn.state = ButtonState.REGULAR
                else:
                    btn.state = ButtonState.HOVERED
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
            return ((Command.CHECK_PROGRESS, None),)
        return ((Command.ADD_SOUNDS, self.sound_cache),)

    def draw(self, screen):
        """Отрисовка диалога"""

        # ТОЛЬКО ЕСЛИ ЧТО-ТО ИЗМЕНИЛОСЬ НА ЭКРАНЕ
        if not self.need_screen_update:
            return None

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
            if self.now_speaking == Speaker.LEFT and self.current_left_speaker:
                self.bg_chars_box_cache.blit(self.current_left_speaker, (100, 30))
                name_sprite = self.left_speaker_name_sprite
            elif self.now_speaking == Speaker.RIGHT and self.current_right_speaker:
                self.bg_chars_box_cache.blit(
                    self.current_right_speaker,
                    (SCREEN_WIDTH - 100 - self.current_right_speaker.get_width(), 30),
                )
                name_sprite = self.right_speaker_name_sprite
            else:
                name_sprite = None

            # Отрисовываем плашку диалога (поверх участников!)
            if self.story_mode:
                self.bg_chars_box_cache.blit(
                    self.dialogue_box_story, (0, SCREEN_HEIGHT // 2)
                )
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
                announce = self.ps_font.render(
                    f"{respect} к респекту!",
                    True,
                    (0, 0, 0) if not self.story_mode else (255, 255, 255),
                )
                screen.blit(announce, (SCREEN_WIDTH / 2, SCREEN_HEIGHT - 100))
            elif artifact:
                announce = self.ps_font.render(
                    f"Теперь у тебя есть {artifact}!",
                    True,
                    (0, 0, 0) if not self.story_mode else (255, 255, 255),
                )
                screen.blit(announce, (SCREEN_WIDTH / 2, SCREEN_HEIGHT - 100))

            # Отрисовываем кнопки выбора (если они есть)
            if self.awaiting.name == Awaiting.CHOOSE.name:
                for btn_ind, btn in enumerate(self.choice_buttons):
                    # Сами кнопки
                    screen.blit(self.choice_button_sprites[btn.state], (btn.x, btn.y))

                    # Текст кнопок
                    screen.blit(
                        self.button_text_sprites[btn_ind],
                        (btn.x + btn.width + 10, btn.y),
                    )

            # Отрисовываем вводимый текст (если можно вводить)
            elif self.awaiting.name == Awaiting.INPUT.name:
                screen.blit(self.input_text_sprite, (TEXT_X, TEXT_Y + 100))

        # Отрисовываем текст ожидания (если есть музыка, которую надо завершить в ритм)
        if (
            self.dialogue.ominous or self.dialogue.victorious
        ) and self.trying_to_finish:
            screen.blit(self.prepare_text, (SCREEN_WIDTH - 350, SCREEN_HEIGHT - 100))

        # БЛОКИРУЕМ ПОВТОРНУЮ ОТРИСОВКУ ДО ОБНОВЛЕНИЯ ЭЛЕМЕНТОВ
        if not self.playing_line:
            self.need_screen_update = False

        # Сообщаем об изменениях функции главного цикла
        return ((Command.UPDATE_DISPLAY, None),)

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
            cursor_sym = self.current_line[self.line_line][
                max(int(self.line_cursor) - 1, 0)
            ]
            if cursor_sym in ".?!":
                self.line_cursor += 0.02
            elif cursor_sym in ":;":
                self.line_cursor += 0.03
            else:
                self.line_cursor += 0.4

        # Выводим "напечатанные" строчки сразу
        for i in range(self.line_line):
            line_sprite = self.ps_font.render(
                self.current_line[i],
                True,
                (0, 0, 0) if not self.story_mode else (255, 255, 255),
            )
            screen.blit(line_sprite, (TEXT_X, TEXT_Y + TEXT_DIST_Y * i))

        # "Печатаем" последнюю строчку по букве
        line_sprite = self.ps_font.render(
            self.current_line[self.line_line][: int(self.line_cursor)],
            True,
            (0, 0, 0) if not self.story_mode else (255, 255, 255),
        )
        screen.blit(line_sprite, (TEXT_X, TEXT_Y + TEXT_DIST_Y * self.line_line))
