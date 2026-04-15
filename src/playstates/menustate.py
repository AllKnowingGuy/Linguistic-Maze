from pathlib import Path

import pygame

from src import assetscreation
from src.config import Config
from src.level_building.button import Button
from src.playstates.basestate import BaseState
from src.util import (
    BIND_BUTTON_HEIGHT,
    BIND_BUTTON_WIDTH,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    START_BUTTON_HEIGHT,
    START_BUTTON_WIDTH,
    ButtonState,
    Command,
    get_centered_point,
    resource_path,
)

START_BUTTON_X = 440
START_BUTTON_Y = 370
LEFT_BIND_BUTTON_X = 5
RIGHT_BIND_BUTTON_X = SCREEN_WIDTH - 5 - BIND_BUTTON_WIDTH
BIND_BUTTON_Y = 165
BIND_BUTTON_DIST_Y = BIND_BUTTON_HEIGHT + 1
SETTING_TIME = 5000

DEF_KEYBIND_DICT = {
    "move_down": "s",
    "move_up": "w",
    "move_left": "a",
    "move_right": "d",
    "end_text_animation": "\u001b",
    "increase_volume": "+",
    "decrease_volume": "-",
    "no_task_advance": "\u000d",
}
KEYBIND_SETUP_TEXTS = {
    "move_down": "передвижения назад (в лабиринте)",
    "move_up": "передвижения вперёд (в лабиринте)",
    "move_left": "передвижения влево (в лабиринте)",
    "move_right": "передвижения вправо (в лабиринте)",
    "end_text_animation": "прекращения анимации текста",
    "increase_volume": "увеличения громкости звука",
    "decrease_volume": "уменьшения громкости звука",
    "no_task_advance": "перехода на следующую строчку диалога",
}
SPECIAL_CHARACTER_NAMES = {
    "\u000d": "ENTER",
    "\u001b": "ESCAPE",
    "\u0009": "TAB",
    "\u007f": "DELETE",
    "\u0008": "BACKSPACE",
}


