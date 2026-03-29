import pygame

from src import assetscreation
from src.config import Config
from src.playstates.basestate import BaseState
from src.level_building.button import Button
from src.util import (
    get_centered_point,
    START_BUTTON_WIDTH,
    START_BUTTON_HEIGHT,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    BIND_BUTTON_HEIGHT,
    BIND_BUTTON_WIDTH,
    Command, ButtonState,
)

START_BUTTON_X = get_centered_point(START_BUTTON_WIDTH, False)
START_BUTTON_Y = SCREEN_HEIGHT / 2 + 100
LEFT_BIND_BUTTON_X = 5
RIGHT_BIND_BUTTON_X = SCREEN_WIDTH - 5 - BIND_BUTTON_WIDTH
BIND_BUTTON_Y = 165
BIND_BUTTON_DIST_Y = BIND_BUTTON_HEIGHT + 10
SETTING_TIME = 5000

DEF_KEYBIND_DICT = {
        "move_down": "s",
        "move_up": "w",
        "move_left": "a",
        "move_right": "d",
        "end_text_animation": "\u001B",
        "increase_volume": "+",
        "decrease_volume": "-",
        "no_task_advance": "\u000D"
    }
KEYBIND_SETUP_TEXTS = {
        "move_down": "передвижения назад (в лабиринте)",
        "move_up": "передвижения вперёд (в лабиринте)",
        "move_left": "передвижения влево (в лабиринте)",
        "move_right": "передвижения вправо (в лабиринте)",
        "end_text_animation": "прекращения анимации текста",
        "increase_volume": "увеличения громкости звука",
        "decrease_volume": "уменьшения громкости звука",
        "no_task_advance": "перехода на следующую строчку диалога"
}
SPECIAL_CHARACTER_NAMES = {
    "\u000d": "ENTER",
    "\u001b": "ESCAPE",
    "\u0009": "TAB",
    "\u007F": "DELETE",
    "\u0008": "BACKSPACE"
}


