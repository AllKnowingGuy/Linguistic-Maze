import json, re
import os, random
from pathlib import Path
from mawo_pymorphy3 import create_analyzer

from main import Main
from src.level_building.enemy import Enemy
from util import Border, StateType, TILE_SIZE

intro_dialogue_path = Path('..\\assets\\data\\dialogues\\intro.json')
DEBUG_DIALOGUE_SKIP = False


existing_words_analyzer = create_analyzer()


def check_all_words_exist(text: str) -> bool:
    punctuation = r"""[\.,:;\?!<>\(\)\[\]"'&~]"""
    text = re.sub(punctuation, '', text).split()
    # TODO: probably make the check softer
    return all([1 in [form.score for form in existing_words_analyzer.parse(w)] for w in text])


class StoryScript:
    rooms_data: dict[int, dict[str, ...]]
    on_monster: Enemy | None

    """self.initiate_progress()
    self.launch_app(game)"""

    def __init__(self):
        self.current_room = -1
        self.attempts_left = 2
        self.total_respect = 0
        self.artifacts = set()
        self.player_name = None

        # Флаги игры в целом
        self.general_progress = {}

        # Монстр, с котором в данный момент встретился игрок
        self.on_monster = None

        # Параметры стояния перед дверью
        self.on_door = False
        self.current_door_code = None

        # Данные комнат (ключи - целочисленные идентификаторы комнат)
        self.rooms_data = {}

        self.initiate_progress()

    def initiate_progress(self):
        self.current_room = -1
        self.attempts_left = 2
        self.total_respect = 0
        self.artifacts = set()
        self.player_name = None
        self.rooms_data = {}

        self.general_progress = {
            'launched_app': False,
            'started_game': False,
            'passed_maze': False,
            'finished_outro': False,
        }

        # Внесение данных обо всех комнатах
        for i in range(5):
            with open(Path(f'..\\assets\\data\\rooms\\level_{i}.json'), 'r', encoding='utf-8') as f:
                raw_room = json.load(f)
            self.rooms_data[i] = {
                "difficulty": 0,
                "completed": False,
                "respect": 0,
                "sizes": raw_room["sizes"], # по сложностям
                "walls_with_doors": raw_room["walls_with_doors"], # НЕ зависит от сложности
                "other_entrance_coords": raw_room["other_entrance_coords"], # по сложностям
                "max_respect": raw_room["max_respect"], # НЕ зависит от сложности
                "respect_check": raw_room["respect_check"], # по сложностям
                "monsters": raw_room.get("monsters"), # координаты каждого монстра - по сложностям
                "artifacts_check": raw_room.get("artifacts_check"), # НЕ зависит от сложности
                "respect_check_w_artifacts": raw_room.get("respect_check_w_artifacts"), # по сложностям
                "code_check": raw_room.get("code_check"), # НЕ зависит от сложности
                "respect_check_w_code": raw_room.get("respect_check_w_code") # по сложностям
            }

    def update_game_progress(self, game: Main):
        """Проверяет и обновляет состояние игры в соответствии со скриптом"""

        # Когда игрок только начинает игру
        if not self.general_progress['launched_app']:
            self.launch_app(game)

        # Когда игрок в меню и нажал "Старт"
        elif game.current_state_type.name == StateType.MENU.name and game.menu_state.game_started:
            self.start_game(game)

        # Когда игрок на диалоге
        elif game.current_state_type.name == StateType.DIALOGUE.name:
            if DEBUG_DIALOGUE_SKIP and not self.current_room == -1:
                game.dialogue_state.finished = True

            # Собираем бонусы строчек из ЛЮБОГО диалога (в том числе из заскриптованных)
            self.collect_dialogue_bonuses(game)

            # Особые диалоги с заскриптованным поведением
            if self.current_room == -1:  # Интро: единственный диалог до начала лабиринта
                self.handle_intro_dialogue(game)

            elif self.on_monster:
                # Особые диалоги монстров

                if self.on_monster.enemy_name == 'monster_gloss':
                    # Выбор формы слова: "студентка" или "студент"
                    if game.dialogue_state.current_line_ind == 0 and self.player_name in ['Денис', 'Даня']:
                        game.dialogue_state.current_line_ind += 1

                elif self.on_monster.enemy_name == 'monster_amateur':
                    # Проверка введённого ответа
                    keywords = ('редукци', 'редуцир', 'позици', 'слаб', 'предударн')
                    if game.dialogue_state.current_line_ind == 2:
                        if not any([kw in game.dialogue_state.dialogue.saved_inputs.get(2, '') for kw in keywords]):
                            game.dialogue_state.current_line_ind += 1

                elif self.on_monster.enemy_name in ('monster_phontermin', 'monster_terminology'):
                    # Проверка намерений игрока (и того, что он говорит реальные слова)
                    keywords = ('практик', 'лингвист', 'наук', 'учен', 'учён', 'термин',
                                ('фонет' if self.on_monster.enemy_name == 'monster_phontermin' else 'социо'))
                    if game.dialogue_state.current_line_ind == 0:
                        response = game.dialogue_state.dialogue.saved_inputs.get(0, '')
                        if check_all_words_exist(response):
                            if any([kw in response for kw in keywords]):
                                # I'm gonna regret this - Vsevolod
                                game.dialogue_state.dialogue.lines[1]['rpoints'] = 2
                        else:
                            game.dialogue_state.current_line_ind += 2

            elif self.on_door:
                self.handle_door_dialogue(game)

            # По завершении стандартных диалогов
            if game.dialogue_state.finished and not self.current_room == -1:
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
                self.rooms_data[self.current_room]["respect"] += game.challenge_state.score
                supposed_end_dialogue = Path(
                    f'..\\assets\\data\\dialogues\\level_{self.current_room}\\{self.on_monster.enemy_name}_end.json'
                )

                # Если есть диалог после испытания - играем его
                if os.path.exists(supposed_end_dialogue):
                    game.current_state_type = StateType.DIALOGUE
                    game.dialogue_state.setup_dialogue(supposed_end_dialogue, game.challenge_state.score)
                    game.associate_current_state()
                    game.dialogue_state.start_playing()

                # Иначе - просто продолжаем лабиринт
                else:
                    game.current_state_type = StateType.MAZE
                    game.associate_current_state()
                    game.maze_state.make_alive()
                    game.maze_state.need_screen_update = True
                    if self.on_monster:
                        self.on_monster.deactivate()
                        self.on_monster = None

    def start_game(self, game: Main):
        self.general_progress['started_game'] = True
        game.current_state_type = StateType.DIALOGUE
        game.dialogue_state.setup_dialogue(intro_dialogue_path)
        game.dialogue_state.story_mode = True
        game.associate_current_state()
        game.dialogue_state.start_playing()

    def launch_app(self, game: Main):
        self.general_progress['launched_app'] = True
        game.current_state_type = StateType.MENU
        game.associate_current_state()
        game.menu_state.need_screen_update = True

    """
    Проверки заскриптованных диалогов
    """

    def handle_intro_dialogue(self, game: Main):
        # Когда игрок отвечает на вопрос тестового вступления

        """if DEBUG_DIALOGUE_SKIP:
            game.dialogue_state.finished = True
            self.intro_progress['said_yes'] = True"""

        # Когда игрок выбирает персонажа
        if game.dialogue_state.current_line_ind == 5:
            chosen_name = game.dialogue_state.dialogue.saved_choices.get(5)
            if chosen_name:
                self.player_name = chosen_name
                game.dialogue_state.left_name = chosen_name
                game.dialogue_state.left_speaker_name_sprite = game.dialogue_state.dialogue_font.render(
                    chosen_name, True, (255, 255, 255)
                )
                game.dialogue_state.right_speaker_name_sprite = game.dialogue_state.dialogue_font.render(
                    game.dialogue_state.dialogue.right_character, True, (255, 255, 255)
                )

        # Когда игрок завершает тестовое вступление
        if game.dialogue_state.finished:
            game.dialogue_state.story_mode = False
            self.generate_next_room(game, 0)

    """
    Проверки остальных диалогов
    """

    def handle_monster_dialogue_finish(self, game: Main):
        """Действия при завершении диалога с монстром"""

        # Если после встречи должно начаться испытание - запускаем
        if (game.dialogue_state.dialogue.starts_challenge
                and not game.dialogue_state.dialogue.get_line_challenge_cancel(game.dialogue_state.current_line_ind)):
            game.current_state_type = StateType.CHALLENGE
            game.challenge_state.setup_challenge(Path(
                f'..\\assets\\data\\challenges\\level_{self.current_room}\\'
                f'{self.on_monster.enemy_name}.json'
            ))
            game.associate_current_state()
            game.challenge_state.start_start_anim()

        # Иначе - простое продолжение лабиринта
        else:
            game.current_state_type = StateType.MAZE
            game.associate_current_state()
            game.maze_state.make_alive()
            self.on_monster.deactivate()
            self.on_monster = None

    def handle_door_dialogue(self, game: Main):
        """Действия во время диалога с дверью выхода"""

        # Ввод кода и его проверка
        if game.dialogue_state.current_line == ["Тогда введи код!"]:
            code_guess = game.dialogue_state.dialogue.saved_inputs.get(game.dialogue_state.current_line_ind, "")
            if code_guess != self.current_door_code:
                game.dialogue_state.current_line_ind += (1 if self.attempts_left > 0 else 2)

        # Выбор поискать монстров или воссоздать комнату
        fate_text = "Что ж, ступай, поищи ещё монстров, выполни мои требования и возвращайся!"
        if game.dialogue_state.current_line == [fate_text]:
            fate = game.dialogue_state.dialogue.saved_choices.get(game.dialogue_state.current_line_ind, "Пойду поищу")
            if fate == "Никак не могу найти...":
                game.dialogue_state.current_line_ind += (0 if self.attempts_left > 0 else 1)

    def handle_dialogue_finish(self, game: Main):
        """Выбор действия после конца диалога"""

        # Если это встреча с монстром
        if self.on_monster:
            self.handle_monster_dialogue_finish(game)

        # Если это диалог двери выхода
        elif self.on_door:
            line_ind = game.dialogue_state.current_line_ind
            if game.dialogue_state.dialogue.get_line_room_switch(line_ind):
                self.generate_next_room(game)
            elif game.dialogue_state.dialogue.get_line_room_restart(line_ind):
                self.restart_current_room(game)
            elif game.dialogue_state.dialogue.get_line_gameover(line_ind):
                game.menu_state.just_lost = True
                game.menu_state.game_end_score = self.total_respect + sum(
                    room["respect"] for _, room in self.rooms_data.items()
                )
                game.menu_state.game_end_artifacts = self.artifacts
                self.initiate_progress()
                self.launch_app(game)
            else:
                game.current_state_type = StateType.MAZE
                game.associate_current_state()
                # Выдвигаем игрока из двери
                game.maze_state.player_pos = [int((game.maze_state.maze.end.x + 0.5) * TILE_SIZE),
                                              int((game.maze_state.maze.end.y + 0.5) * TILE_SIZE)]
                game.maze_state.make_alive()

            self.on_door = False
            game.dialogue_state.story_mode = False

    def collect_dialogue_bonuses(self, game: Main):
        """Сбор респектов и артефактов по строчкам"""

        line_ind = game.dialogue_state.current_line_ind
        respect = game.dialogue_state.dialogue.get_line_respect_points(line_ind)
        artifact = game.dialogue_state.dialogue.get_line_artifact(line_ind)

        if not game.dialogue_state.dialogue.collected_respect_points.get(line_ind, False):
            if self.current_room in self.rooms_data:
                self.rooms_data[self.current_room]["respect"] += respect
            else:
                self.total_respect += respect
            game.dialogue_state.dialogue.record_collected_respect_points(line_ind)
            # print(f"GOT {respect} RESPECT AND RECORDED {game.dialogue_state.dialogue.collected_respect_points}")
        if artifact:
            self.artifacts.add(artifact)

    """
    Проверки уровней лабиринта
    """

    def handle_monster_encounter(self, game, supposed_monster):
        """Загрузка диалога с монстром при столкновении"""

        self.on_monster = supposed_monster
        game.current_state_type = StateType.DIALOGUE
        game.dialogue_state.setup_dialogue(Path(
            f'..\\assets\\data\\dialogues\\level_{self.current_room}\\{supposed_monster.enemy_name}.json'
        ))
        game.associate_current_state()
        game.dialogue_state.start_playing()

    def handle_room_exit(self, game: Main):
        """Проверка выхода из комнаты"""

        if self.current_room in self.rooms_data:
            room_data = self.rooms_data[self.current_room]
        else:
            raise ValueError(f"This room was not initiated: {self.current_room}")
        self.on_door = True

        door_dialogue = self.make_door_interaction(room_data)
        game.current_state_type = StateType.DIALOGUE
        game.dialogue_state.story_mode = True
        game.dialogue_state.setup_dialogue(door_dialogue)
        game.associate_current_state()
        game.dialogue_state.start_playing()

    def make_door_interaction(self, room_data):
        """Проверка респектов/артефактов для выхода"""

        # Преобразование сложности в словесный вид
        difficulty = room_data["difficulty"]
        diff_word = ("easy", "medium", "hard")[difficulty]

        # Получение требований двери
        respect_req = room_data["respect_check"][diff_word]

        if room_data["artifacts_check"] and room_data["respect_check_w_artifacts"]:
            artifacts_req = room_data["artifacts_check"]
            respect_req_w_artifacts = room_data["respect_check_w_artifacts"][diff_word]
        else:
            artifacts_req = None
            respect_req_w_artifacts = None

        if room_data["code_check"] and room_data["respect_check_w_code"]:
            code_req = room_data["code_check"]
            respect_req_w_code = room_data["respect_check_w_code"][diff_word]
        else:
            code_req = None
            respect_req_w_code = None
        self.current_door_code = code_req

        # Получение собранных респектов
        respect = room_data["respect"]  # I made sure there are such attributes in rooms_data - Vsevolod

        # Проверка всех 3 способов прохода через дверь
        scored_respect, got_artifact, scored_discounted_respect, can_enter_code = self.check_room_exit_conditions(
            respect, respect_req, artifacts_req, respect_req_w_artifacts, respect_req_w_code)

        # Постройка диалога
        door_dialogue = {"lines": []} # минимальный диалог, из уникального только задний фон двери
        stop_building = False

        if scored_respect:
            door_dialogue["lines"].append(
                {
                    "text": f"Чтобы пройти через меня, требуется заслужить респект монстров на уровне {respect_req} или выше.\n"
                            f"Ты заслужил {respect} и справился с задачей.",
                    "bg": "doorbg.png"
                }
            )
            stop_building = True
        else:
            door_dialogue["lines"].append(
                {
                    "text": f"Чтобы пройти через меня, требуется заслужить респект монстров на уровне {respect_req} или выше.\n"
                            f"Ты заслужил всего {respect}, человек.",
                    "bg": "doorbg.png"
                }
            )

        if not stop_building and artifacts_req and got_artifact:
            door_dialogue["lines"].append(
                {
                    "text": f"Но у тебя в инвентаре {
                    f"лежит {artifacts_req[0]}" if len(artifacts_req) == 1 else 
                    f"лежат {", ".join(artifacts_req[:-1])} и {artifacts_req[-1]}"
                    }.\nЗа твою находку я сделаю тебе скидку на респект: теперь достаточно набрать {respect_req_w_artifacts}."
                }
            )
            if scored_discounted_respect:
                door_dialogue["lines"].append(
                    {"text": "И в этот раз твоего респекта хватит."}
                )
                stop_building = True
        elif not stop_building and artifacts_req:
            door_dialogue["lines"].append(
                {
                    "text": f"Но если тебе {
                    f"попадётся {artifacts_req[0]}" if len(artifacts_req) == 1 else 
                    f"попадутся {", ".join(artifacts_req[:-1])} и {artifacts_req[-1]}"
                    }, и ты {"этот предмет" if len(artifacts_req) == 1 else "эти предметы"} "
                            f"принесёшь сюда,\nто я сделаю тебе скидку на респект."
                }
            )

        if not stop_building and code_req and can_enter_code:
            door_dialogue["lines"].extend([
                {
                    "text": f"Впрочем, если ты знаешь мой секретный код, то минимальный уровень респекта будет "
                            f"{respect_req_w_code}. И твоего респекта хватит.\n"
                            f"Готов ввести код? Предупреждаю: у тебя на это 1 попытка!",
                    "action": {
                        "type": "choosefrom",
                        "options": ["Да", "Нет"],
                        "jumps": [None, len(door_dialogue["lines"]) + 5]
                    }
                },
                {
                    "text": "Тогда введи код!",
                    "action": {"type": "savetyped"}
                },
                {
                    "text": "Код верный! Проходи, человек!",
                    "bg": "dooropenbg.png",
                    "jump": -1,
                    "nextroom": True
                },
                {
                    "text": f"Код неверный!\nТеперь тебе придётся пройти комнату заново, но она будет воссоздана. "
                            f"После этого у тебя останется "
                            f"{f"1 воссоздание!" if self.attempts_left >= 2 else f"0 воссозданий!"}",
                    "jump": -1,
                    "restartroom": True
                },
                {
                    "text": "Код неверный!\nВоссоздать комнату больше нельзя, так что дальше тебе дороги нет!",
                    "music": "STOP",
                    "jump": -1,
                    "gameover": True
                }
            ])
        elif not stop_building and code_req:
            door_dialogue["lines"].append(
                {
                    "text": f"Впрочем, если ты знаешь мой секретный код, "
                            f"то минимальный уровень респекта будет {respect_req_w_code}."
                }
            )

        if scored_respect or scored_discounted_respect:
            door_dialogue["lines"].extend([
                {
                    "text": "Готов попасть в следующую комнату?",
                    "action": {
                        "type": "choosefrom",
                        "options": ["Да", "Нет"],
                        "jumps": [None, len(door_dialogue["lines"]) + 2]
                    }
                },
                {
                    "text": "Тогда проходи, человек!",
                    "bg": "dooropenbg.png",
                    "jump": -1,
                    "nextroom": True
                },
                {
                    "text": "Тогда возвращайся, когда будешь готов. И не растрать респект!",
                    "jump": -1
                }
            ])
        else:
            door_dialogue["lines"].extend([
                {
                    "text": "Что ж, ступай, поищи ещё монстров, выполни мои требования и возвращайся!",
                    "action": {
                        "type": "choosefrom",
                        "options": ["Пойду поищу", "Никак не могу найти..."],
                        "jumps": [-1, None]
                    }
                },
                {
                    "text": f"Прискорбно! Придётся воссоздать комнату, чтобы пройти её ещё раз.\n"
                            f"После этого у тебя останется "
                            f"{f"1 воссоздание!" if self.attempts_left >= 2 else f"0 воссозданий!"}",
                    "jump": -1,
                    "restartroom": True
                },
                {
                    "text": "Прискорбно! Воссоздать комнату больше нельзя, так что дальше тебе дороги нет!",
                    "music": "STOP",
                    "jump": -1,
                    "gameover": True
                }
            ])

        return door_dialogue

    def check_room_exit_conditions(self, respect, respect_req,
                                   artifacts_req = None, respect_req_w_artifacts = None,
                                   respect_req_w_code = None):
        scored_respect = got_artifact = scored_discounted_respect = can_enter_code = False
        if respect >= respect_req:
            scored_respect = True
        if artifacts_req is not None and all([artifact in self.artifacts for artifact in artifacts_req]):
            got_artifact = True
            if respect_req_w_artifacts is not None and respect >= respect_req_w_artifacts:
                scored_discounted_respect = True
        if respect_req_w_code is not None and respect >= respect_req_w_code:
            can_enter_code = True
        return scored_respect, got_artifact, scored_discounted_respect, can_enter_code

    def prepare_room_gen_data(self, diff_word: str):
        room_data = self.rooms_data[self.current_room]

        # Размер комнаты
        sizes = room_data.get("sizes", {"easy": (31, 19), "medium": (31, 25), "hard": (37, 37)})
        w, h = sizes[diff_word]

        # Определение стен с дверьми
        walls_with_doors = room_data.get("walls_with_doors", {"entrance": "west", "exit": "east"})
        string_entrance = walls_with_doors["entrance"]
        string_exit = walls_with_doors["exit"]
        enum_entrance = (Border.NORTH if string_entrance == "north"
                         else Border.SOUTH if string_entrance == "south"
                         else Border.WEST if string_entrance == "west"
                         else Border.EAST)
        enum_exit = (Border.NORTH if string_exit == "north"
                     else Border.SOUTH if string_exit == "south"
                     else Border.WEST if string_exit == "west"
                     else Border.EAST)

        # Определение координаты двери выхода в её стене
        entrance_coords = room_data.get("other_entrance_coords", {"easy": 9, "medium": 13, "hard": 19})
        en_coord = entrance_coords[diff_word]
        ex_coord = (random.choice(range(1, h - 1, 2))
                    if enum_entrance in (Border.WEST, Border.EAST)
                    else random.randrange(1, w - 1, 2))
        # входная дверь в одном и том же месте, дверь выхода в разных, но всегда в одной стене

        # Выбор областей генерации монстров по сложности
        raw_monster_dict = room_data.get("monsters", {})
        processed_monster_dict = {}
        for monster, areas in raw_monster_dict.items():
            processed_monster_dict[monster] = tuple(areas[diff_word])

        return w, h, enum_entrance, enum_exit, en_coord, ex_coord, processed_monster_dict

    def restart_current_room(self, game: Main):
        """Рестарт текущей комнаты при провале"""

        # Трата попытки и сброс респекта
        self.attempts_left -= 1
        self.rooms_data[self.current_room]["respect"] = 0

        # Подготовка данных для установки лабиринта
        w, h, enum_entrance, enum_exit, en_coord, ex_coord, processed_monster_dict = self.prepare_room_gen_data(
            ("easy", "medium", "hard")[self.rooms_data[self.current_room].get("difficulty", 0)]
        )

        # Переключение состояния и генерация лабиринта
        game.current_state_type = StateType.MAZE
        game.maze_state.setup_maze(w, h,
                                   (enum_entrance, enum_exit), (en_coord, ex_coord),
                                   monster_dict=processed_monster_dict,
                                   more_random=True, curving=True)
        game.associate_current_state()
        game.maze_state.make_alive()

    def generate_next_room(self, game: Main, set_difficulty: int | None = None):
        """Генерация новой комнаты"""

        # Данные предыдущей комнаты и определение сложности следующей
        if set_difficulty is None:
            prev_room_data = self.rooms_data[self.current_room]
            prev_difficulty = prev_room_data["difficulty"]
            prev_diff_word = ("easy", "medium", "hard")[prev_difficulty]
            min_respects = prev_room_data["respect_check"][prev_diff_word]
            max_respects = prev_room_data["max_respect"]
            relative_respects = prev_room_data["respect"] - min_respects
            respect_span = max_respects - min_respects + 1
            if relative_respects < respect_span // 3:
                difficulty = 0 # легко
            elif relative_respects >= (respect_span * 2) // 3:
                difficulty = 2 # сложно
            else:
                difficulty = 1 # средне
        else:
            difficulty = set_difficulty
        diff_word = ("easy", "medium", "hard")[difficulty]

        # Продвижение на одну комнату и установка сложности
        self.current_room = min(self.current_room + 1, 2)  # временное ограничение на максимальный уровень
        self.rooms_data[self.current_room]["difficulty"] = difficulty

        # Подготовка данных для установки лабиринта
        w, h, enum_entrance, enum_exit, en_coord, ex_coord, processed_monster_dict = self.prepare_room_gen_data(
            diff_word
        )

        # Переключение состояния и генерация лабиринта
        game.current_state_type = StateType.MAZE
        game.maze_state.set_level(self.current_room)
        game.maze_state.setup_maze(w, h,
                                   (enum_entrance, enum_exit), (en_coord, ex_coord),
                                   monster_dict=processed_monster_dict,
                                   more_random=True, curving=True)
        game.associate_current_state()
        game.maze_state.make_alive()
