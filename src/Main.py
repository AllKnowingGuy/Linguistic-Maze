import pygame
import sys
from enum import Enum

from playstates import MazeState
# импортируйте другие состояния через запятую
from Util import Border


# Константы
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 650
# TODO: make camera move along with the character for mazes that exceed screen bounds


class State(Enum):
    MAZE = 1
    DIALOGUE = 2
    CHALLENGE = 3


# Инициализация Pygame
pygame.init()


class Main:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Лингвист в лабиринте")
        self.clock = pygame.time.Clock()

        self.maze = MazeState.MazeState()
        # добавляйте другие состояния таким же образом (не забудьте об уважении к другим, давая названия переменным)
        self.maze.setup_maze(31, 19,
                             (Border.WEST, Border.EAST),
                             (1, 17),
                             True, True)

        self.current_state = State.MAZE

    def handle_input(self):
        """Обработка ввода с клавиатуры"""
        # TODO: create customizable keybinds
        keys = pygame.key.get_pressed()

        if self.current_state == State.MAZE:
            self.maze.handle_input(keys)
        # в блоке elif можете подключить другие состояния таким же образом, как и MAZE

    def draw(self):
        """Отрисовка игры"""
        self.screen.fill((0, 0, 0))

        if self.current_state == State.MAZE:
            self.maze.draw(self.screen)
        # в блоке elif можете подключить другие состояния таким же образом, как и MAZE

        pygame.display.flip()

    def run(self):
        """Главный цикл игры"""
        self.maze.precalculate_walls()

        clock = pygame.time.Clock()
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    # TODO: disable or reimplement under a different event
                    elif event.key == pygame.K_r:
                        self.maze.setup_maze(31, 19,
                                             (Border.WEST, Border.EAST),
                                             (1, 17),
                                             True, True)
                        self.maze.wall_cache.clear()
                        self.maze.precalculate_walls()

            self.handle_input()
            self.draw()
            if self.maze.check_win():
                running = False
            clock.tick(10)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Main()
    game.run()
