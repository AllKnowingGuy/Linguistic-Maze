# Архитектура проекта

## Структура
**main.py** – бесконечный цикл. Вызывает методы `handle_input`, `update`, `draw` текущего состояния, обрабатывает команды, возвращённые этими методами.

`src`

**basestate.py** – определяет интерфейс для всех состояний. Каждое состояние (лабиринт, диалог, задание) наследуется от него и реализует свою логику.

**storyscript.py** – отвечает за переходы между состояниями и внутри состояний. При выборе игрока (например, в диалоге) передаётся команда, которая меняет текущее состояние.

**assetscreation.py** – единое место загрузки спрайтов и звуков, а также видоизменения спрайтов. Для добавления нового ресурса нужно написать функцию загрузки (по образцу add_dialogue_bg) и вызвать её в нужном состоянии.

**config.py** – загружает и сохраняет настройки из config.json. Преобразует строковые представления Unicode для заданных клавиш в символы и обратно. Предоставляет методы для получения привязок клавиш для каждого режима (лабиринт, диалог, задание). Позволяет изменять настройки и записывать их обратно.

**util.py** – хранит общие константы (размеры экрана, клеток, кнопок), перечисления (StateType, Command, WallPattern, Border, ButtonState, Awaiting), вспомогательные функции для центрирования объектов и получения пути к файлу-ресурсу в собранной игре.

`level_building`

**button.py** – класс кнопки, хранит координаты, размеры, текст и состояние (ButtonState). Метод is_hovered проверяет, находится ли курсор над кнопкой. Используется в состояниях диалога, заданий и меню для создания интерактивных элементов.

**challenge.py** – загружает JSON с описанием заданий (окна с вопросами, изображениями, действиями). Предоставляет геттеры для всех полей. Позволяет пропускать задание при наличии артефакта через can_skip_with_artifact.

**checker.py** - содержит метод проверки ответов, а также локально хранимые модели для проверки. Реализует чекеры plainequality, rematch, sentiment_rubert (с использованием Hugging Face pipeline) и existing_words. Список чекеров может быть легко расширен.

**dialogue.py** – загружает JSON диалога. Содержит список реплик, метаданные (имена персонажей, спрайт собеседника, наличие музыки, флаги). Методы извлекают данные для конкретной реплики: текст, тип действия (выбор вариантов или сохранение ввода), варианты, переходы, смену фона. Сохраняет введённые пользователем ответы и сделанные выборы.

**enemy.py** – иерархия врагов. Базовый класс Enemy хранит координаты, имя, активность. Методы: check_collision (проверка столкновения с игроком), deactivate (исчезновение после диалога). Наследники - StationaryEnemy (неподвижный враг) и PatrollingEnemy (ходячий враг).

**maze.py** – генерация лабиринта модифицированным DFS-алгоритмом. Класс Tile – вспомогательный для хранения координат. Основной класс Maze хранит размеры, позиции входа/выхода и внутреннюю карту pattern. Метод generate_maze создаёт проходы, учитывая параметры more_random и curving. Метод place_monsters размещает врагов в лабиринте.

`playstates`

**basestate.py** – модуль с базовым классом для всех состояний. Определяет интерфейс обработки ввода (клавиатура, мышь), обновления, отрисовки. Содержит вспомогательные методы для работы с текстовыми полями и кнопками, а также общий шрифт состояний и атрибут для хранения объекта-чекера. Флаг `need_screen_update` управляет перерисовкой.

**challengestate.py** – состояние прохождения заданий. Отображает карточки с вопросами, вариантами ответов или полем ввода, анимирует и озвучивает переходы, начисляет респекты, использует объект-чекер для проверки ответов.

**dialoguestate.py** – состояние диалога. Управляет репликами, анимацией печатания, выбором вариантов, сохранением ввода, сменой фона/музыки, проигрыванием звуков, начислением респектов, выдачей артефактов и переходом к следующей комнате или заданию. Использует объект-чекер для проверки некоторых введённых ответов, влияющих на переходы.

**mazestate.py** – состояние лабиринта. Генерирует и отображает лабиринт, обрабатывает движение игрока с коллизиями, анимацию ходьбы, статичных и движущихся врагов, эффект темноты и камеру. При столкновении с врагом или дверью меняет флаги, которые считываются StoryScript для смены состояний.

