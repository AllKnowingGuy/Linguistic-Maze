from math import ceil
import pygame, random

from src import AssetsCreation
from src.Config import Config
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
    get_centered_point,
)
from src.playstates.BaseState import BaseState

# Константы
CHOICE_BUTTON_X = 180
CHOICE_BUTTON_Y = SCREEN_HEIGHT // 2 + 70
CHOICE_BUTTON_DIST_X = CHOICE_BUTTON_SIZE + 350  # расстояние между кнопками выбора по горизонтали
CHOICE_BUTTON_DIST_Y = CHOICE_BUTTON_SIZE + 10  # расстояние между кнопками выбора по вертикали

BACK_BUTTON_X = 100
FORTH_BUTTON_X = SCREEN_WIDTH - 250
NAV_BUTTON_Y = SCREEN_HEIGHT - 140

TITLE_Y = 100
TEXT_X = 150
TEXT_Y = TITLE_Y + 40
TEXT_DIST_Y = 40
IMAGE_Y = TITLE_Y + 100

TRANSITION_TIME = 2000
RESULTS_TIME = 4000

CHECK_TIME = 1000


class ChallengeState(BaseState):
    challenge: Challenge.Challenge | None

    choice_buttons_sets: dict[int, list[Button]]
    input_texts: dict[int, str]

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
    current_task_text: list[str]
    current_image: pygame.Surface | None
    current_answer_correctness: bool | None
    current_stamp: pygame.Surface | None
    current_tip: str | None

    awaiting: Awaiting

    playing_text: bool = False
    text_line: int
    text_cursor: int

    def __init__(self):
        """Задание некоторых атрибутов, загрузка изображений для отрисовки и создание шрифтов"""
        super().__init__()

        """Параметры по умолчанию"""
        self.challenge = None
        self.score = 0

        # На запуске испытания (запуск заставки проводит StoryScript)
        self.playing_start_anim = False
        self.start_anim_time = 0
        self.start_anim_perc = 0.0

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
        self.current_task_text = []
        self.awaiting = Awaiting.CONTINUE
        self.current_answer_correctness = None
        self.current_reward = 0

        # Данные анимации текста
        self.playing_text = False
        self.text_cursor = 10 ** 10
        self.text_line = 0

        # Наборы кнопок выбора (по окнам)
        self.choice_buttons_sets = {}

        # Тексты полей ввода (по окнам)
        self.input_texts = {}

        # Кнопки перехода
        self.back_button = Button(BACK_BUTTON_X, NAV_BUTTON_Y, CHAL_BUTTON_WIDTH, CHAL_BUTTON_HEIGHT, 'back')
        self.forth_button = Button(FORTH_BUTTON_X, NAV_BUTTON_Y, CHAL_BUTTON_WIDTH, CHAL_BUTTON_HEIGHT, 'forth')
        self.submit_button = Button(FORTH_BUTTON_X, NAV_BUTTON_Y, CHAL_BUTTON_WIDTH, CHAL_BUTTON_HEIGHT, 'submit')
        self.nav_buttons = (self.back_button, self.forth_button, self.submit_button)

        """Управление"""
        self.stop_anim_bind = Config().get_challenge_controls()

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

        # Шрифт испытания и выводимые тексты
        self.challenge_font = pygame.font.Font(None, 35)

        # Кэш для картинок, когда они появляются
        self.image_cache = {}

        # Кеш редко меняющегося содержимого дисплея
        self.need_cache = False
        self.bg_card_task_img_cache = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

        """Звуки"""
        self.start_challenge_sound = AssetsCreation.add_challenge_start_sound()

    def setup_challenge(self, json_path: str):
        """Задание структурных данных испытания, сброс параметров этапов испытания"""

        self.challenge = Challenge.Challenge(json_path)
        self.score = 0

        # Сброс параметров и очистка словарей ответов
        self.choice_buttons_sets = {}
        self.input_texts = {}
        self.playing_start_anim = False
        self.start_anim_perc = 0.0
        self.submitted = False
        self.playing_check_load_anim = False
        self.playing_window_check_anim = False
        self.verdicted = False
        self.finished = False

        self.current_window_ind = 0
        self.current_answer_correctness = None
        self.current_reward = 0
        self.current_stamp = None
        self.current_tip = None

        # Получение данных первого окна
        self.get_window_fields()

        # Данные анимации текста
        self.playing_text = False

        # Запрос на обновление экрана
        self.need_screen_update = True

        # Обновление клавиши прекращения анимации (чтобы подтянулись изменения в меню)
        self.stop_anim_bind = Config().get_challenge_controls()

        return self.challenge

    def start_start_anim(self):
        self.playing_start_anim = True

        # Играем переход и обновляем музыку
        AssetsCreation.set_challenge_music()
        self.start_challenge_sound.play()

        self.start_anim_time = pygame.time.get_ticks()
        self.need_screen_update = True

    def play_start_anim(self):
        if self.playing_start_anim:
            current_ticks = pygame.time.get_ticks()
            if current_ticks >= self.start_anim_time + TRANSITION_TIME:
                self.playing_start_anim = False

                # Ставим музыку испытания
                pygame.mixer.music.play(-1)

                # Можно сразу начинать выводить текст окна
                self.text_line = 0
                self.playing_text = True
                self.text_cursor = 0

                self.need_screen_update = True

            else:
                self.start_anim_perc = float((current_ticks - self.start_anim_time)
                                             //
                                             (TRANSITION_TIME // 16) * 6.25)

    def start_check_anim(self):
        pygame.mixer.music.stop()
        self.playing_check_load_anim = True
        self.check_load_anim_time = pygame.time.get_ticks()
        self.need_screen_update = True

    def play_check_anim(self):
        if self.playing_check_load_anim and pygame.time.get_ticks() >= self.check_load_anim_time + TRANSITION_TIME:
            self.playing_check_load_anim = False

            # Отключаем кнопки, которые больше не используются
            self.back_button.state = ButtonState.DISABLED
            self.submit_button.state = ButtonState.DISABLED

            # Находим первое реальное задание и сразу играем его анимацию
            self.current_window_ind = -1
            self.change_card_on_checking()

            self.need_screen_update = True

    def start_window_check_anim(self):
        self.playing_window_check_anim = True
        self.check_window_anim_time = pygame.time.get_ticks()
        self.need_screen_update = True

    def play_window_check_anim(self):
        if self.playing_window_check_anim:

            # Анимация штампа правильности
            # TODO: maybe check the answer earlier such as in start_window_check_anim
            current_ticks = pygame.time.get_ticks()
            if (self.current_answer_correctness is None
                    and current_ticks >= self.check_window_anim_time + CHECK_TIME):
                self.current_answer_correctness = self.challenge.check_current_answer(self.current_window_ind)

                self.current_reward = (self.challenge.get_window_incorrect_respect_points(self.current_window_ind),
                                       self.challenge.get_window_correct_respect_points(self.current_window_ind)
                                       )[self.current_answer_correctness]
                self.score += self.current_reward

                self.current_stamp = (self.incorrect_stamp, self.correct_stamp)[self.current_answer_correctness]
                self.need_screen_update = True

            # Анимация плашки с комментарием
            elif current_ticks >= self.check_window_anim_time + CHECK_TIME * 2:

                self.current_tip = random.choice((self.challenge.get_window_incorrect_tips(self.current_window_ind),
                                                  self.challenge.get_window_correct_tips(self.current_window_ind)
                                                  )[self.current_answer_correctness])

                self.forth_button.state = ButtonState.REGULAR
                self.playing_window_check_anim = False
                self.need_screen_update = True

    def start_end_anim(self):
        self.end_anim_time = pygame.time.get_ticks()
        self.need_screen_update = True

    def play_end_anim(self):
        if not self.finished and pygame.time.get_ticks() >= self.end_anim_time + RESULTS_TIME:
            self.finished = True
            self.need_screen_update = True

    def change_card(self, back: bool = False):
        """Переключение на следующее или предыдущее задание"""

        if back:
            self.current_window_ind -= 1
        else:
            self.current_window_ind += 1
        self.get_window_fields()
        self.playing_text = True
        self.text_cursor = 0

        self.need_screen_update = True

    def change_card_on_checking(self):
        """Переключение на следующее задание при отображении верных ответов"""

        self.forth_button.state = ButtonState.DISABLED
        self.current_window_ind += 1
        while (not self.challenge.get_window_action_type(self.current_window_ind)
               or self.challenge.get_window_action_type(self.current_window_ind) not in ('choosefrom', 'savetyped')):
            self.current_window_ind += 1
            if self.current_window_ind >= len(self.challenge.windows):
                self.current_window_ind -= 1  # на всякий случай остаёмся в пределах окон
                self.get_window_fields()  # последнее окно не будет видно, но обновятся параметры для отрисовки
                self.verdicted = True
                self.start_end_anim()
                return
        self.get_window_fields()
        self.current_answer_correctness = None
        self.current_stamp = None
        self.current_tip = None
        self.start_window_check_anim()

        self.need_screen_update = True

    def get_window_fields(self):
        """Получение данных из строчки файла испытания"""

        # Если испытание завершено - не пытаемся извлечь данные
        if self.finished or self.verdicted:
            return

        # Когда перебрали все окна при проверке, завершаем испытание
        elif self.current_window_ind >= len(self.challenge.windows):
            self.current_window_ind = len(self.challenge.windows) - 1
            self.verdicted = True
            return

        # Извлекаем заголовок
        self.current_title = self.challenge.get_window_title(self.current_window_ind)

        # Извлекаем текст
        self.current_task_text = self.challenge.get_window_task_text(self.current_window_ind)
        self.text_line = 0

        # Извлекаем и создаём изображение (с кешированием)
        image_path = self.challenge.get_window_image_path(self.current_window_ind)
        if image_path:
            if not image_path in self.image_cache:
                self.image_cache[image_path] = AssetsCreation.add_window_image(image_path)
            self.current_image = self.image_cache[image_path]
        else:
            self.current_image = None

        # Извлекаем метаданные
        action_type = self.challenge.get_window_action_type(self.current_window_ind)
        if action_type:
            if action_type == 'savetyped':
                # Создаём вводимый текст данной страницы (если ещё не был создан)
                self.awaiting = Awaiting.INPUT
                if not self.current_window_ind in self.input_texts:
                    self.input_texts[self.current_window_ind] = ''
            elif action_type == 'choosefrom':
                # Получаем варианты ответа и создаём список кнопок данной страницы (если ещё не был создан)
                self.awaiting = Awaiting.CHOOSE
                self.set_choosefrom_window()
            else:
                raise ValueError(f'This action cannot be processed: {action_type}')
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

        # Запрашиваем обновление редко меняющихся элементов экрана
        self.need_cache = True

    def set_choosefrom_window(self):
        if not self.current_window_ind in self.choice_buttons_sets:
            self.choice_buttons_sets[self.current_window_ind] = []
            current_choice_options = self.challenge.get_window_choose_options(self.current_window_ind)
            number_of_options = len(current_choice_options)

            for opt_ind, opt in enumerate(current_choice_options):
                if number_of_options < 5:
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

    """
    Переписанные функции состояния
    """

    def handle_input(self, event):
        """Обработка ввода с клавиатуры, когда ожидается ввод, и прекращения анимации печатания текста"""

        # Вывод всего сообщения сразу
        if self.playing_text and event.unicode == chr(self.stop_anim_bind):
            self.text_line = len(self.current_task_text) - 1
            self.text_cursor = len(self.current_task_text[self.text_line])

        # Ограничения
        elif (self.awaiting.name == Awaiting.INPUT.name
              and not self.submitted
              and not self.playing_text
              and not self.playing_start_anim):

            # Нажатие кнопок (когда есть поле ввода)
            self.input_texts[self.current_window_ind], updated = self.update_input_field(
                self.input_texts[self.current_window_ind], event
            )
            if updated:
                self.need_screen_update = True

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
                    self.update_button_on_hovering(btn, event)

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
                to_reset = None
                if btn not in self.nav_buttons:
                    to_reset = self.choice_buttons_sets[self.current_window_ind]
                if self.update_buttons_on_press(btn, to_reset):
                    return

    def handle_mouse_release(self, event):
        """Обработка отпуска ЛКМ после щелчка по кнопке навигации"""

        if (event.button == pygame.BUTTON_LEFT
                and not self.playing_start_anim
                and not self.playing_check_load_anim
                and not self.verdicted
                and ButtonState.PRESSED in [btn.state for btn in self.nav_buttons]):

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
                        supposed_command = self.check_save_and_submit()
                        if supposed_command:
                            return supposed_command

                    else:
                        raise ValueError(f'This button is foreign: {btn.text}')

            else:
                # Когда отпустили курсор не над нажатой кнопкой - все кнопки становятся неподсвеченными
                for btn in self.nav_buttons:
                    if not btn.state == ButtonState.DISABLED:
                        btn.state = ButtonState.REGULAR
            self.need_screen_update = True
        return None

    def execute_before_draw(self):
        """Проверка истечения таймеров анимации"""

        if self.playing_start_anim:
            self.play_start_anim()
        elif self.playing_check_load_anim:
            self.play_check_anim()
        elif self.verdicted:
            self.play_end_anim()

        if self.playing_window_check_anim:
            self.play_window_check_anim()

    def draw(self, screen):
        """Отрисовка испытания"""

        # ТОЛЬКО ЕСЛИ ЧТО-ТО ИЗМЕНИЛОСЬ НА ЭКРАНЕ
        if self.need_screen_update:

            # Заново вносим кешируемые элементы, когда мы меняем окно
            if self.need_cache:

                # Создаём фон
                self.bg_card_task_img_cache.blit(self.challenge_bg, (0, 0))

                # Отрисовываем карточку испытания
                self.bg_card_task_img_cache.blit(
                    self.question_card,
                    (get_centered_point(self.question_card.get_width(), False), TITLE_Y - 50)
                )

                # Отрисовываем заголовок
                title_sprite = self.challenge_font.render(self.current_title, True, (0, 0, 0))
                self.bg_card_task_img_cache.blit(
                    title_sprite, (get_centered_point(title_sprite.get_width(), False), TITLE_Y)
                )

                # Отрисовываем изображение из задания (если оно есть)
                if self.current_image:
                    self.bg_card_task_img_cache.blit(
                        self.current_image, (get_centered_point(self.current_image.get_width(), False), IMAGE_Y)
                    )

                self.need_cache = False

            # Достаём кешированные элементы, пока мы на одном и том же окне
            screen.blit(self.bg_card_task_img_cache, (0, 0))

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
                    screen.blit(input_text_sprite, (TEXT_X + 200, SCREEN_HEIGHT // 2 + 180))

            # Отрисовываем штамп правильности (когда он ставится по анимации)
            if self.current_stamp:
                screen.blit(self.current_stamp,
                            (get_centered_point(self.current_stamp.get_width(), False), NAV_BUTTON_Y)
                            )

            # Отрисовываем плашку совета и кнопку продолжения (когда они появляются по анимации)
            if self.current_tip:
                screen.blit(self.tip_card, (get_centered_point(self.tip_card.get_width(), False),
                                            get_centered_point(self.tip_card.get_height(), True)))

                if self.current_reward > 0:
                    reward_announce = f'Твой респект увеличился на {self.current_reward}!'
                elif self.current_reward < 0:
                    reward_announce = f'Твой респект уменьшился на {-self.current_reward}!'
                else:
                    reward_announce = 'Твой респект не изменился!'

                tip_text = self.challenge_font.render(self.current_tip, True, (0, 0, 0))
                screen.blit(tip_text, (get_centered_point(self.tip_card.get_width(), False) + 40,
                                       get_centered_point(self.tip_card.get_height(), True) + 40))
                reward_announce_text = self.challenge_font.render(reward_announce, True, (0, 0, 0))
                screen.blit(reward_announce_text, (get_centered_point(self.tip_card.get_width(), False) + 40,
                                                   get_centered_point(self.tip_card.get_height(), True) + 80))

            # Отрисовываем заставку (поверх всего-всего)
            if self.playing_start_anim:
                screen.blit(self.start_cover, (0, 0))
                percent_text = self.challenge_font.render(f'{"{:.2f}".format(self.start_anim_perc)} %',
                                                          True,
                                                          (255, 255, 255))
                screen.blit(percent_text, (SCREEN_WIDTH - 200 - percent_text.get_width(), SCREEN_HEIGHT - 100))
            elif self.playing_check_load_anim:
                screen.blit(self.check_cover, (0, 0))
            elif self.verdicted:
                screen.blit(self.end_cover, (0, 0))
                score_text = self.challenge_font.render(f'Респект, который ты заработал: {self.score}',
                                                        True,
                                                        (255, 255, 255))
                screen.blit(score_text, (get_centered_point(score_text.get_width(), False), SCREEN_HEIGHT / 2 + 100))

            # БЛОКИРУЕМ ПОВТОРНУЮ ОТРИСОВКУ ДО ОБНОВЛЕНИЯ ЭЛЕМЕНТОВ
            if not self.playing_text and not self.playing_start_anim:
                self.need_screen_update = False

            # Сообщаем об изменениях главному циклу
            return (Command.CHECK_PROGRESS, None), (Command.UPDATE_DISPLAY, None),

        return None

    """
    Вспомогательные функции для обработки нажатия кнопок
    """

    def check_save_and_submit(self):
        answers = self.input_texts.copy()
        all_filled = all(field.strip() for field in self.input_texts.values())
        for btns_ind, btns in self.choice_buttons_sets.items():
            for btn2 in btns:
                if btn2.state == ButtonState.PRESSED:
                    answers[btns_ind] = btn2.text
                    break
            else:
                all_filled = False
        if all_filled:
            self.challenge.answers = answers
            self.submitted = True
            self.start_check_anim()
            return (Command.CHECK_PROGRESS, None),
        # TODO: add 'else' and make the game warn the player
        return None

    """
    Вспомогательные функции для отрисовки
    """

    def draw_text_by_letter(self, screen):
        """Приятный глазу эффект выведения текста по буковке"""

        # Двигаем курсор
        if self.submitted:
            self.text_line = len(self.current_task_text) - 1
            self.text_cursor = len(self.current_task_text[self.text_line])
            self.playing_text = False

        elif self.text_cursor >= len(self.current_task_text[self.text_line]):
            self.text_line += 1
            if self.text_line >= len(self.current_task_text):
                self.text_line -= 1
                self.playing_text = False
            else:
                self.text_cursor = 0

        else:
            self.text_cursor += 0.4

        # Выводим "напечатанные" строчки сразу
        for i in range(self.text_line):
            text_sprite = self.challenge_font.render(
                self.current_task_text[i], True, (0, 0, 0)
            )
            screen.blit(text_sprite, (TEXT_X, TEXT_Y + TEXT_DIST_Y * i))

        # "Печатаем" последнюю строчку по букве
        text_sprite = self.challenge_font.render(
            self.current_task_text[self.text_line][:int(self.text_cursor)], True, (0, 0, 0)
        )
        screen.blit(text_sprite, (TEXT_X, TEXT_Y + TEXT_DIST_Y * self.text_line))