class MenuState(BaseState):
    def __init__(self):
        super().__init__()
        self.starting_game = False  # если True - переход "в дверь"
        self.enter_anim_time = 0  # время начала перехода "в дверь"
        self.game_started = False  # если True - запуск интро

        self.just_lost = False  # экран проигрыша и рестарт
        self.just_won = False  # экран победы и рестарт
        self.played_victory_sound = False  # флаг, чтобы звук победы сыграл 1 раз
        self.game_end_score = None  # счёт, выводимый при проигрыше и победе
        self.game_end_artifacts = []  # артефакты, выводимые при проигрыше и победе

        self.left_settings_shown = False  # показаны ли левые кнопки настройки
        self.right_settings_shown = False  # показаны ли правые кнопки настройки

        self.awaiting_input = False  # если True - показывается экран настройки
        self.no_model_warning = False  # если True - показывается предупреждение
        self.current_action_binding = ""  # настраиваемое действие
        self.start_setting_time = 0  # время начала настройки
        self.setting_seconds = 5  # таймер настройки на экране

        self.config = Config()  # конфигуратор для получения и сохранения настроек
        self.keybind_dict = self.config.get_all_controls().copy()
        self.start_button = Button(
            START_BUTTON_X,
            START_BUTTON_Y,
            START_BUTTON_WIDTH,
            START_BUTTON_HEIGHT,
            "start",
        )  # кнопка старта
        self.left_settings_button = Button(
            LEFT_BIND_BUTTON_X,
            BIND_BUTTON_Y - BIND_BUTTON_DIST_Y,
            BIND_BUTTON_WIDTH,
            BIND_BUTTON_HEIGHT,
            "left_settings",
        )  # кнопка левого меню настроек
        self.right_settings_button = Button(
            RIGHT_BIND_BUTTON_X,
            BIND_BUTTON_Y - BIND_BUTTON_DIST_Y,
            BIND_BUTTON_WIDTH,
            BIND_BUTTON_HEIGHT,
            "right_settings",
        )  # кнопка правого меню настроек
        self.keybind_button_dict = {}  # кнопки настройки

        """Графика"""
        self.bg = assetscreation.add_menu_bg()  # основной задний фон
        self.bg_overlay = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT)
        )  # осветление фона для видимости текста настройки
        self.bg_overlay.set_alpha(200)
        self.bg_overlay.fill((255, 255, 255))
        self.bg_scale = 1.0

        self.loss_bg = assetscreation.add_menu_loss_bg()  # картинка проигрыша
        self.win_bg = assetscreation.add_menu_win_bg()  # картинка победы

        self.start_button_sprite = (
            assetscreation.add_start_buttons()
        )  # изображение кнопки старта
        self.left_settings_button_sprite, self.right_settings_button_sprite = (
            assetscreation.add_setting_sections_buttons()
        )  # изображения кнопок меню настроек
        self.keybind_button_sprites_dict = {}  # изображения кнопок настройки

        for s_ind, setting in enumerate(self.keybind_dict):
            # заполнение словарей кнопок настройки
            self.keybind_button_dict[setting] = Button(
                (
                    LEFT_BIND_BUTTON_X
                    if s_ind < len(self.keybind_dict) / 2
                    else RIGHT_BIND_BUTTON_X
                ),
                BIND_BUTTON_Y + BIND_BUTTON_DIST_Y * (s_ind % 4),
                BIND_BUTTON_WIDTH,
                BIND_BUTTON_HEIGHT,
                setting,
            )
            self.keybind_button_dict[setting].state = ButtonState.DISABLED
            self.keybind_button_sprites_dict[setting] = assetscreation.add_bind_buttons(
                setting
            )

        self.btn_set = [
            self.start_button,
            self.left_settings_button,
            self.right_settings_button,
        ]  # список всех кнопок меню
        self.btn_set.extend(self.keybind_button_dict.values())

        # Выводимые тексты
        self.setting_text_sprite = None  # текст настройки и предупреждения
        self.current_bind_sprite = None  # текст текущей кнопки действия

        """Музыка"""
        assetscreation.set_menu_music()  # основная музыка меню
        pygame.mixer.music.play(-1)
        self.enter_sound = assetscreation.add_maze_enter_sound()  # звук входа в дверь
        self.victory_sound = assetscreation.add_victory_sound()  # звук победы

        self.need_screen_update = True

    def add_sounds_for_volume_change(self):
        """
        Возврат звуков входа и победы для изменения громкости
        """

        return ((Command.ADD_SOUNDS, {self.enter_sound, self.victory_sound}),)

    def start_enter_anim(self):
        self.starting_game = True
        for btn in self.btn_set:
            btn.state = ButtonState.DISABLED

        # Играем переход, останавливаем музыку и играем звук
        pygame.mixer.music.stop()
        self.enter_sound.play()

        self.enter_anim_time = pygame.time.get_ticks()
        self.need_screen_update = True

    def play_enter_anim(self):
        if not self.starting_game:
            return None

        current_ticks = pygame.time.get_ticks()
        if current_ticks >= self.enter_anim_time + 2000:
            self.starting_game = False

            # Игра начинается
            self.game_started = True
            self.need_screen_update = True
            return ((Command.CHECK_PROGRESS, None),)

        # elif 0 <= (current_ticks - self.enter_anim_time) % 30 < 29:
        elif current_ticks <= self.enter_anim_time + 1000:
            self.bg_scale = min(
                float((current_ticks - self.enter_anim_time) / 80 + 1.0), 15.0
            )
            self.need_screen_update = True

        return None

    def start_setting(self):
        self.awaiting_input = True
        self.start_setting_time = pygame.time.get_ticks()
        self.need_screen_update = True

    def play_setting_timer(self):
        if not self.awaiting_input:
            return None

        current_ticks = pygame.time.get_ticks()

        if current_ticks >= self.start_setting_time + SETTING_TIME:
            # Когда время анимации настройки истекло
            for btn in self.btn_set:
                if not btn.state == ButtonState.DISABLED:
                    btn.state = ButtonState.REGULAR
            self.awaiting_input = False
            self.current_action_binding = ""
            self.config.set_controls(self.keybind_dict)
            self.need_screen_update = True
            return ((Command.UPDATE_MAIN_SETTINGS, None),)

        else:
            prev_time = self.setting_seconds
            self.setting_seconds = (
                SETTING_TIME // 1000 - (current_ticks - self.start_setting_time) // 1000
            )
            if self.setting_seconds != prev_time:
                self.need_screen_update = True
            return None

    """
    Переписанные функции состояния
    """

    def handle_input(self, event: pygame.event.Event):
        """
        Обработка нажатия клавиш для назначения кнопок управления или закрытия окна проигрыша/победы

        Args:
            event (Event): событие нажатия клавиши
        """

        if event.unicode != self.keybind_dict["no_task_advance"]:
            return

        if self.just_lost or self.just_won:
            # Полный рестарт игры после проигрыша или выигрыша
            self.just_lost = False
            self.just_won = False
            self.played_victory_sound = False
            self.game_end_score = None
            self.game_end_artifacts.clear()
            assetscreation.set_menu_music()
            pygame.mixer.music.play(-1)
            self.need_screen_update = True
            return

        elif (
            not self.awaiting_input
            or self.no_model_warning
            or not self.current_action_binding
            or not event.unicode
        ):
            return

        # Установка кнопок
        self.keybind_dict[self.current_action_binding] = event.unicode
        self.need_screen_update = True

    def handle_mouse_motion(self, event):
        """Обработка наведения курсора на кнопки"""

        if self.awaiting_input or self.starting_game or self.just_lost or self.just_won:
            return

        for btn in self.btn_set:
            self.update_button_on_hovering(btn, event)

    def handle_mouse_click(self, event):
        """Обработка нажатия на кнопки"""

        if (
            not event.button == pygame.BUTTON_LEFT
            or self.awaiting_input
            or self.starting_game
            or self.just_lost
            or self.just_won
        ):
            return

        for btn in self.btn_set:
            if self.update_buttons_on_press(btn):
                return

    def handle_mouse_release(self, event):
        """Обработка отпуска ЛКМ после щелчка по кнопке навигации"""

        if not event.button == pygame.BUTTON_LEFT:
            return None

        if (
            self.awaiting_input
            or self.starting_game
            or self.just_lost
            or self.just_won
            or not ButtonState.PRESSED in [btn.state for btn in self.btn_set]
        ):
            return None

        # Когда курсор поверх нажатой кнопки - отпуск активирует действие
        for btn in self.btn_set:
            if btn.is_hovered(event.pos) and btn.state == ButtonState.PRESSED:

                # Почти все кнопки становятся неподсвеченными
                for btn2 in self.btn_set:
                    if not btn2.state == ButtonState.DISABLED:
                        if btn2 is btn:
                            btn2.state = ButtonState.HOVERED
                        else:
                            btn2.state = ButtonState.REGULAR
                self.need_screen_update = True

                # Кнопка старта
                if btn is self.start_button:
                    return self.try_to_start()

                # Кнопка левого меню настроек
                elif btn is self.left_settings_button:
                    for btn2 in tuple(self.keybind_button_dict.values())[
                        0 : (len(self.keybind_button_dict) + 1) // 2
                    ]:
                        if self.left_settings_shown:
                            btn2.state = ButtonState.DISABLED
                        else:
                            btn2.state = ButtonState.REGULAR
                    self.left_settings_shown = not self.left_settings_shown
                    return None

                # Кнопка правого меню настроек
                elif btn is self.right_settings_button:
                    for btn2 in tuple(self.keybind_button_dict.values())[
                        (len(self.keybind_button_dict) + 1)
                        // 2 : len(self.keybind_button_dict)
                    ]:
                        if self.right_settings_shown:
                            btn2.state = ButtonState.DISABLED
                        else:
                            btn2.state = ButtonState.REGULAR
                    self.right_settings_shown = not self.right_settings_shown
                    return None

                # Кнопки самих настроек
                elif btn in self.keybind_button_dict.values():
                    self.current_action_binding = btn.text
                    self.start_setting()
                    return None

                else:
                    raise ValueError(f"This button is foreign: {btn.text}")

        else:
            # Когда отпустили курсор не над нажатой кнопкой - почти все кнопки становятся неподсвеченными
            for btn in self.btn_set:
                if not btn.state == ButtonState.DISABLED:
                    if not btn.is_hovered(event.pos):
                        btn.state = ButtonState.REGULAR
                    else:
                        btn.state = ButtonState.HOVERED
            self.need_screen_update = True
            return None

    def execute_before_draw(self):
        """Проверка истечения таймера настройки, а также возвратов в меню"""

        if self.just_lost or self.just_won:
            if self.just_lost and not pygame.mixer.music.get_busy():
                assetscreation.set_gameover_music()
                pygame.mixer.music.play(-1)
            elif self.just_won and not self.played_victory_sound:
                pygame.mixer.music.stop()
                self.victory_sound.play()
                self.played_victory_sound = True

            self.game_started = False
            self.bg_scale = 1.0
            self.start_button.state = ButtonState.REGULAR
            self.left_settings_button.state = ButtonState.REGULAR
            self.right_settings_button.state = ButtonState.REGULAR
            for btn in tuple(self.keybind_button_dict.values())[
                0 : (len(self.keybind_button_dict) + 1) // 2
            ]:
                if self.left_settings_shown:
                    btn.state = ButtonState.DISABLED
                else:
                    btn.state = ButtonState.REGULAR
            for btn in tuple(self.keybind_button_dict.values())[
                (len(self.keybind_button_dict) + 1) // 2 : len(self.keybind_button_dict)
            ]:
                if self.right_settings_shown:
                    btn.state = ButtonState.DISABLED
                else:
                    btn.state = ButtonState.REGULAR

        if self.awaiting_input:
            return self.play_setting_timer()
        elif self.starting_game:
            return self.play_enter_anim()

        return None

    def draw(self, screen):
        """Отрисовка меню"""

        # ТОЛЬКО ЕСЛИ ЧТО-ТО ИЗМЕНИЛОСЬ НА ЭКРАНЕ
        if not self.need_screen_update:
            return None

        if self.just_lost or self.just_won:
            if self.just_lost:
                screen.blit(self.loss_bg, (0, 0))
            else:
                screen.blit(self.win_bg, (0, 0))

            cheer_text = (
                self.ps_font.render(
                    "Ничего страшного, игру можно пройти снова!",
                    True,
                    (255, 255, 255),
                )
                if self.just_lost
                else self.ps_font.render(
                    "Практика закрыта, игра пройдена!", True, (255, 255, 255)
                )
            )
            score_text = self.ps_font.render(
                f"Общий респект: {self.game_end_score}", True, (255, 255, 255)
            )
            artifacts_text = self.ps_font.render("", True, (255, 255, 255))
            artifacts_text_2 = self.ps_font.render("", True, (255, 255, 255))
            if len(self.game_end_artifacts) > 3:
                art_set_list = list(self.game_end_artifacts)
                artifacts_text = self.ps_font.render(
                    f"Найденные артефакты: {", ".join(art_set_list[:3])},",
                    True,
                    (255, 255, 255),
                )
                artifacts_text_2 = self.ps_font.render(
                    f"{", ".join(art_set_list[3:])}",
                    True,
                    (255, 255, 255),
                )
            elif len(self.game_end_artifacts) > 0:
                artifacts_text = self.ps_font.render(
                    f"Найденные артефакты: {", ".join(self.game_end_artifacts)}",
                    True,
                    (255, 255, 255),
                )
            advance_bind = self.keybind_dict["no_task_advance"]
            continue_text = self.ps_font.render(
                f"Нажмите {SPECIAL_CHARACTER_NAMES[advance_bind] if advance_bind in SPECIAL_CHARACTER_NAMES
                else advance_bind}, чтобы продолжить...",
                True,
                (255, 255, 255),
            )

            screen.blit(
                cheer_text, (get_centered_point(cheer_text.get_width(), False), 340)
            )
            screen.blit(score_text, (SCREEN_WIDTH / 2, 500))
            screen.blit(artifacts_text, (SCREEN_WIDTH / 2, 540))
            screen.blit(artifacts_text_2, (SCREEN_WIDTH / 2, 580))
            screen.blit(continue_text, (SCREEN_WIDTH / 2, 650))

        else:
            scaled_bg = pygame.transform.scale(
                self.bg,
                (
                    self.bg.get_width() * self.bg_scale,
                    self.bg.get_height() * self.bg_scale,
                ),
            )
            screen.blit(
                scaled_bg,
                (
                    get_centered_point(scaled_bg.get_width(), is_height=False)
                    - 60
                    + 60 * self.bg_scale,
                    get_centered_point(scaled_bg.get_height(), is_height=True)
                    + 190
                    - 190 * self.bg_scale,
                ),
            )
            if self.start_button.state != ButtonState.DISABLED:
                screen.blit(
                    self.start_button_sprite[self.start_button.state],
                    (self.start_button.x, self.start_button.y),
                )
            for btn_ind, s_m_btn in enumerate(
                (self.left_settings_button, self.right_settings_button)
            ):
                if s_m_btn.state != ButtonState.DISABLED:
                    screen.blit(
                        (
                            self.left_settings_button_sprite,
                            self.right_settings_button_sprite,
                        )[btn_ind][s_m_btn.state],
                        (s_m_btn.x, s_m_btn.y),
                    )
            for s_btn in self.keybind_button_dict.values():
                if s_btn.state != ButtonState.DISABLED:
                    screen.blit(
                        self.keybind_button_sprites_dict[s_btn.text][s_btn.state],
                        (s_btn.x, s_btn.y),
                    )

            if self.awaiting_input:
                screen.blit(self.bg_overlay, (0, 0))

                if not self.no_model_warning:
                    setting_text = self.ps_font.render(
                        f"Задайте клавишу для {KEYBIND_SETUP_TEXTS[self.current_action_binding]}:",
                        True,
                        (0, 0, 0),
                    )

                    if (
                        self.keybind_dict[self.current_action_binding]
                        in SPECIAL_CHARACTER_NAMES
                    ):
                        bind_text = self.ps_font.render(
                            SPECIAL_CHARACTER_NAMES[
                                self.keybind_dict[self.current_action_binding]
                            ],
                            True,
                            (0, 0, 0),
                        )
                    else:
                        bind_text = self.ps_font.render(
                            self.keybind_dict[self.current_action_binding],
                            True,
                            (0, 0, 0),
                        )

                    seconds_text = self.ps_font.render(
                        f"Клавиша сохранится через {self.setting_seconds}...",
                        True,
                        (0, 0, 0),
                    )

                else:
                    setting_text = self.ps_font.render(
                        f"Некоторые языковые модели, необходимые для правильной работы игры, отсутствуют в папке "
                        f"ресурсов",
                        True,
                        (0, 0, 0),
                    )

                    bind_text = self.ps_font.render(
                        f"Проверьте подключение к интернету и перезапустите игру для загрузки модели тональности",
                        True,
                        (0, 0, 0),
                    )

                    seconds_text = self.ps_font.render(
                        f"Предупреждение закроется через {self.setting_seconds}...",
                        True,
                        (0, 0, 0),
                    )

                screen.blit(
                    setting_text,
                    (
                        get_centered_point(setting_text.get_width(), False),
                        SCREEN_HEIGHT / 2 - 50,
                    ),
                )
                screen.blit(
                    bind_text,
                    (
                        get_centered_point(bind_text.get_width(), False),
                        SCREEN_HEIGHT / 2,
                    ),
                )
                screen.blit(
                    seconds_text,
                    (
                        get_centered_point(seconds_text.get_width(), False),
                        SCREEN_HEIGHT / 2 + 50,
                    ),
                )

        self.need_screen_update = False

        # Сообщаем об изменениях функции главного цикла
        return ((Command.UPDATE_DISPLAY, None),)

    def try_to_start(self):
        if (
            resource_path(
                Path("assets\\models\\existing_words_analysis\\dicts_ru")
            ).exists()
            and resource_path(
                Path("assets\\models\\sentiment_analysis\\rubert_sentiment_model")
            ).exists()
        ):
            self.start_enter_anim()
            return ((Command.CHECK_PROGRESS, None),)
        else:
            self.no_model_warning = True
            self.start_setting()
            return None