class MenuState(BaseState):
    def __init__(self):
        super().__init__()
        self.game_started = False

        self.just_lost = False
        self.just_won = False
        self.game_end_score = None
        self.game_end_artifacts = []

        self.awaiting_input = False
        self.current_action_binding = ''
        self.start_setting_time = 0
        self.setting_seconds = 5

        self.config = Config()
        self.keybind_dict = self.config.get_all_controls().copy()
        self.start_button = Button(START_BUTTON_X, START_BUTTON_Y, START_BUTTON_WIDTH, START_BUTTON_HEIGHT, 'start')
        self.keybind_button_dict = {}

        self.bg = assetscreation.add_menu_bg()
        self.bg_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.bg_overlay.set_alpha(200)
        self.bg_overlay.fill((255, 255, 255))

        self.loss_bg = assetscreation.add_menu_loss_bg()
        self.win_bg = assetscreation.add_menu_win_bg()

        self.start_button_sprite = assetscreation.add_start_buttons()
        self.keybind_button_sprites_dict = {}

        for s_ind, setting in enumerate(self.keybind_dict):
            self.keybind_button_dict[setting] = Button(
                LEFT_BIND_BUTTON_X if s_ind < len(self.keybind_dict) / 2 else RIGHT_BIND_BUTTON_X,
                BIND_BUTTON_Y + BIND_BUTTON_DIST_Y * (s_ind % 4),
                BIND_BUTTON_WIDTH,
                BIND_BUTTON_HEIGHT,
                setting
            )
            self.keybind_button_sprites_dict[setting] = assetscreation.add_bind_buttons(setting)

        self.btn_set = [self.start_button]
        self.btn_set.extend(self.keybind_button_dict.values())

        # Шрифт меню и выводимые тексты
        self.menu_font = pygame.font.Font(None, 35)
        self.setting_text_sprite = None
        self.current_bind_sprite = None

        # Музыка
        assetscreation.set_menu_music()
        pygame.mixer.music.play(-1)
        self.victory_sound = assetscreation.add_victory_sound()

        self.need_screen_update = True

    def start_setting(self):
        self.awaiting_input = True
        self.start_setting_time = pygame.time.get_ticks()
        self.need_screen_update = True

    def play_input_timer(self):
        if self.awaiting_input:
            current_ticks = pygame.time.get_ticks()

            if current_ticks >= self.start_setting_time + SETTING_TIME:
                self.awaiting_input = False
                self.current_action_binding = ''
                self.config.set_controls(self.keybind_dict)
                self.need_screen_update = True

            else:
                prev_time = self.setting_seconds
                self.setting_seconds = SETTING_TIME // 1000 - (current_ticks - self.start_setting_time) // 1000
                if self.setting_seconds != prev_time:
                    self.need_screen_update = True

    """
    Переписанные функции состояния
    """

    def handle_input(self, event):
        """Обработка назначения клавиш"""

        if (self.just_lost or self.just_won) and event.unicode == self.keybind_dict["no_task_advance"]:
            self.just_lost = False
            self.just_won = False
            self.game_end_score = None
            self.game_end_artifacts.clear()
            assetscreation.set_menu_music()
            pygame.mixer.music.play(-1)
            self.need_screen_update = True

        if self.awaiting_input and self.current_action_binding and event.unicode:
            # Установка кнопок
            self.keybind_dict[self.current_action_binding] = event.unicode
            self.need_screen_update = True

    def handle_mouse_motion(self, event):
        """Обработка наведения курсора на кнопки"""

        if not self.awaiting_input:
            for btn in self.btn_set:
                self.update_button_on_hovering(btn, event)

    def handle_mouse_click(self, event):
        """Обработка нажатия на кнопки"""

        if event.button == pygame.BUTTON_LEFT and not self.awaiting_input:
            for btn in self.btn_set:
                if self.update_buttons_on_press(btn):
                    return

    def handle_mouse_release(self, event):
        """Обработка отпуска ЛКМ после щелчка по кнопке навигации"""

        if (event.button == pygame.BUTTON_LEFT
                and not self.awaiting_input
                and ButtonState.PRESSED in [btn.state for btn in self.btn_set]):

            # Когда курсор поверх нажатой кнопки - отпуск активирует действие
            for btn in self.btn_set:
                if btn.is_hovered(event.pos) and btn.state == ButtonState.PRESSED:

                    if btn is self.start_button:
                        self.game_started = True
                        btn.state = ButtonState.REGULAR
                        return (Command.CHECK_PROGRESS, None),

                    elif btn in self.keybind_button_dict.values():
                        self.current_action_binding = btn.text
                        self.start_setting()

                    else:
                        raise ValueError(f'This button is foreign: {btn.text}')

            # Когда отпустили курсор - все кнопки становятся неподсвеченными
            for btn in self.btn_set:
                if not btn.state == ButtonState.DISABLED:
                    btn.state = ButtonState.REGULAR
            self.need_screen_update = True

        return None

    def execute_before_draw(self):
        """Проверка истечения таймера настройки, а также возвратов в меню"""

        if self.just_lost and not pygame.mixer.music.get_busy():
            assetscreation.set_gameover_music()
            pygame.mixer.music.play(-1)

        elif self.just_won:
            pygame.mixer.music.stop()
            self.victory_sound.play()

        if self.awaiting_input:
            self.play_input_timer()

    def draw(self, screen):
        """Отрисовка меню"""

        # ТОЛЬКО ЕСЛИ ЧТО-ТО ИЗМЕНИЛОСЬ НА ЭКРАНЕ
        if self.need_screen_update:

            if self.just_lost or self.just_won:
                screen.blit(self.loss_bg, (0, 0)) if self.just_lost else screen.blit(self.win_bg, (0, 0))

                cheer_text = self.menu_font.render(
                    "Ничего страшного, игру можно пройти снова!", True, (255, 255, 255)
                ) if self.just_lost else self.menu_font.render(
                    "Практика закрыта, игра пройдена!", True, (255, 255, 255)
                )
                score_text = self.menu_font.render(
                    f"Общий респект: {self.game_end_score}", True, (255, 255, 255))
                artifacts_text = self.menu_font.render("", True, (255, 255, 255))
                artifacts_text_2 = self.menu_font.render("", True, (255, 255, 255))
                if len(self.game_end_artifacts) > 3:
                    artifacts_text = self.menu_font.render(
                        f"Найденные артефакты: {", ".join(self.game_end_artifacts[:3])},", True, (255, 255, 255)
                    )
                    artifacts_text_2 = self.menu_font.render(
                        f"{", ".join(self.game_end_artifacts[3:])}", True, (255, 255, 255)
                    )
                elif len(self.game_end_artifacts) > 0:
                    artifacts_text = self.menu_font.render(
                        f"Найденные артефакты: {", ".join(self.game_end_artifacts)}", True, (255, 255, 255)
                    )
                advance_bind = self.keybind_dict["no_task_advance"]
                continue_text = self.menu_font.render(
                    f"Нажмите {SPECIAL_CHARACTER_NAMES[advance_bind] if advance_bind in SPECIAL_CHARACTER_NAMES
                    else advance_bind}, чтобы продолжить...", True, (255, 255, 255))

                screen.blit(cheer_text, (get_centered_point(cheer_text.get_width(), False), 300))
                screen.blit(score_text, (SCREEN_WIDTH / 2, 500))
                screen.blit(artifacts_text, (SCREEN_WIDTH / 2, 540))
                screen.blit(artifacts_text_2, (SCREEN_WIDTH / 2, 580))
                screen.blit(continue_text, (SCREEN_WIDTH / 2, 650))

            else:
                screen.blit(self.bg, (0, 0))
                screen.blit(self.start_button_sprite[self.start_button.state], (self.start_button.x, self.start_button.y))
                for s_btn in self.keybind_button_dict.values():
                    screen.blit(self.keybind_button_sprites_dict[s_btn.text][s_btn.state], (s_btn.x, s_btn.y))

                if self.awaiting_input:
                    screen.blit(self.bg_overlay, (0, 0))

                    setting_text = self.menu_font.render(
                        f"Задайте клавишу для {KEYBIND_SETUP_TEXTS[self.current_action_binding]}:",
                        True,
                        (0, 0, 0))

                    if self.keybind_dict[self.current_action_binding] in SPECIAL_CHARACTER_NAMES:
                        bind_text = self.menu_font.render(
                            SPECIAL_CHARACTER_NAMES[self.keybind_dict[self.current_action_binding]],
                            True,
                            (0, 0, 0))
                    else:
                        bind_text = self.menu_font.render(
                            self.keybind_dict[self.current_action_binding],
                            True,
                            (0, 0, 0))

                    seconds_text = self.menu_font.render(
                        f"Клавиша сохранится через {self.setting_seconds}...",
                        True,
                        (0, 0, 0))

                    screen.blit(setting_text,
                                (get_centered_point(setting_text.get_width(), False), SCREEN_HEIGHT / 2 - 50))
                    screen.blit(bind_text,
                                (get_centered_point(bind_text.get_width(), False), SCREEN_HEIGHT / 2))
                    screen.blit(seconds_text,
                                (get_centered_point(seconds_text.get_width(), False), SCREEN_HEIGHT / 2 + 50))

            self.need_screen_update = False

            # Сообщаем об изменениях функции главного цикла
            return (Command.UPDATE_DISPLAY, None),

        return None