**menustate.py** – главное меню. Позволяет запустить игру и переназначить управление через режим установки клавиши. Отображает текущие привязки, сохраняет их в конфигурации.


## Диаграммы

Диаграмма классов в папке `src`:
![Диаграмма классов в папке src](/assets/images/diagram.png)

Текстовая диаграмма для директории файлов:
```bash
├── assets
│   ├── data
│   │   ├── challenges
│   │   │   ├── level_0
│   │   │   │   └── monster_esperanto.json
│   │   │   ├── level_1
│   │   │   │   ├── monster_agressive.json
│   │   │   │   ├── monster_expert.json
│   │   │   │   ├── monster_formant.json
│   │   │   │   └── monster_phontermin.json
│   │   │   ├── level_2
│   │   │   │   ├── monster_gloss.json
│   │   │   │   ├── monster_linguist.json
│   │   │   │   └── monster_terminology.json
│   │   │   ├── level_3
│   │   │   │   └── monster_questioner.json
│   │   │   └── level_4
│   │   │       └── monster_childspeech.json
│   │   ├── dialogues
│   │   │   ├── level_0
│   │   │   │   ├── monster_esperanto.json
│   │   │   │   ├── monster_esperanto_end.json
│   │   │   │   ├── monster_motivator.json
│   │   │   │   └── monster_runner.json
│   │   │   ├── level_1
│   │   │   │   ├── monster_agressive.json
│   │   │   │   ├── monster_agressive_end.json
│   │   │   │   ├── monster_amateur.json
│   │   │   │   ├── monster_expert.json
│   │   │   │   ├── monster_expert_end.json
│   │   │   │   ├── monster_formant.json
│   │   │   │   ├── monster_formant_end.json
│   │   │   │   ├── monster_phonmotivator.json
│   │   │   │   ├── monster_phontermin.json
│   │   │   │   ├── monster_phontermin_end.json
│   │   │   │   └── monster_runner.json
│   │   │   ├── level_2
│   │   │   │   ├── monster_gloss.json
│   │   │   │   ├── monster_linguist.json
│   │   │   │   ├── monster_linguist_end.json
│   │   │   │   ├── monster_motivator.json
│   │   │   │   ├── monster_researcher.json
│   │   │   │   ├── monster_runner.json
│   │   │   │   ├── monster_sphinx.json
│   │   │   │   ├── monster_terminology.json
│   │   │   │   └── monster_terminology_end.json
│   │   │   ├── level_3
│   │   │   │   ├── monster_communicator.json
│   │   │   │   ├── monster_helper.json
│   │   │   │   ├── monster_questioner.json
│   │   │   │   ├── monster_questioner_end.json
│   │   │   │   ├── monster_runner.json
│   │   │   │   ├── monster_sphinx.json
│   │   │   │   └── monster_tfidf.json
│   │   │   ├── level_4
│   │   │   │   ├── monster_childspeech.json
│   │   │   │   ├── monster_childspeech_end.json
│   │   │   │   ├── monster_motivator.json
│   │   │   │   ├── monster_neuroanatomy.json
│   │   │   │   ├── monster_runner.json
│   │   │   │   ├── monster_schizophrenia_1.json
│   │   │   │   ├── monster_schizophrenia_2.json
│   │   │   │   ├── monster_schizophrenia_3.json
│   │   │   │   ├── monster_schizophrenia_4.json
│   │   │   │   └── monster_silent.json
│   │   │   ├── boss.json
│   │   │   ├── intro.json
│   │   │   └── outro.json
│   │   └── rooms
│   │       ├── room_0.json
│   │       ├── room_1.json
│   │       ├── room_2.json
│   │       ├── room_3.json
│   │       └── room_4.json
│   ├── fonts
│   │   ├── BauhausSaUni.ttf
│   │   ├── BleekerCyrillic.ttf
│   │   └── Full Lettersano.ttf
│   ├── images
│   │   ├── challenge
│   │   │   ├── back_button
│   │   │   │   ├── back_button.png
│   │   │   │   ├── back_button_hovered.png
│   │   │   │   └── back_button_pressed.png
│   │   │   ├── choice_button
│   │   │   │   ├── choice_button.png
│   │   │   │   ├── choice_button_hovered.png
│   │   │   │   └── choice_button_pressed.png
│   │   │   ├── forth_button
│   │   │   │   ├── forth_button.png
│   │   │   │   ├── forth_button_hovered.png
│   │   │   │   └── forth_button_pressed.png
│   │   │   ├── levels
│   │   │   │   ├── level_0
│   │   │   │   │   └── student.png
│   │   │   │   ├── level_1
│   │   │   │   │   ├── first_contour.png
│   │   │   │   │   ├── second_contour.png
│   │   │   │   │   └── third_contour.png
│   │   │   │   └── level_4
│   │   │   │       └── korablik.png
│   │   │   ├── submit_button
│   │   │   │   ├── submit_button.png
│   │   │   │   ├── submit_button_hovered.png
│   │   │   │   └── submit_button_pressed.png
│   │   │   ├── transitions
│   │   │   │   ├── check.png
│   │   │   │   ├── end.png
│   │   │   │   └── start.png
│   │   │   ├── bg.png
│   │   │   ├── card.png
│   │   │   ├── correct.png
│   │   │   ├── incorrect.png
│   │   │   └── tip_card.png
│   │   ├── dialogue
│   │   │   ├── backgrounds
│   │   │   │   ├── back_home.png
│   │   │   │   ├── bg.png
│   │   │   │   ├── bus_time.png
│   │   │   │   ├── challengebg.png
│   │   │   │   ├── doorbg.png
│   │   │   │   ├── dooropenbg.png
│   │   │   │   ├── pass_practicum_plz.png
│   │   │   │   ├── pitchblack.png
│   │   │   │   ├── sphinx.png
│   │   │   │   ├── there_was_anya.png
│   │   │   │   ├── there_was_danya.png
│   │   │   │   ├── there_was_denis.png
│   │   │   │   ├── there_was_lera.png
│   │   │   │   ├── there_were_students.png
│   │   │   │   └── where_are_we.png
│   │   │   ├── choice_button
│   │   │   │   ├── choice_button.png
│   │   │   │   ├── choice_button_hovered.png
│   │   │   │   └── choice_button_pressed.png
│   │   │   ├── monsters
│   │   │   │   ├── level_0
│   │   │   │   │   ├── monster_esperanto.png
│   │   │   │   │   ├── monster_motivator.png
│   │   │   │   │   └── monster_runner.png
│   │   │   │   ├── level_1
│   │   │   │   │   ├── monster_agressive.png
│   │   │   │   │   ├── monster_amateur.png
│   │   │   │   │   ├── monster_expert.png
│   │   │   │   │   ├── monster_formant.png
│   │   │   │   │   ├── monster_phonmotivator.png
│   │   │   │   │   ├── monster_phontermin.png
│   │   │   │   │   └── monster_runner.png
│   │   │   │   ├── level_2
│   │   │   │   │   ├── monster_gloss.png
│   │   │   │   │   ├── monster_linguist.png
│   │   │   │   │   ├── monster_motivator.png
│   │   │   │   │   ├── monster_researcher.png
│   │   │   │   │   ├── monster_runner.png
│   │   │   │   │   ├── monster_sphinx.png
│   │   │   │   │   └── monster_terminology.png
│   │   │   │   ├── level_3
│   │   │   │   │   ├── monster_communicator.png
│   │   │   │   │   ├── monster_helper.png
│   │   │   │   │   ├── monster_questioner.png
│   │   │   │   │   ├── monster_runner.png
│   │   │   │   │   ├── monster_sphinx.png
│   │   │   │   │   └── monster_tfidf.png
│   │   │   │   ├── level_4
│   │   │   │   │   ├── monster_childspeech.png
│   │   │   │   │   ├── monster_motivator.png
│   │   │   │   │   ├── monster_neuroanatomy.png
│   │   │   │   │   ├── monster_runner.png
│   │   │   │   │   ├── monster_schizophrenia_1.png
│   │   │   │   │   ├── monster_schizophrenia_2.png
│   │   │   │   │   ├── monster_schizophrenia_3.png
│   │   │   │   │   ├── monster_schizophrenia_4.png
│   │   │   │   │   └── monster_silent.png
│   │   │   │   ├── empty.png
│   │   │   │   └── monster.png
│   │   │   ├── protagonists
│   │   │   │   ├── anya.png
│   │   │   │   ├── anya_right.png
│   │   │   │   ├── danya.png
│   │   │   │   ├── danya_right.png
│   │   │   │   ├── denis.png
│   │   │   │   ├── denis_right.png
│   │   │   │   ├── lera.png
│   │   │   │   ├── lera_right.png
│   │   │   │   └── student.png
│   │   │   ├── box.png
│   │   │   └── box_story.png
│   │   ├── maze_tiles
│   │   │   ├── level_0
│   │   │   │   ├── monsters
│   │   │   │   │   ├── monster_esperanto.png
│   │   │   │   │   ├── monster_motivator.png
│   │   │   │   │   └── monster_runner.png
│   │   │   │   ├── walls
│   │   │   │   │   ├── wall_corner.png
│   │   │   │   │   ├── wall_corner_south.png
│   │   │   │   │   ├── wall_single.png
│   │   │   │   │   ├── wall_straight.png
│   │   │   │   │   └── wall_straight_south.png
│   │   │   │   ├── enemy.png
│   │   │   │   ├── entrance.png
│   │   │   │   ├── exit.png
│   │   │   │   └── floor.png
│   │   │   ├── level_1
│   │   │   │   ├── monsters
│   │   │   │   │   ├── monster_agressive.png
│   │   │   │   │   ├── monster_amateur.png
│   │   │   │   │   ├── monster_expert.png
│   │   │   │   │   ├── monster_formant.png
│   │   │   │   │   ├── monster_phonmotivator.png
│   │   │   │   │   ├── monster_phontermin.png
│   │   │   │   │   └── monster_runner.png
│   │   │   │   ├── walls
│   │   │   │   │   ├── wall_corner.png
│   │   │   │   │   ├── wall_corner_south.png
│   │   │   │   │   ├── wall_single.png
│   │   │   │   │   ├── wall_straight.png
│   │   │   │   │   └── wall_straight_south.png
│   │   │   │   ├── enemy.png
│   │   │   │   ├── entrance.png
│   │   │   │   ├── exit.png
│   │   │   │   └── floor.png
│   │   │   ├── level_2
│   │   │   │   ├── monsters
│   │   │   │   │   ├── monster_gloss.png
│   │   │   │   │   ├── monster_linguist.png
│   │   │   │   │   ├── monster_motivator.png
│   │   │   │   │   ├── monster_researcher.png
│   │   │   │   │   ├── monster_runner.png
│   │   │   │   │   ├── monster_sphinx.png
│   │   │   │   │   └── monster_terminology.png
│   │   │   │   ├── walls
│   │   │   │   │   ├── wall_corner.png
│   │   │   │   │   ├── wall_corner_south.png
│   │   │   │   │   ├── wall_single.png
│   │   │   │   │   ├── wall_straight.png
│   │   │   │   │   └── wall_straight_south.png
│   │   │   │   ├── enemy.png
│   │   │   │   ├── entrance.png
│   │   │   │   ├── exit.png
│   │   │   │   └── floor.png
│   │   │   ├── level_3
│   │   │   │   ├── monsters
│   │   │   │   │   ├── monster_communicator.png
│   │   │   │   │   ├── monster_helper.png
│   │   │   │   │   ├── monster_questioner.png
│   │   │   │   │   ├── monster_runner.png
│   │   │   │   │   ├── monster_sphinx.png
│   │   │   │   │   └── monster_tfidf.png
│   │   │   │   ├── walls
│   │   │   │   │   ├── wall_corner.png
│   │   │   │   │   ├── wall_corner_south.png
│   │   │   │   │   ├── wall_single.png
│   │   │   │   │   ├── wall_straight.png
│   │   │   │   │   └── wall_straight_south.png
│   │   │   │   ├── enemy.png
│   │   │   │   ├── entrance.png
│   │   │   │   ├── exit.png
│   │   │   │   └── floor.png
│   │   │   ├── level_4
│   │   │   │   ├── monsters
│   │   │   │   │   ├── monster_childspeech.png
│   │   │   │   │   ├── monster_motivator.png
│   │   │   │   │   ├── monster_neuroanatomy.png
│   │   │   │   │   ├── monster_runner.png
│   │   │   │   │   ├── monster_schizophrenia_1.png
│   │   │   │   │   ├── monster_schizophrenia_2.png
│   │   │   │   │   ├── monster_schizophrenia_3.png
│   │   │   │   │   ├── monster_schizophrenia_4.png
│   │   │   │   │   └── monster_silent.png
│   │   │   │   ├── walls
│   │   │   │   │   ├── wall_corner.png
│   │   │   │   │   ├── wall_corner_south.png
│   │   │   │   │   ├── wall_single.png
│   │   │   │   │   ├── wall_straight.png
│   │   │   │   │   └── wall_straight_south.png
│   │   │   │   ├── enemy.png
│   │   │   │   ├── entrance.png
│   │   │   │   ├── exit.png
│   │   │   │   └── floor.png
│   │   │   └── player
│   │   │       ├── anya
│   │   │       │   ├── player.png
│   │   │       │   ├── walk1.png
│   │   │       │   ├── walk2.png
│   │   │       │   ├── walk3.png
│   │   │       │   └── walk4.png
│   │   │       ├── danya
│   │   │       │   ├── player.png
│   │   │       │   ├── walk1.png
│   │   │       │   ├── walk2.png
│   │   │       │   ├── walk3.png
│   │   │       │   └── walk4.png
│   │   │       ├── denis
│   │   │       │   ├── player.png
│   │   │       │   ├── walk1.png
│   │   │       │   ├── walk2.png
│   │   │       │   ├── walk3.png
│   │   │       │   └── walk4.png
│   │   │       ├── lera
│   │   │       │   ├── player.png
│   │   │       │   ├── walk1.png
│   │   │       │   ├── walk2.png
│   │   │       │   ├── walk3.png
│   │   │       │   └── walk4.png
│   │   │       └── student
│   │   │           ├── player.png
│   │   │           ├── walk1.png
│   │   │           ├── walk2.png
│   │   │           ├── walk3.png
│   │   │           └── walk4.png
│   │   ├── menu
│   │   │   ├── keybind_buttons
│   │   │   │   ├── decrease_volume_button
│   │   │   │   │   ├── decrease_volume_button.png
│   │   │   │   │   ├── decrease_volume_button_hovered.png
│   │   │   │   │   └── decrease_volume_button_pressed.png
│   │   │   │   ├── end_text_animation_button
│   │   │   │   │   ├── end_text_animation_button.png
│   │   │   │   │   ├── end_text_animation_button_hovered.png
│   │   │   │   │   └── end_text_animation_button_pressed.png
│   │   │   │   ├── increase_volume_button
│   │   │   │   │   ├── increase_volume_button.png
│   │   │   │   │   ├── increase_volume_button_hovered.png
│   │   │   │   │   └── increase_volume_button_pressed.png
│   │   │   │   ├── move_down_button
│   │   │   │   │   ├── move_down_button.png
│   │   │   │   │   ├── move_down_button_hovered.png
│   │   │   │   │   └── move_down_button_pressed.png
│   │   │   │   ├── move_left_button
│   │   │   │   │   ├── move_left_button.png
│   │   │   │   │   ├── move_left_button_hovered.png
│   │   │   │   │   └── move_left_button_pressed.png
│   │   │   │   ├── move_right_button
│   │   │   │   │   ├── move_right_button.png
│   │   │   │   │   ├── move_right_button_hovered.png
│   │   │   │   │   └── move_right_button_pressed.png
│   │   │   │   ├── move_up_button
│   │   │   │   │   ├── move_up_button.png
│   │   │   │   │   ├── move_up_button_hovered.png
│   │   │   │   │   └── move_up_button_pressed.png
│   │   │   │   └── no_task_advance_button
│   │   │   │       ├── no_task_advance_button.png
│   │   │   │       ├── no_task_advance_button_hovered.png
│   │   │   │       └── no_task_advance_button_pressed.png
│   │   │   ├── left_settings_button
│   │   │   │   ├── left_settings_button.png
│   │   │   │   ├── left_settings_button_hovered.png
│   │   │   │   └── left_settings_button_pressed.png
│   │   │   ├── right_settings_button
│   │   │   │   ├── right_settings_button.png
│   │   │   │   ├── right_settings_button_hovered.png
│   │   │   │   └── right_settings_button_pressed.png
│   │   │   ├── start_button
│   │   │   │   ├── start_button.png
│   │   │   │   ├── start_button_hovered.png
│   │   │   │   └── start_button_pressed.png
│   │   │   ├── bg.png
│   │   │   ├── lossbg.png
│   │   │   └── winbg.png
│   │   ├── diagram.png
│   │   ├── icon.ico
│   │   └── icon.png
│   ├── models
│   │   ├── existing_words_analysis
│   │   │   └── dicts_ru
│   │   │       ├── grammemes.json
│   │   │       ├── gramtab-opencorpora-ext.json
│   │   │       ├── gramtab-opencorpora-int.json
│   │   │       ├── meta.json
│   │   │       ├── paradigms.array
│   │   │       ├── prediction-suffixes-0.dawg
│   │   │       ├── prediction-suffixes-1.dawg
│   │   │       ├── prediction-suffixes-2.dawg
│   │   │       ├── suffixes.json
│   │   │       └── words.dawg
│   │   └── sentiment_analysis
│   └── music
│       ├── Boss.wav
│       ├── Challenge.wav
│       ├── Correct Stamp.wav
│       ├── Door Closes.wav
│       ├── Door Opens.wav
│       ├── Gameover.wav
│       ├── Incorrect Stamp.wav
│       ├── Intro.wav
│       ├── Lol.wav
│       ├── Maze.wav
│       ├── Menu.wav
│       ├── Monster.wav
│       ├── Outro.wav
│       ├── Roll.wav
│       ├── Start Challenge.wav
│       ├── Start Game.wav
│       ├── Transition.wav
│       └── Victory.wav
├── docs
│   ├── API.md
│   ├── ARCHITECTURE.md
│   ├── CHANGELOG.md
│   ├── INSTALL.md
│   └── README.md
├── log
│   └── console_output_goes_here
├── MAILBOX
│   ├── Листок.txt
│   └── Фото.png
├── src
│   ├── level_building
│   │   ├── button.py
│   │   ├── challenge.py
│   │   ├── checker.py
│   │   ├── dialogue.py
│   │   ├── enemy.py
│   │   └── maze.py
│   ├── playstates
│   │   ├── basestate.py
│   │   ├── challengestate.py
│   │   ├── dialoguestate.py
│   │   ├── mazestate.py
│   │   └── menustate.py
│   ├── assetscreation.py
│   ├── config.py
│   ├── storyscript.py
│   └── util.py
├── tests
│   ├── __init__.py
│   ├── assetscreation_test.py
│   ├── challengestate_test.py
│   ├── conftest.py
│   └── mazestate_test.py
├── config.json
├── icon.ico
├── main.py
├── main.spec
├── poetry.lock
├── pyproject.toml
└── README.md
```

