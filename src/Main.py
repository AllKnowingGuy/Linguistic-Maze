import pygame
import sys

from playstates.BaseState import BaseState
from playstates import MazeState, DialogueState
# импортируйте другие состояния через запятую
from Util import Command, StateType, SCREEN_WIDTH, SCREEN_HEIGHT
from StoryScript import StoryScript


# Инициализация Pygame
pygame.init()


class Main: # TODO: maybe rename to Game
    current_state_type: StateType
    current_state: BaseState
    framerate: int = 60

    def __init__(self):
        self.running = True

        # Окно и дисплей
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Лингвист в лабиринте")
        self.clock = pygame.time.Clock()

        # Базовый шрифт
        self.base_font = pygame.font.Font(None, 20)

        # Счётчик FPS и задний фон для него
        self.fps_underlay = pygame.Surface((60, 20))
        self.fps_underlay.set_alpha(128)
        self.fps_underlay.fill((255, 255, 255))
        self.fps_text_sprite = self.base_font.render('FPS: ' + 'pending...', True, (0, 0, 0))

        # Состояния игры
        self.maze_manager = MazeState.MazeState()
        self.dialogue_manager = DialogueState.DialogueState()
        # добавляйте другие состояния таким же образом (не забудьте отредактировать associate_current_state!)

        # Трекер прогресса
        self.story_script = StoryScript()

    def associate_current_state(self):
        """Добавление текущего состояния в специальную переменную для полиморфного использования"""
        if self.current_state_type == StateType.MAZE:
            self.current_state = self.maze_manager
        elif self.current_state_type == StateType.DIALOGUE:
            self.current_state = self.dialogue_manager

    def handle_input(self, event):
        """Обработка ввода с клавиатуры"""
        # TODO: create customizable keybinds
        supposed_commands = self.current_state.handle_input(event)
        return supposed_commands

    def handle_hold_input(self):
        """Обработка зажатых кнопок"""
        pressed_keys = pygame.key.get_pressed()
        supposed_commands = self.current_state.handle_hold_input(pressed_keys)
        return supposed_commands

    def handle_mouse_motion(self):
        """Обработка движений курсора"""
        # TODO: try to optimise
        mouse_pos = pygame.mouse.get_pos()
        supposed_commands = self.current_state.handle_mouse_motion(mouse_pos)
        return supposed_commands

    def handle_mouse_click(self):
        """Обработка щелчка ЛКМ"""
        pressed_buttons = pygame.mouse.get_pressed()
        supposed_commands = self.current_state.handle_mouse_click(pressed_buttons)
        return supposed_commands

    def draw(self):
        """Отрисовка игры"""
        # self.screen.fill((0, 0, 0)) # disabled to test 'screenshotting' - Vsevolod
        supposed_commands = self.current_state.draw(self.screen)

        # Счётчик FPS
        # TODO: make blit on a different surface than self.screen and enable again
        # self.screen.blit(self.fps_underlay, (5, 5))
        # self.fps_text_sprite = self.base_font.render('FPS: ' + str(int(self.clock.get_fps())), True, (0, 0, 0))
        # self.screen.blit(self.fps_text_sprite, (10, 10))

        # Обновление дисплея
        pygame.display.flip()
        return supposed_commands

    def run(self):
        """Главный цикл игры"""

        pressed_btns_amount = 0

        def process_commands(commands: tuple[tuple[Command, int] | None]):
            """
            Игровые состояния могут отправлять команды главному циклу (грубо говоря, игровому окну).
            Эта функция позволяет обрабатывать такие команды в разные моменты обновления окна.
            Например, до и после отрисовки.
            """
            if commands: # проверка на None
                for command in commands:
                    if command: # проверка на None
                        if command[0].name == Command.STOP.name:
                            self.running = False
                        elif command[0].name == Command.WAIT.name:
                            pygame.time.wait(command[1])
                        elif command[0].name == Command.SET_FPS.name:
                            self.framerate = command[1]
                        elif command[0].name == Command.CHECK_PROGRESS.name:
                            self.story_script.update_game_progress(self)

        self.story_script.update_game_progress(self)
        while self.running: # как только running станет False, игра закроется в конце итерации
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
                    # TODO: maybe add playstate release handling but I don't see how it could be used

                # Обработка движения мыши
                elif event.type == pygame.MOUSEMOTION:
                    if self.current_state_type == StateType.DIALOGUE: # не проверяем мышь, когда она не используется
                        process_commands(self.handle_mouse_motion())

                # Обработка щелчка мышью
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.current_state_type == StateType.DIALOGUE: # не проверяем мышь, когда она не используется
                        process_commands(self.handle_mouse_click())

            # Обработка держания кнопок
            if pressed_btns_amount > 0:
                process_commands(self.handle_hold_input())

            # Прорисовка
            process_commands(self.current_state.execute_before_draw())
            process_commands(self.draw())
            process_commands(self.current_state.execute_after_draw())

            # Обновление всего, что на экране
            self.clock.tick(self.framerate)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Main()
    game.run()
