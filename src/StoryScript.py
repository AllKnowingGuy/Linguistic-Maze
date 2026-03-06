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
        self.current_level = 1 # Используется для применения подходящего скина к комнате
        self.general_progress = {
            'started_game': False,
            'finished_intro': False,
            'level_1_completed': False,
            'finished_transition': False,
            'level_2_completed': False,
            'passed_maze': False,
            'finished_outro': False,
        }

        # Объекты в порядке следования
        self.intro = None
        self.room_1 = None
        self.transition = None
        self.room_2 = None
        self.outro = None

        # Прогресс по разделам игры
        self.intro_progress = {
            'answered_question': False,
            'said_yes': False,
            'said_no': False,
        }

    def update_game_progress(self, game):
        """Проверяет и обновляет состояние игры в соответствии со скриптом"""

        # Когда игрок только начинает игру
        if not self.general_progress['started_game']:
            self.on_game_start(game)

        # Когда игрок на диалоге
        if game.current_state_type.name == StateType.DIALOGUE.name:
            # Вступление
            if self.general_progress['started_game'] and game.dialogue_manager.dialogue is self.intro:
                self.on_intro_dialogue(game)
            # Промежуточный диалог
            elif self.general_progress['level_1_completed'] and game.dialogue_manager.dialogue is self.transition:
                self.on_transition_dialogue(game)
            # Концовка
            elif self.general_progress['passed_maze'] and game.dialogue_manager.dialogue is self.outro:
                self.on_outro_dialogue(game)

        # Когда игрок в лабиринте
        if game.current_state_type.name == StateType.MAZE.name:
            # 1-я комната
            if self.general_progress['finished_intro'] and game.maze_manager.maze is self.room_1:
                self.on_first_maze_level(game)
            # 2-я комната
            elif self.general_progress['finished_transition'] and game.maze_manager.maze is self.room_2:
                self.on_second_maze_level(game)

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

    def on_transition_dialogue(self, game):
        # Когда игрок завершает промежуточный диалог
        if game.dialogue_manager.finished:
            self.general_progress['finished_transition'] = True
            game.current_state_type = StateType.MAZE
            game.maze_manager.set_level(self.current_level)
            self.room_2 = game.maze_manager.setup_maze(25, 31, (Border.EAST, Border.WEST), (1, 29), True, True)
            game.associate_current_state()

    def on_outro_dialogue(self, game):
        # Когда игрок завершает тестовую концовку
        if game.dialogue_manager.finished:
            self.general_progress['finished_outro'] = True
            game.running = False

    """
    Проверки уровней лабиринта (Все комнаты уникальные, поэтому проводим свою проверку для каждого уровня)
    """

    def on_first_maze_level(self, game):
        # Когда игрок прошёл уровень - переход к промежуточному диалогу
        if game.maze_manager.check_win():
            self.general_progress['level_1_completed'] = True
            self.current_level += 1
            game.current_state_type = StateType.DIALOGUE
            self.transition = game.dialogue_manager.setup_dialogue(transition_dialogue_text.split('\n'), 'Говорящий монстр')
            game.associate_current_state()

    def on_second_maze_level(self, game):
        # Когда игрок прошёл уровень - переход к концовке
        if game.maze_manager.check_win():
            self.general_progress['level_2_completed'] = True
            self.general_progress['passed_maze'] = True
            game.current_state_type = StateType.DIALOGUE
            self.outro = game.dialogue_manager.setup_dialogue(outro_dialogue_text.split('\n'), 'Говорящий монстр')
            game.associate_current_state()
