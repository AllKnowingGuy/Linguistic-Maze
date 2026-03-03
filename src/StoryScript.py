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
outro_dialogue_text = """left\tnoaction\tУра, прошёл!
right\tnoaction\tХорош, я не сомневался(ась) в тебе!
right\tchoosefrom{Да, Нет}\tА ты знал, что игра теперь поддерживает смену диалогов?
right\tnoaction\tНе переживай, в этом вопросе не было ложной презумпции ;)
left\tsavetyped\tЛадно, дай-ка я оставлю отзыв на лабиринт.
left\tnoaction\tЯ всё, а теперь мне пора бежать.
right\tnoaction\tНу давай, пока!"""


class StoryScript:
    def __init__(self):
        self.progress = {
            'started_game': False,
            'answered_intro_question': False,
            'finished_intro': False,
            'passed_maze': False,
            'finished_outro': False
        }

        # Объекты в порядке следования
        self.intro = None
        self.maze = None
        self.outro = None

        # Проверки
        # TODO: make a dict of these?
        self.intro_said_yes = False
        self.intro_said_no = False

    def update_game_progress(self, game): # TODO: split checks into functions
        """Проверяет и обновляет состояние игры в соответствии со скриптом"""

        # Когда игрок только начинает игру
        if not self.progress['started_game']:
            game.current_state_type = StateType.DIALOGUE
            self.intro = game.dialogue_manager.setup_dialogue(intro_dialogue_text.split('\n'), 'Говорящий монстр')
            game.associate_current_state()
            self.progress['started_game'] = True

        # Когда игрок на тестовом вступлении
        if (self.progress['started_game']
            and game.current_state_type.name == StateType.DIALOGUE.name
            and game.dialogue_manager.dialogue is self.intro):

            # Когда игрок отвечает на вопрос тестового вступления
            if not self.progress['answered_intro_question']:
                intro_choice = game.dialogue_manager.dialogue.saved_choices.get("Так говоришь, хочешь пройти лабиринт?")
                if intro_choice == 'Да':
                    game.dialogue_manager.advance(jump_to=6)
                    self.intro_said_yes = True
                    self.progress['answered_intro_question'] = True
                elif intro_choice == 'Нет':
                    game.dialogue_manager.advance(jump_to=7)
                    self.intro_said_no = True
                    self.progress['answered_intro_question'] = True

            # Когда диалог показал линию "Ну тогда заходи!" и должен завершиться
            if self.intro_said_yes and game.dialogue_manager.current_line_ind > 6:
                game.dialogue_manager.finished = True

            # Когда игрок завершает тестовое вступление
            if game.dialogue_manager.finished:
                # Если игрок выбрал "Да" - переход к лабиринту
                if self.intro_said_yes:
                    self.progress['finished_intro'] = True
                    game.current_state_type = StateType.MAZE
                    self.maze = game.maze_manager.setup_maze(31, 19, (Border.WEST, Border.EAST), (1, 17), True, True)
                    game.associate_current_state()
                # Если игрок выбрал "Нет" - завершение игры
                elif self.intro_said_no:
                    game.running = False

        # Когда игрок в тестовом лабиринте
        if (self.progress['finished_intro']
            and game.current_state_type.name == StateType.MAZE.name
            and game.maze_manager.maze is self.maze):

            # Когда игрок прошёл тестовый лабиринт - переход к концовке
            if game.maze_manager.check_win():
                self.progress['passed_maze'] = True
                game.current_state_type = StateType.DIALOGUE
                self.outro = game.dialogue_manager.setup_dialogue(outro_dialogue_text.split('\n'), 'Говорящий монстр')
                game.associate_current_state()

        # Когда игрок на тестовой концовке
        if (self.progress['passed_maze']
            and game.current_state_type.name == StateType.DIALOGUE.name
            and game.dialogue_manager.dialogue is self.outro):

            # Когда игрок завершает тестовую концовку
            if game.dialogue_manager.finished:
                self.progress['finished_outro'] = True
                game.running = False
