import pygame
import sys
from enum import Enum

from playstates.BaseState import BaseState
from playstates import MazeState, DialogueState
# импортируйте другие состояния через запятую
from Util import Border, Command, SCREEN_WIDTH, SCREEN_HEIGHT


class StateType(Enum):
    MAZE = 1
    DIALOGUE = 2
    CHALLENGE = 3


# Инициализация Pygame
pygame.init()


# Для тестирования диалога
dialogue_text = """left\tnoaction\tЯ студент и я умею говорить; только не знаю, что сказать(
right\tnoaction\tА я монстр, но я пока не знаю, как меня зовут.
left\tnoaction\tО, зато я знаю, сейчас скажу)
nochar\tsavetyped\tА как зовут монстра? Напишите ответ: здесь есть (нет) поле ввода
nochar\tchoosefrom{Да, Нет}\tВы уверены, что это правда?"""


class Main:
    current_state_type: StateType
    current_state: BaseState
    framerate: int = 10

    def __init__(self):
        self.running = True

        # Окно и дисплей
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Лингвист в лабиринте")
        self.clock = pygame.time.Clock()

        # Состояния игры
        self.maze = MazeState.MazeState()
        self.dialogue = DialogueState.DialogueState()
        # добавляйте другие состояния таким же образом (не забудьте отредактировать associate_current_state!)

        # Текущее состояние (пока игра в нём, ей неважно, что происходит в других состояниях)
        self.current_state_type = StateType.DIALOGUE # StateType.MAZE
        self.associate_current_state()

        # TODO: create a game script in a different file to set up stages and change current state following the plot
        self.maze.setup_maze(31, 19, (Border.WEST, Border.EAST), (1, 17), True, True)
        self.dialogue.setup_dialogue(dialogue_text.split('\n'), 'Говорящий монстр')

    def associate_current_state(self):
        """Добавление текущего состояния в специальную переменную для полиморфного использования"""
        if self.current_state_type == StateType.MAZE:
            self.current_state = self.maze
        elif self.current_state_type == StateType.DIALOGUE:
            self.current_state = self.dialogue

    def handle_input(self):
        """Обработка ввода с клавиатуры"""
        # TODO: create customizable keybinds
        keys = pygame.key.get_pressed()
        self.current_state.handle_input(keys)

    def draw(self):
        """Отрисовка игры"""
        self.screen.fill((0, 0, 0))
        self.current_state.draw(self.screen)
        pygame.display.flip()

    def run(self):
        """Главный цикл игры"""

        def process_command(command: tuple[Command, int]):
            """
            Игровые состояния могут отправлять команды главному циклу (грубо говоря, игровому окну).
            Эта функция позволяет обрабатывать такие команды в разные моменты обновления окна.
            Например, до и после отрисовки.
            """
            if command: # проверка на None
                if command[0].name == Command.WAIT.name:
                    pygame.time.wait(command[1])
                elif command[0].name == Command.SET_FPS.name:
                    self.framerate = command[1]

        running = True
        while running: # как только этот цикл наткнётся на running = False, игра закроется в конце итерации
            for event in pygame.event.get():
                # Обработка выхода из игры
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    # Обработка выхода через кнопку Esc
                    if event.key == pygame.K_ESCAPE:
                        running = False

                    # Сброс лабиринта через кнопку R (временно)
                    elif self.current_state_type == StateType.MAZE and event.key == pygame.K_r:
                        self.maze.setup_maze(31, 19,
                                             (Border.WEST, Border.EAST),
                                             (1, 17),
                                             True, True)

            # Обработка прочих нажатых кнопок
            self.handle_input()

            # Прорисовка
            process_command(self.current_state.execute_before_draw())
            self.draw()
            process_command(self.current_state.execute_after_draw())

            # Временная проверка прохождения
            if self.current_state_type == StateType.MAZE and self.maze.check_win():
                running = False
            self.clock.tick(self.framerate)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Main()
    game.run()
