import os, random

#from Main import Main
from Util import Border, StateType


intro_dialogue_path = '..\\assets\\data\\dialogues\\intro.json'
DEBUG_DIALOGUE_SKIP = False


class StoryScript:
    def __init__(self):
        self.current_room = -1
        self.last_passed_room = -1
        self.general_progress = {
            'started_game': False,
            'passed_maze': False,
            'finished_outro': False,
        }

        # Монстр, с котором в данный момент встретился игрок
        self.on_monster = None

        # Данные комнат (ключи - целочисленные идентификаторы комнат)
        self.rooms_data = {
            0: {
                "difficulty": 0,
                "sizes": [(29, 25), (37, 29), (37, 37)],
                "walls_with_doors": (Border.SOUTH, Border.NORTH),
                "other_entrance_coords": [15, 19, 19],
                "completed": False,
                "respect": 0
            },
            1: {
                "difficulty": 0,
                "sizes": [(29, 25), (37, 29), (37, 37)],
                "walls_with_doors": (Border.SOUTH, Border.NORTH),
                "other_entrance_coords": [15, 19, 19],
                "completed": False,
                "respect": 0
            }
        }

        # Прогресс по разделам игры
        self.intro_progress = {
            'answered_question': False,
            'said_no': False
        }

    def update_game_progress(self, game):
        """Проверяет и обновляет состояние игры в соответствии со скриптом"""

        # Когда игрок только начинает игру
        if not self.general_progress['started_game']:
            self.start_game(game)

        # Когда игрок на диалоге
        elif game.current_state_type.name == StateType.DIALOGUE.name:
            if DEBUG_DIALOGUE_SKIP and not self.current_room == -1:
                game.dialogue_state.finished = True

            # Особые диалоги с сильно заскриптованным поведением
            if self.current_room == -1: # Интро: единственный диалог до начала лабиринта
                self.handle_intro_dialogue(game)

            # По завершении стандартных диалогов
            elif game.dialogue_state.finished:
                self.handle_dialogue_finish(game)

        # Когда игрок в лабиринте
        elif game.current_state_type.name == StateType.MAZE.name:

            # Если встретился с монстром
            supposed_monster = game.maze_state.check_enemy_collision()
            if supposed_monster:
                self.handle_monster_encounter(game, supposed_monster)

            # Когда прошёл уровень
            elif game.maze_state.check_win():
                self.handle_room_exit(game)

        # Когда игрок на испытании
        elif game.current_state_type.name == StateType.CHALLENGE.name:

            # Конец испытания
            if game.challenge_state.finished:
                game.current_state_type = StateType.MAZE
                game.associate_current_state()
                game.maze_state.needs_screen_update = True
                self.on_monster.active = False
                self.on_monster = None

    def start_game(self, game):
        self.general_progress['started_game'] = True
        game.current_state_type = StateType.DIALOGUE
        game.dialogue_state.setup_dialogue(intro_dialogue_path)
        game.associate_current_state()
        game.dialogue_state.start_playing()

    """
    Проверки заскриптованных диалогов
    """

    def handle_intro_dialogue(self, game):
        # Когда игрок отвечает на вопрос тестового вступления
        if game.dialogue_state.current_line_ind > 5 and not self.intro_progress['answered_question']:
            intro_choice = game.dialogue_state.dialogue.saved_choices.get("Так говоришь, хочешь пройти лабиринт?")
            if intro_choice:
                if intro_choice == 'Нет':
                    self.intro_progress['said_no'] = True
                self.intro_progress['answered_question'] = True

        if DEBUG_DIALOGUE_SKIP:
            game.dialogue_state.finished = True
            self.intro_progress['said_yes'] = True

        # Когда игрок завершает тестовое вступление
        if game.dialogue_state.finished:
            # Если игрок выбрал "Нет" - завершение игры
            if self.intro_progress['said_no']:
                game.running = False
                return
            self.generate_next_room(game)

    """
    Проверки остальных диалогов
    """

    def handle_dialogue_finish(self, game):
        """Выбор действия после конца диалога"""

        # Если это встреча с монстром
        if self.on_monster:

            # Собираем бесплатные респекты, если они предусмотрены
            self.rooms_data[self.current_room]["respect"] += game.dialogue_state.dialogue.respect_points

            # Если после встречи должно начаться испытание
            if game.dialogue_state.dialogue.starts_challenge:
                game.current_state_type = StateType.CHALLENGE
                game.challenge_state.setup_challenge(
                    f'..\\assets\\data\\challenges\\level_{self.current_room}\\'
                    f'{self.on_monster.enemy_name}.json'
                )
                game.associate_current_state()
                game.challenge_state.start_start_anim()

            # Иначе - простое продолжение лабиринта
            else:
                game.current_state_type = StateType.MAZE
                game.associate_current_state()
                self.on_monster.active = False
                self.on_monster = None

        # Если это диалог двери выхода
        elif self.last_passed_room == self.current_room:
            if self.current_room == 1:
                # Особый случай для диалога последней комнаты
                game.running = False
            self.generate_next_room(game)

    """
    Проверки уровней лабиринта
    """

    def handle_monster_encounter(self, game, supposed_monster):
        """Загрузка диалога с монстром при столкновении"""

        self.on_monster = supposed_monster
        game.current_state_type = StateType.DIALOGUE
        game.dialogue_state.setup_dialogue(
            f'..\\assets\\data\\dialogues\\level_{self.current_room}\\{supposed_monster.enemy_name}.json'
        )
        game.associate_current_state()
        game.dialogue_state.start_playing()

    def handle_room_exit(self, game):
        """Проверка выхода из комнаты"""

        room_data = self.rooms_data[self.current_room]
        if self.check_room_exit_conditions(room_data):
            self.last_passed_room = self.current_room
            supposed_dialogue_path = f'..\\assets\\data\\dialogues\\level_{self.current_room}\\exit_door.json'

            # Если у текущей двери выхода существует диалог
            if os.path.exists(supposed_dialogue_path):
                game.current_state_type = StateType.DIALOGUE
                game.dialogue_state.setup_dialogue(supposed_dialogue_path)
                game.associate_current_state()
                game.dialogue_state.start_playing()
            else:
                self.generate_next_room(game)
        else:
            self.restart_current_room(game)

    def check_room_exit_conditions(self, room_data):
        """Проверка респектов/артефактов для выхода"""

        respect = room_data.get("respect", 0)
        difficulty = room_data.get("difficulty", 0)

        # Условия по сложности:
        respect_req = (0, 0, 0)[difficulty] # 0=5, 1=2, 2=5 респектов, временно отключены

        print(f"Комната {self.current_room}: {respect}/{respect_req} респектов")
        return respect >= respect_req

    def restart_current_room(self, game):
        """Рестарт текущей комнаты при провале"""

        print(f"Нужны респекты для {self.current_room}")
        # Пока просто следующая комната (потом рестарт)
        self.generate_next_room(game)

    def generate_next_room(self, game):
        """Генерация новой комнаты"""

        # Продвижение на одну комнату и извлечение данных
        self.current_room = min(self.current_room + 1, 1) # временное ограничение на максимальный уровень
        room_data = self.rooms_data[self.current_room]

        difficulty = random.randint(0, 2) # 0=легко, 1=средне, 2=сложно
        # random difficulty for now - Vsevolod

        # Размер комнаты
        sizes = room_data.get("sizes", [(31, 19), (31, 25), (37, 37)])
        w, h = sizes[difficulty]

        walls_with_doors = room_data.get("walls_with_doors", (Border.WEST, Border.EAST))

        entrance_coords = room_data.get("other_entrance_coords", [9, 13, 19])
        en_coord = entrance_coords[difficulty]
        ex_coord = (random.choice(range(1, h - 1, 2))
                    if walls_with_doors[1] in (Border.WEST, Border.EAST)
                    else random.choice(range(1, w - 1, 2)))

        game.current_state_type = StateType.MAZE
        game.maze_state.set_level(self.current_room)
        game.maze_state.setup_maze(w, h, walls_with_doors, (en_coord, ex_coord), True, True)
        game.associate_current_state()
