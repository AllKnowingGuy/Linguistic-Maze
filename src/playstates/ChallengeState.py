from math import ceil
import random

import pygame

from src import AssetsCreation
from src.levelBuilding import Challenge
from src.levelBuilding.Button import Button
from src.Util import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    CHOICE_BUTTON_SIZE,
    CHAL_BUTTON_WIDTH,
    CHAL_BUTTON_HEIGHT,
    Command,
    ButtonState,
    Awaiting,
)
from src.playstates.BaseState import BaseState


# Константы
CHOICE_BUTTON_X = 300
CHOICE_BUTTON_Y = SCREEN_HEIGHT // 2 + 90
CHOICE_BUTTON_DIST_X = CHOICE_BUTTON_SIZE + 250 # расстояние между кнопками выбора по горизонтали
CHOICE_BUTTON_DIST_Y = CHOICE_BUTTON_SIZE + 10 # расстояние между кнопками выбора по вертикали

BACK_BUTTON_X = 100
FORTH_BUTTON_X = SCREEN_WIDTH - 250
NAV_BUTTON_Y = SCREEN_HEIGHT - 140

TITLE_Y = 80
TEXT_X = 160
TEXT_Y = 130
IMAGE_Y = 190

TRANSITION_TIME = 2000
RESULTS_TIME = 4000

CHECK_TIME = 1000