## Взаимодействие компонентов

Игра построена вокруг цикла состояний и скриптового управления сюжетом. Основные игровые режимы 
(лабиринт, диалог, задание, меню) реализованы как классы-состояния, наследующие BaseState. Переключение между ними 
контролируется StoryScript, а главный цикл main.py вызывает методы текущего состояния и обрабатывает команды.

### Запуск игры и главный цикл

Main создаёт все объекты состояний, StoryScript загружает переменные-трекеры прогресса. В цикле по очереди обрабатываются события Pygame, 
вызываются соответствующие методы текущего состояния, а затем обрабатываются возвращаемые ими команды, которые могут изменить состояние,
завершить игру, изменить FPS и многое другое.

### Переключение состояний

StoryScript – центральный контроллер сюжета. Он отслеживает текущий прогресс, хранит данные комнат, обрабатывает переходы. 
Когда игрок завершает диалог, достигает выхода или наступает на монстра, StoryScript меняет `current_state_type` в Main и 
вызывает `associate_current_state()`, чтобы подставить нужный объект состояния.

### Настройки управления

В MenuState кнопки настройки управления вызывают диалог ожидания нажатия. После ввода новая клавиша сохраняется в Config и записывается 
в файл. После этого Main передаёт привязки в соответствующие состояния, которые используют их в обработке ввода.
