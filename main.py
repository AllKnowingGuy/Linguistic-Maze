import sys
from pathlib import Path

import pygame

from src.config import Config
from src.level_building.checker import Checker
from src.playstates.basestate import BaseState
from src.playstates.challengestate import ChallengeState
from src.playstates.dialoguestate import DialogueState
from src.playstates.mazestate import MazeState
from src.playstates.menustate import MenuState
from src.util import SCREEN_HEIGHT, SCREEN_WIDTH, Command, StateType, resource_path

# Инициализация Pygame (теперь с музыкой!)
if pygame.get_sdl_version()[0] == 2:
    pygame.mixer.pre_init(44100, 32, 2, 1024)
pygame.init()
if pygame.mixer and not pygame.mixer.get_init():
    print("Warning, no sound")
    pygame.mixer = None


class Main:
    current_state_type: StateType
    current_state: BaseState
    framerate: int = 120
    sound_volume: float = 1.0
    show_framerate = True
    sounds: set[pygame.mixer.Sound]

    def __init__(self):
        from src.storyscript import StoryScript

        # Параметры
        self.running = True
        self.current_state = BaseState()
        self.current_state_type = StateType.MENU

        # Кнопки управления громкостью
        self.volume_up_bind, self.volume_down_bind = Config().get_sound_controls()

        # Звуки, громкость которых меняется
        self.sounds = set()

        # Окно и дисплей
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Лингвист в лабиринте")
        pygame.display.set_icon(
            pygame.image.load(resource_path(Path("assets\\images\\icon.png")))
        )
        self.clock = pygame.time.Clock()

        # Слои дисплея
        self.content_layer = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.hud_layer = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

        # Базовый шрифт
        self.base_font = pygame.font.Font(None, 20)

        # Счётчик FPS и задний фон для него
        self.fps_underlay = pygame.Surface((65, 20), pygame.SRCALPHA)
        self.fps_underlay.set_alpha(128)
        self.fps_underlay.fill((255, 255, 255))
        self.fps_text_sprite = self.base_font.render("FPS: " + "NA", True, (0, 0, 0))

        # Состояния игры (некоторые изспользуют проверщик)
        checker = Checker()
        self.maze_state = MazeState()
        self.dialogue_state = DialogueState(checker)
        self.challenge_state = ChallengeState(checker)
        self.menu_state = MenuState()
        # добавляйте другие состояния таким же образом (не забудьте отредактировать associate_current_state!)

        # Трекер прогресса
        self.story_script = StoryScript()

    def associate_current_state(self):
        """Добавление текущего состояния в специальную переменную для полиморфного использования"""
        if self.current_state_type == StateType.MAZE:
            self.current_state = self.maze_state
        elif self.current_state_type == StateType.DIALOGUE:
            self.current_state = self.dialogue_state
        elif self.current_state_type == StateType.CHALLENGE:
            self.current_state = self.challenge_state
        elif self.current_state_type == StateType.MENU:
            self.current_state = self.menu_state

    def handle_input(self, event):
        """Обработка ввода с клавиатуры"""

        # Изменение громкости всех звуков игры
        if event.unicode == chr(self.volume_up_bind):
            self.sound_volume = min(self.sound_volume + 0.1, 1.0)
        elif event.unicode == chr(self.volume_down_bind):
            self.sound_volume = max(self.sound_volume - 0.1, 0.0)
        for sound in self.sounds:
            sound.set_volume(self.sound_volume)
        pygame.mixer.music.set_volume(self.sound_volume)

        supposed_commands = self.current_state.handle_input(event)
        return supposed_commands

    def handle_hold_input(self):
        """Обработка зажатых кнопок"""

        pressed_keys = pygame.key.get_pressed()
        supposed_commands = self.current_state.handle_hold_input(pressed_keys)
        return supposed_commands

    def handle_button_release(self, event):
        """Обработка отпущенных кнопок"""

        pressed_keys = pygame.key.get_pressed()
        supposed_commands = self.current_state.handle_button_release(
            event, pressed_keys
        )
        return supposed_commands

    def handle_mouse_motion(self, event):
        """Обработка движений курсора"""

        supposed_commands = self.current_state.handle_mouse_motion(event)
        return supposed_commands

    def handle_mouse_click(self, event):
        """Обработка щелчка ЛКМ"""

        supposed_commands = self.current_state.handle_mouse_click(event)
        return supposed_commands

    def handle_mouse_release(self, event):
        """Обработка отпуска ЛКМ"""

        supposed_commands = self.current_state.handle_mouse_release(event)
        return supposed_commands

    def draw(self):
        """Отрисовка игры"""

        # Содержимое игры (полностью контролируется текущим состоянием)
        supposed_commands = self.current_state.draw(self.content_layer)

        # Счётчик FPS
        self.hud_layer.fill((0, 0, 0, 0))
        if self.show_framerate:
            self.hud_layer.blit(self.fps_underlay, (5, 5))
            self.fps_text_sprite = self.base_font.render(
                "FPS: " + str(int(self.clock.get_fps())), True, (0, 0, 0)
            )
            self.hud_layer.blit(self.fps_text_sprite, (10, 10))

        # Обновление дисплея содержимого (теперь со строгими ограничениями)
        if supposed_commands:
            for command in supposed_commands:
                if command[0].name == Command.UPDATE_DISPLAY.name:
                    self.screen.blit(self.content_layer, (0, 0))
                    break

        # Обновление дисплея FPS
        self.screen.blit(self.hud_layer, (0, 0))
        pygame.display.flip()
        return supposed_commands

    def run(self):
        """Главный цикл игры"""

        pressed_btns_amount = 0

        def process_commands(
            commands: tuple[tuple[Command, int | set[pygame.mixer.Sound]] | None],
        ):
            """
            Игровые состояния могут отправлять команды главному циклу (грубо говоря, игровому окну).
            Эта функция позволяет обрабатывать такие команды в разные моменты обновления окна.
            Например, до и после отрисовки.
            """
            if commands:  # проверка на None
                for command in commands:
                    if command:  # проверка на None
                        if command[0].name == Command.STOP.name:
                            self.running = False
                        elif command[0].name == Command.WAIT.name:
                            pygame.time.wait(command[1])
                        elif command[0].name == Command.SET_FPS.name:
                            self.framerate = command[1]
                        elif command[0].name == Command.CHECK_PROGRESS.name:
                            self.story_script.update_game_progress(self)
                        elif command[0].name == Command.ADD_SOUNDS.name:
                            self.sounds.update(command[1])
                        elif command[0].name == Command.UPDATE_MAIN_SETTINGS.name:
                            self.volume_up_bind, self.volume_down_bind = (
                                Config().get_sound_controls()
                            )

        # Подготовка к циклу
        self.story_script.update_game_progress(self)
        for state in (
            self.maze_state,
            self.dialogue_state,
            self.challenge_state,
            self.menu_state,
        ):
            process_commands(state.add_sounds_for_volume_change())

        # Начало цикла
        # Как только running станет False, игра закроется в конце итерации
        while self.running:

            # Обработка событий Pygame
            for event in pygame.event.get():

                # Обработка выхода из игры
                if event.type in (pygame.QUIT, pygame.WINDOWCLOSE):
                    self.running = False

                # Обработка нажатий кнопок
                elif event.type == pygame.KEYDOWN:
                    pressed_btns_amount += 1
                    process_commands(self.handle_input(event))

                # Обработка отпусков кнопок
                elif event.type == pygame.KEYUP:
                    pressed_btns_amount -= 1
                    process_commands(self.handle_button_release(event))

                # Обработка движения мыши
                elif event.type == pygame.MOUSEMOTION:
                    if self.current_state_type not in (StateType.MAZE,):
                        process_commands(self.handle_mouse_motion(event))

                # Обработка щелчка мышью
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.current_state_type not in (StateType.MAZE,):
                        process_commands(self.handle_mouse_click(event))

                # Обработка отпуска мыши
                elif event.type == pygame.MOUSEBUTTONUP:
                    if self.current_state_type not in (StateType.MAZE,):
                        process_commands(self.handle_mouse_release(event))

            # Обработка держания кнопок
            if pressed_btns_amount > 0:
                process_commands(self.handle_hold_input())

            # Отрисовка
            process_commands(self.current_state.execute_before_draw())
            process_commands(self.draw())
            process_commands(self.current_state.execute_after_draw())

            # Обновление всего, что на экране
            self.clock.tick(self.framerate)

        # Выход из игры
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Main()
    game.run()