class ChallengeState(BaseState):
    challenge: Challenge.Challenge | None

    playing_start_anim: bool
    submitted: bool
    playing_check_load_anim: bool
    playing_window_check_anim: bool
    verdicted: bool
    finished: bool

    start_anim_time: float
    check_load_anim_time: float
    check_window_anim_time: float
    end_anim_time: float

    current_window_ind: int
    current_title: str | None
    current_task_text: str | None
    current_image: pygame.Surface | None
    current_answer_correctness: bool | None
    current_stamp: pygame.Surface | None
    current_tip: str | None

    awaiting: Awaiting

    playing_text: bool = False
    text_cursor: int
    cursor_sym: str

    def __init__(self):
        """Задание некоторых атрибутов, загрузка изображений для отрисовки и создание шрифтов"""
        super().__init__()

        """Параметры по умолчанию"""
        self.challenge = None

        # На запуске испытания (запуск заставки проводит StoryScript)
        self.playing_start_anim = False
        self.start_anim_time = 0

        # Отправка ответов
        self.submitted = False

        # Перед проверкой ответов
        self.playing_check_load_anim = False
        self.check_load_anim_time = 0

        # Во время проверки
        self.playing_window_check_anim = False
        self.check_window_anim_time = 0

        # Конец проверки
        self.verdicted = False
        self.end_anim_time = 0
        self.finished = False

        # Данные текущего окна
        self.current_window_ind = 0
        self.current_title = None
        self.current_task_text = None
        self.awaiting = Awaiting.CONTINUE
        self.current_answer_correctness = None

        # Данные анимации текста
        self.playing_text = False
        self.text_cursor = 10**10
        self.cursor_sym = ''

        # Наборы кнопок выбора (по окнам)
        self.choice_buttons_sets: dict[int, list[Button]] = {}

        # Тексты полей ввода (по окнам)
        self.input_texts = {}

        # Кнопки перехода
        self.back_button = Button(BACK_BUTTON_X, NAV_BUTTON_Y, CHAL_BUTTON_WIDTH, CHAL_BUTTON_HEIGHT, 'back')
        self.forth_button = Button(FORTH_BUTTON_X, NAV_BUTTON_Y, CHAL_BUTTON_WIDTH, CHAL_BUTTON_HEIGHT, 'forth')
        self.submit_button = Button(FORTH_BUTTON_X, NAV_BUTTON_Y, CHAL_BUTTON_WIDTH, CHAL_BUTTON_HEIGHT, 'submit')
        self.nav_buttons = (self.back_button, self.forth_button, self.submit_button)

        """Графика"""
        # Фон испытания
        self.challenge_bg = AssetsCreation.add_challenge_bg()

        # Карточка с заданием
        self.question_card = AssetsCreation.add_question_card()

        # Изображение для задания
        self.current_image = None

        # Спрайты кнопок
        self.choice_button_sprites = AssetsCreation.add_challenge_choice_buttons()
        self.back_button_sprites = AssetsCreation.add_back_buttons()
        self.forth_button_sprites = AssetsCreation.add_forth_buttons()
        self.submit_button_sprites = AssetsCreation.add_submit_buttons()

        # Штампы "Верно" и "Неверно"
        self.correct_stamp, self.incorrect_stamp = AssetsCreation.add_judgement_stamps()
        self.current_stamp = None

        # Карточка с комментариями к ответу
        self.tip_card = AssetsCreation.add_tip_card()
        self.current_tip = None

        # Заставки
        self.start_cover, self.check_cover, self.end_cover = AssetsCreation.add_transitions()

        # Шрифт испытания
        # TODO: it's probably better to create this in Main where Pygame is initiated
        self.challenge_font = pygame.font.Font(None, 35)

        # Кэш для картинок, когда они появляются
        self.image_cache = {}

    def setup_challenge(self, json_path: str):
        """Задание структурных данных испытания, сброс параметров этапов испытания"""

        self.challenge = Challenge.Challenge(json_path)
        self.playing_start_anim = False
        self.submitted = False
        self.playing_check_load_anim = False
        self.playing_window_check_anim = False
        self.verdicted = False
        self.finished = False
        self.current_window_ind = 0

        # Получение данных первого окна
        self.get_window_fields()

        # Данные анимации текста
        self.text_cursor = 10**10 # чтобы анимация не играла при заставке
        self.cursor_sym = ''

        return self.challenge

    def start_start_anim(self):
        self.playing_start_anim = True
        self.start_anim_time = pygame.time.get_ticks()

    def play_start_anim(self):
        if self.playing_start_anim and pygame.time.get_ticks() >= self.start_anim_time + TRANSITION_TIME:
            self.playing_start_anim = False

            # Можно сразу начинать выводить текст окна
            self.playing_text = True
            self.text_cursor = 0

    def start_check_anim(self):
        self.playing_check_load_anim = True
        self.check_load_anim_time = pygame.time.get_ticks()

    def play_check_anim(self):
        if self.playing_check_load_anim and pygame.time.get_ticks() >= self.check_load_anim_time + TRANSITION_TIME:
            self.playing_check_load_anim = False

            # Отключаем кнопки, которые больше не используются
            self.back_button.state = ButtonState.DISABLED
            self.submit_button.state = ButtonState.DISABLED

            # Находим первое реальное задание и сразу играем его анимацию
            self.current_window_ind = -1
            self.change_card_on_checking()

    def start_window_check_anim(self):
        self.playing_window_check_anim = True
        self.check_window_anim_time = pygame.time.get_ticks()

    def play_window_check_anim(self):
        if self.playing_window_check_anim:
            if (self.current_answer_correctness is None
                    and pygame.time.get_ticks() >= self.check_window_anim_time + CHECK_TIME):
                self.current_answer_correctness = self.check_current_answer()
                self.current_stamp = (self.incorrect_stamp, self.correct_stamp)[self.current_answer_correctness]
            elif pygame.time.get_ticks() >= self.check_window_anim_time + CHECK_TIME * 2:
                self.current_tip = random.choice((self.challenge.get_window_incorrect_tips(self.current_window_ind),
                                                  self.challenge.get_window_correct_tips(self.current_window_ind)
                                                  )[self.current_answer_correctness])
                self.forth_button.state = ButtonState.REGULAR
                self.playing_window_check_anim = False

    def start_end_anim(self):
        self.end_anim_time = pygame.time.get_ticks()

    def play_end_anim(self):
        if not self.finished and pygame.time.get_ticks() >= self.end_anim_time + RESULTS_TIME:
            self.finished = True

    def change_card(self, back: bool = False):
        """Переключение на следующее или предыдущее задание"""

        if back:
            self.current_window_ind -= 1
        else:
            self.current_window_ind += 1
        self.get_window_fields()
        self.playing_text = True
        self.text_cursor = 0

    def change_card_on_checking(self):
        """Переключение на следующее задание при отображении верных ответов"""

        self.forth_button.state = ButtonState.DISABLED
        self.current_window_ind += 1
        while (not self.challenge.get_window_action_type(self.current_window_ind)
               or self.challenge.get_window_action_type(self.current_window_ind) not in ('choosefrom', 'savetyped')):
            self.current_window_ind += 1
            if self.current_window_ind >= len(self.challenge.windows):
                self.current_window_ind -= 1 # на всякий случай остаёмся в пределах окон
                self.get_window_fields() # последнее окно не будет видно, но обновятся параметры для отрисовки
                self.verdicted = True
                self.start_end_anim()
                return
        self.get_window_fields()
        self.current_answer_correctness = None
        self.current_stamp = None
        self.current_tip = None
        self.start_window_check_anim()

    def get_window_fields(self):
        """Получение данных из строчки файла испытания"""

        # Извлекаем заголовок
        self.current_title = self.challenge.get_window_title(self.current_window_ind)

        # Извлекаем текст
        self.current_task_text = self.challenge.get_window_task_text(self.current_window_ind)

        # Извлекаем изображение с кешированием
        image_path = self.challenge.get_window_image_path(self.current_window_ind)
        if image_path:
            if not image_path in self.image_cache:
                self.image_cache[image_path] = AssetsCreation.add_window_image(image_path)
            self.current_image = self.image_cache[image_path]
        else:
            self.current_image = None

        # Извлекаем метаданные
        action_type = self.challenge.get_window_action_type(self.current_window_ind)

        # Преобразуем данные в формат, поддерживаемый ChallengeState
        if action_type:
            if action_type == 'savetyped':
                # Создаём вводимый текст данной страницы (если ещё не был создан)
                if not self.current_window_ind in self.input_texts:
                    self.input_texts[self.current_window_ind] = ''
                self.awaiting = Awaiting.INPUT

            elif action_type == 'choosefrom':
                # Получаем варианты ответа и создаём список кнопок данной страницы (если ещё не был создан)
                if not self.current_window_ind in self.choice_buttons_sets:
                    self.choice_buttons_sets[self.current_window_ind] = []
                    current_choice_options = self.challenge.get_window_choose_options(self.current_window_ind)
                    number_of_options = len(current_choice_options)

                    for opt_ind, opt in enumerate(current_choice_options):
                        if number_of_options < 4:
                            # Один столбик
                            self.choice_buttons_sets[self.current_window_ind].append(
                                Button(
                                CHOICE_BUTTON_X,
                                CHOICE_BUTTON_Y + CHOICE_BUTTON_DIST_Y * opt_ind,
                                CHOICE_BUTTON_SIZE,
                                CHOICE_BUTTON_SIZE,
                                opt)
                            )
                        else:
                            # Два столбика
                            self.choice_buttons_sets[self.current_window_ind].append(
                                Button(
                                CHOICE_BUTTON_X + CHOICE_BUTTON_DIST_X * (opt_ind >= number_of_options / 2),
                                CHOICE_BUTTON_Y + CHOICE_BUTTON_DIST_Y * (opt_ind % ceil(number_of_options / 2)),
                                CHOICE_BUTTON_SIZE,
                                CHOICE_BUTTON_SIZE,
                                opt)
                            )

                self.awaiting = Awaiting.CHOOSE

            else:
                raise ValueError('This action cannot be processed')

        else:
            self.awaiting = Awaiting.CONTINUE

        # Включаем и отключаем кнопки навигации в зависимости от текущего индекса окна
        if not self.submitted:
            if self.current_window_ind == 0 and self.current_window_ind == len(self.challenge.windows) - 1:
                self.back_button.state = ButtonState.DISABLED
                self.forth_button.state = ButtonState.DISABLED
                self.submit_button.state = ButtonState.REGULAR
            elif self.current_window_ind == 0:
                self.back_button.state = ButtonState.DISABLED
                self.forth_button.state = ButtonState.REGULAR
                self.submit_button.state = ButtonState.DISABLED
            elif self.current_window_ind == len(self.challenge.windows) - 1:
                self.back_button.state = ButtonState.REGULAR
                self.forth_button.state = ButtonState.DISABLED
                self.submit_button.state = ButtonState.REGULAR
            else:
                self.back_button.state = ButtonState.REGULAR
                self.forth_button.state = ButtonState.REGULAR
                self.submit_button.state = ButtonState.DISABLED

    def check_current_answer(self):
        """Проверка текущего ответа на правильность методом, назначенным на это задание"""

        if self.current_window_ind in self.input_texts:
            user_input = self.input_texts[self.current_window_ind]
        elif self.current_window_ind in self.choice_buttons_sets:
            for btn in self.choice_buttons_sets[self.current_window_ind]:
                if btn.state == ButtonState.PRESSED:
                    user_input = btn.text
                    break
            else:
                raise Exception(f'No buttons were pressed for this question: {self.current_window_ind}')
        else:
            raise Exception(f'This window has no question: {self.current_window_ind}')
        keys = self.challenge.get_window_correct_answers(self.current_window_ind)
        checker = self.challenge.get_window_answers_checker(self.current_window_ind)
        if checker:
            if checker == 'plainequality':
                return user_input in keys # затычка
            else:
                raise ValueError(f'This checker cannot be recognized: {checker}')
        else:
            return user_input in keys

    """
    Переписанные функции состояния
    """

    def handle_input(self, event):
        """Обработка ввода с клавиатуры, когда ожидается ввод"""

        # Вывод всего сообщения сразу
        if self.playing_text and event.key == pygame.K_ESCAPE:
            self.text_cursor = len(self.current_task_text)

        # Ограничения
        if (self.awaiting.name == Awaiting.INPUT.name
            and not self.submitted
            and not self.playing_text
            and not self.playing_start_anim):

            # Нажатие кнопок (когда есть поле ввода)
            if event.key == pygame.K_BACKSPACE:
                self.input_texts[self.current_window_ind] = self.input_texts[self.current_window_ind][:-1]
            elif event.key not in (pygame.K_ESCAPE, pygame.K_TAB, pygame.K_DELETE, pygame.K_RETURN):
                self.input_texts[self.current_window_ind] += event.unicode

    def handle_mouse_motion(self, event):
        """Обработка наведения курсора на кнопки"""

        if not self.playing_start_anim and not self.playing_check_load_anim and not self.verdicted:
            btn_set = []
            btn_set.extend(self.nav_buttons)
            if self.awaiting.name == Awaiting.CHOOSE.name:
                btn_set.extend(self.choice_buttons_sets[self.current_window_ind])

            for btn in btn_set:
                if ((btn in self.nav_buttons or not self.playing_text and not self.submitted)
                        and not btn.state in (ButtonState.DISABLED, ButtonState.PRESSED)):
                    if btn.is_hovered(event.pos):
                        # Когда курсор поверх кнопки - подсвечиваем
                        btn.state = ButtonState.HOVERED
                    else:
                        # Когда убираем курсор - убираем подсветку
                        btn.state = ButtonState.REGULAR

    def handle_mouse_click(self, event):
        """Обработка нажатия на кнопки"""

        if (event.button == pygame.BUTTON_LEFT
                and not self.playing_start_anim
                and not self.playing_check_load_anim
                and not self.verdicted):
            btn_set = []
            btn_set.extend(self.nav_buttons)
            if self.awaiting.name == Awaiting.CHOOSE.name:
                btn_set.extend(self.choice_buttons_sets[self.current_window_ind])

            for btn in btn_set:
                if btn.state == ButtonState.HOVERED:
                    btn.state = ButtonState.PRESSED
                    if btn not in self.nav_buttons:
                        # Отжатие остальных кнопок выбора
                        for btn2 in self.choice_buttons_sets[self.current_window_ind]:
                            # TODO: optimize or make a separate function
                            btn2.state = ButtonState.REGULAR if not btn2 is btn else ButtonState.PRESSED
                    return

    def handle_mouse_release(self, event):
        """Обработка отпуска ЛКМ после щелчка по кнопке навигации"""

        if (event.button == pygame.BUTTON_LEFT
                and not self.playing_start_anim
                and not self.playing_check_load_anim
                and not self.verdicted):
            for btn in self.nav_buttons:
                if btn.is_hovered(event.pos) and btn.state == ButtonState.PRESSED:
                    # Когда курсор поверх нажатой кнопки - отпуск активирует действие
                    if btn is self.back_button:
                        self.change_card(back=True)
                        return None
                    elif btn is self.forth_button:
                        if not self.submitted:
                            self.change_card(back=False)
                        else:
                            self.change_card_on_checking()
                        return (Command.CHECK_PROGRESS, None),
                    elif btn is self.submit_button:
                        # TODO: check if fields are filled and choice buttons are pressed
                        self.submitted = True
                        self.start_check_anim()
                        return (Command.CHECK_PROGRESS, None),
                    else:
                        raise ValueError(f'This button is foreign: {btn.text}')
            else:
                # Когда отпустили курсор не над нажатой кнопкой - все кнопки становятся неподсвеченными
                for btn in self.nav_buttons:
                    if not btn.state == ButtonState.DISABLED:
                        btn.state = ButtonState.REGULAR
        return None

    def draw(self, screen):
        """Отрисовка испытания"""

        # Создаём фон
        screen.blit(self.challenge_bg, (0, 0))

        # Отрисовываем карточку испытания
        screen.blit(self.question_card, (SCREEN_WIDTH / 2 - self.question_card.get_width() / 2, 50))

        # Отрисовываем заголовок
        title_sprite = self.challenge_font.render(self.current_title, True, (0, 0, 0))
        screen.blit(title_sprite, (SCREEN_WIDTH / 2 - title_sprite.get_width() / 2, TITLE_Y))

        # Отрисовываем изображение из задания (если оно есть)
        if self.current_image:
            screen.blit(self.current_image, (SCREEN_WIDTH / 2 - self.current_image.get_width() / 2, IMAGE_Y))

        # Отрисовываем кнопки навигации
        btn_sprites_set = (self.back_button_sprites, self.forth_button_sprites, self.submit_button_sprites)
        if not self.submitted or not self.playing_window_check_anim:
            for btn_ind, btn in enumerate(self.nav_buttons):
                if btn.state != ButtonState.DISABLED:
                    screen.blit(btn_sprites_set[btn_ind][btn.state], (btn.x, btn.y))

        # Отрисовываем текст (по буковке, если отвечаем, и сразу, если проверяем)
        self.draw_text_by_letter(screen)

        # Отрисовываем, когда текст испытания прекращает печататься (или сразу, если проверяем)
        if not self.playing_text or self.submitted:

            # Отрисовываем кнопки выбора (если они есть)
            if self.awaiting.name == Awaiting.CHOOSE.name:
                for btn in self.choice_buttons_sets[self.current_window_ind]:

                    # Сами кнопки
                    screen.blit(self.choice_button_sprites[btn.state], (btn.x, btn.y))

                    # Текст кнопок
                    input_text_sprite = self.challenge_font.render(btn.text, True, (0, 0, 0))
                    screen.blit(input_text_sprite, (btn.x + btn.width + 10, btn.y))

            # Отрисовываем вводимый текст (если можно вводить)
            elif self.awaiting.name == Awaiting.INPUT.name:
                # TODO: make BG for input field
                input_text_sprite = self.challenge_font.render(
                    ' - Ввод: ' + self.input_texts[self.current_window_ind],
                    True,
                    (0, 0, 0))
                screen.blit(input_text_sprite, (TEXT_X, SCREEN_HEIGHT // 2 + 110))

        # Отрисовываем штамп правильности (когда он ставится по анимации)
        if self.current_stamp:
            screen.blit(self.current_stamp, (SCREEN_WIDTH / 2 - self.current_stamp.get_width() / 2, NAV_BUTTON_Y))

        # Отрисовываем плашку совета и кнопку продолжения (когда они появляются по анимации)
        if self.current_tip:
            screen.blit(self.tip_card, (SCREEN_WIDTH / 2 - self.tip_card.get_width() / 2, TEXT_Y))
            tip_text = self.challenge_font.render(self.current_tip, True, (0, 0, 0))
            screen.blit(tip_text, (SCREEN_WIDTH / 2 - self.tip_card.get_width() / 2 + 40, TEXT_Y + 40))

        if self.play_window_check_anim():
            self.play_window_check_anim()

        # Отрисовываем заставку (поверх всего-всего)
        if self.playing_start_anim:
            screen.blit(self.start_cover, (0, 0))
            self.play_start_anim()
        elif self.playing_check_load_anim:
            screen.blit(self.check_cover, (0, 0))
            self.play_check_anim()
        elif self.verdicted:
            screen.blit(self.end_cover, (0, 0))
            self.play_end_anim()

        return (Command.CHECK_PROGRESS, None),

    """
    Вспомогательные функции для отрисовки
    """

    def draw_text_by_letter(self, screen):
        """Приятный глазу эффект выведения текста по буковке"""
        # TODO: MOVE TO A SEPARATE CLASS ALONG WITH ALL PLAYABLE TEXT ATTRIBUTES

        if self.text_cursor >= len(self.current_task_text):
            self.playing_text = False
        else:
            self.text_cursor += 1

        text_sprite = self.challenge_font.render(self.current_task_text[:self.text_cursor], True, (0, 0, 0))
        screen.blit(text_sprite, (TEXT_X, TEXT_Y))
