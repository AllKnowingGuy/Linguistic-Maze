#from Main import Main
from Util import Border, StateType


# Для тестирования: 1-й диалог
intro_dialogue_text = """left\tnoaction\tЯ студент и я пришёл в лабиринт; только не знаю, что делать(
right\tnoaction\tА я монстр, но я пока не знаю, как меня зовут.
left\tnoaction\tО, зато я знаю, сейчас скажу)
nochar\tsavetyped\tА как зовут монстра? Напишите ответ: внизу появилось поле ввода
right\tnoaction\tО, прикольно, спасибо ^-^
right\tchoosefrom{Да, Нет}\tТак говоришь, хочешь пройти лабиринт?
right\tnoaction\tНу тогда заходи!
left\tnoaction\tНе, что-то не хочу пока. Но было приятно познакомиться!"""


# Для тестирования: 2-й диалог
transition_dialogue_text = """right\tnoaction\tА что так быстро? Я текст не успел подготовить...\tprevscreen
left\tnoaction\tПравда быстро? Я вообще не заметил, как дошёл до конца.
right\tnoaction\tЛадно, вот тебе ещё комната.
right\tnoaction\tСлегка похожа на предыдущую, но пока это всё, что есть("""


# Для тестирования: 3-й диалог
outro_dialogue_text = """left\tnoaction\tУра, прошёл!\tprevscreen
right\tnoaction\tХорош, я не сомневался(ась) в тебе!
right\tchoosefrom{Да, Нет}\tА ты знал, что игра теперь поддерживает смену диалогов?
right\tnoaction\tНе переживай, в этом вопросе не было ложной презумпции ;)
left\tsavetyped\tЛадно, дай-ка я оставлю отзыв на лабиринт.
left\tnoaction\tЯ всё, а теперь мне пора бежать.
right\tnoaction\tНу давай, пока!"""


class StoryScript:
    def __init__(self):
        self.current_level = 0  # 0=вступление, 1=лабиринт, 2=финал
        self.total_respect = 0
        self.artifacts = []
        self.player_name = None
        self.rooms_progress = {}  # {room_id: {'respect': 0, 'completed': False}}
        self.current_room_id = None

        # Сохраняем старое для совместимости
        self.general_progress = {
            'started_game': False, 'finished_intro': False,
            'passed_maze': False, 'finished_outro': False
        }
        self.intro_progress = {'answered_question': False, 'said_yes': False, 'said_no': False}

    def update_game_progress(self, game):
        """Проверяет и обновляет состояние игры в соответствии со скриптом"""

        if not self.general_progress['started_game']:
            self.on_game_start(game)

    def on_game_start(self, game):
        self.general_progress['started_game'] = True
        game.current_state_type = StateType.DIALOGUE
        self.intro = game.dialogue_manager.setup_dialogue(intro_dialogue_text.split('\n'), 'Говорящий монстр')
        game.associate_current_state()

    """
    Проверки диалогов
    """

    def on_intro_dialogue(self, game):
        # Когда игрок отвечает на вопрос тестового вступления
        if not self.intro_progress['answered_question']:
            intro_choice = game.dialogue_manager.dialogue.saved_choices.get("Так говоришь, хочешь пройти лабиринт?")
            if intro_choice == 'Да':
                game.dialogue_manager.advance(jump_to=6)
                self.intro_progress['said_yes'] = True
                self.intro_progress['answered_question'] = True
            elif intro_choice == 'Нет':
                game.dialogue_manager.advance(jump_to=7)
                self.intro_progress['said_no'] = True
                self.intro_progress['answered_question'] = True

        # Когда диалог показал линию "Ну тогда заходи!" и должен завершиться
        if self.intro_progress['said_yes'] and game.dialogue_manager.current_line_ind > 6:
            game.dialogue_manager.finished = True

        # Когда игрок завершает тестовое вступление
        if game.dialogue_manager.finished:
            # Если игрок выбрал "Да" - переход к лабиринту
            if self.intro_progress['said_yes']:
                self.general_progress['finished_intro'] = True
                game.current_state_type = StateType.MAZE
                game.maze_manager.set_level(self.current_level)
                self.room_1 = game.maze_manager.setup_maze(31, 19, (Border.WEST, Border.EAST), (1, 17), True, True)
                game.associate_current_state()
            # Если игрок выбрал "Нет" - завершение игры
            elif self.intro_progress['said_no']:
                game.running = False

    def on_monster_dialogue(self, game):
        if game.dialogue_manager.finished:
            self.handle_room_exit(game)

    def on_dynamic_maze_level(self, game):
        if game.maze_manager.check_win():
            self.handle_room_exit(game)

    def check_room_exit_conditions(self, room_data):
        """Проверяет респекты/артефакты для выхода"""
        respect = room_data.get('respect', 0)
        difficulty = int(self.current_room_id.split('_')[1])

        # Условия по сложности:
        respect_req = [5, 2, 5][difficulty]  # 0=5, 1=2, 2=5 респектов

        print(f"Комната {self.current_room_id}: {respect}/{respect_req} респектов")
        return respect >= respect_req

    def restart_current_room(self, game):
        """Рестарт текущей комнаты при провале"""
        print(f"Нужны респекты для {self.current_room_id}")
        # Пока просто следующая комната (потом рестарт)
        self.generate_next_room(game)

    def handle_room_exit(self, game):
        """Проверяет выход из ЛЮБОЙ комнаты"""
        room_data = self.rooms_progress[self.current_room_id]

        if self.check_room_exit_conditions(room_data):
            self.generate_next_room(game)
        else:
            self.restart_current_room(game)

    def generate_next_room(self, game):
        """Генерирует новую комнату"""
        self.current_level = min(self.current_level + 1, 2)
        self.current_room_id = f"room_{self.current_level}"  # "room_1", "room_2", ...

        sizes = [(31, 19), (25, 31), (20, 25)]  # 0=легко, 1=средне, 2=сложно
        w, h = sizes[self.current_level]

        game.current_state_type = StateType.MAZE
        game.maze_manager.set_level(self.current_level)
        game.maze_manager.setup_maze(w, h, (Border.WEST, Border.EAST), (1, h - 2), True, True)
        game.associate_current_state()
