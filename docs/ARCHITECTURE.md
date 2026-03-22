# Архитектура проекта

## Структура

`levelBuilding`

**Button.py** – класс кнопки, хранит координаты, размеры, текст и состояние (ButtonState). Метод is_hovered проверяет, находится ли курсор над кнопкой. Используется в состояниях диалога и заданий для создания интерактивных элементов.

**Challenge.py** – загружает JSON с описанием заданий (окна с вопросами, изображениями, действиями). Предоставляет геттеры для всех полей. Содержит методы проверки ответов: check_current_answer (для текстового ввода) и check_choice (для выбора из вариантов). Реализует чекеры plainequality, ling_terms, wordmatch, sentiment_rubert (с использованием Hugging Face pipeline). Позволяет пропускать задание при наличии артефакта через can_skip_with_artifact.

**Dialogue.py** – загружает JSON диалога. Содержит список реплик, метаданные (имена персонажей, спрайт собеседника, наличие музыки, флаги). Методы извлекают данные для конкретной реплики: текст, тип действия (выбор вариантов или сохранение ввода), варианты, переходы, смену фона. Сохраняет введённые пользователем ответы и сделанные выборы.

**Enemy.py** – иерархия врагов. Базовый класс Enemy хранит координаты, имя, активность. Методы: check_collision (проверка столкновения с игроком), deactivate (исчезновение после диалога). Наследник StationaryEnemy – неподвижный враг, используемый в текущей версии.

**Maze.py** – генерация лабиринта модифицированным DFS-алгоритмом. Класс Tile – вспомогательный для хранения координат. Основной класс Maze хранит размеры, позиции входа/выхода и внутреннюю карту pattern. Метод generate_maze создаёт проходы, учитывая параметры more_random и curving.

`playstates`

**Main.py** – бесконечный цикл. Вызывает `handle_input`, `update`, `draw` текущего состояния, обрабатывает команды из `get_command`.

**BaseState.py** – определяет интерфейс для всех состояний. Каждое состояние (лабиринт, диалог, задание) наследуется от него и реализует свою логику.

**Challenge.py** – загружает JSON-файлы с заданием, предоставляет методы для получения данных (текст, варианты, изображения) и проверки ответов через чекеры (plainequality, ling_terms, wordmatch, sentiment_rubert). Чекеры изолированы и могут быть легко расширены.

**StoryScript.py** – отвечает за переходы между состояниями. При выборе игрока (например, в диалоге) передаётся команда, которая меняет текущее состояние.

**AssetsCreation.py** – единое место загрузки спрайтов, звуков и их кэширования. Для добавления нового ресурса нужно написать функцию загрузки (по образцу add_right_speak_sprite) и вызвать её в нужном состоянии.

**Config.py** – загружает и сохраняет настройки из config.json. Преобразует хранящиеся в файле строковые представления Unicode в символы и обратно. Предоставляет методы для получения привязок клавиш для каждого режима (лабиринт, диалог, задание). Позволяет изменять настройки и записывать их обратно.

**Util.py** – хранит общие константы (размеры экрана, клеток, кнопок), перечисления (StateType, Command, WallPattern, Border, ButtonState, Awaiting), вспомогательную функцию для центрирования объектов.

## Диаграммы

Диаграмма классов в папке `src`:
![Диаграмма классов в папке src](/assets/images/diagram.png)

Текстовая диаграмма для директории файлов:
```bash
├── assets
│   ├── data
│   │   ├── challenges
│   │   │   ├── level_0
│   │   │   │   └── enemy_at_exit.json
│   │   │   └── level_1
│   │   │       └── enemy_at_exit.json
│   │   └── dialogues
│   │       ├── intro.json
│   │       ├── level_0
│   │       │   ├── enemy_at_exit.json
│   │       │   └── exit_door.json
│   │       └── level_1
│   │           ├── enemy_at_exit.json
│   │           └── exit_door.json
│   ├── images
│   │   ├── challenge
│   │   │   ├── back_button
│   │   │   │   ├── back_button.png
│   │   │   │   ├── back_button_hovered.png
│   │   │   │   └── back_button_pressed.png
│   │   │   ├── bg.png
│   │   │   ├── card.png
│   │   │   ├── choice_button
│   │   │   │   ├── choice_button.png
│   │   │   │   ├── choice_button_hovered.png
│   │   │   │   └── choice_button_pressed.png
│   │   │   ├── correct.png
│   │   │   ├── forth_button
│   │   │   │   ├── forth_button.png
│   │   │   │   ├── forth_button_hovered.png
│   │   │   │   └── forth_button_pressed.png
│   │   │   ├── incorrect.png
│   │   │   ├── levels
│   │   │   │   └── level_0
│   │   │   │       └── student.png
│   │   │   ├── submit_button
│   │   │   │   ├── submit_button.png
│   │   │   │   ├── submit_button_hovered.png
│   │   │   │   └── submit_button_pressed.png
│   │   │   ├── tip_card.png
│   │   │   └── transitions
│   │   │       ├── check.png
│   │   │       ├── end.png
│   │   │       └── start.png
│   │   ├── dialogue
│   │   │   ├── backgrounds
│   │   │   │   └── bg.png
│   │   │   ├── box.png
│   │   │   ├── choice_button
│   │   │   │   ├── choice_button.png
│   │   │   │   ├── choice_button_hovered.png
│   │   │   │   └── choice_button_pressed.png
│   │   │   ├── monsters
│   │   │   │   ├── level_0
│   │   │   │   │   └── enemy_at_exit.png
│   │   │   │   ├── level_1
│   │   │   │   │   └── enemy_at_exit.png
│   │   │   │   └── monster.png
│   │   │   └── protagonists
│   │   │       └── student.png
│   │   ├── maze_tiles
│   │   │   ├── level_0
│   │   │   │   ├── enemy.png
│   │   │   │   ├── entrance.png
│   │   │   │   ├── exit.png
│   │   │   │   ├── floor.png
│   │   │   │   └── walls
│   │   │   │       ├── wall_corner.png
│   │   │   │       ├── wall_corner_south.png
│   │   │   │       ├── wall_single.png
│   │   │   │       ├── wall_straight.png
│   │   │   │       └── wall_straight_south.png
│   │   │   ├── level_1
│   │   │   │   ├── enemy.png
│   │   │   │   ├── entrance.png
│   │   │   │   ├── exit.png
│   │   │   │   ├── floor.png
│   │   │   │   └── walls
│   │   │   │       ├── wall_corner.png
│   │   │   │       ├── wall_corner_south.png
│   │   │   │       ├── wall_single.png
│   │   │   │       ├── wall_straight.png
│   │   │   │       └── wall_straight_south.png
│   │   │   ├── level_2
│   │   │   │   ├── enemy.png
│   │   │   │   ├── entrance.png
│   │   │   │   ├── exit.png
│   │   │   │   ├── floor.png
│   │   │   │   └── walls
│   │   │   │       ├── wall_corner.png
│   │   │   │       ├── wall_corner_south.png
│   │   │   │       ├── wall_single.png
│   │   │   │       ├── wall_straight.png
│   │   │   │       └── wall_straight_south.png
│   │   │   ├── level_3
│   │   │   │   ├── enemy.png
│   │   │   │   ├── entrance.png
│   │   │   │   ├── exit.png
│   │   │   │   ├── floor.png
│   │   │   │   └── walls
│   │   │   │       ├── wall_corner.png
│   │   │   │       ├── wall_corner_south.png
│   │   │   │       ├── wall_single.png
│   │   │   │       ├── wall_straight.png
│   │   │   │       └── wall_straight_south.png
│   │   │   ├── level_4
│   │   │   │   ├── enemy.png
│   │   │   │   ├── entrance.png
│   │   │   │   ├── exit.png
│   │   │   │   ├── floor.png
│   │   │   │   └── walls
│   │   │   │       ├── wall_corner.png
│   │   │   │       ├── wall_corner_south.png
│   │   │   │       ├── wall_single.png
│   │   │   │       ├── wall_straight.png
│   │   │   │       └── wall_straight_south.png
│   │   │   └── player
│   │   │       ├── player.png
│   │   │       ├── walk1.png
│   │   │       ├── walk2.png
│   │   │       ├── walk3.png
│   │   │       └── walk4.png
│   │   └── menu
│   │       ├── bg.png
│   │       ├── keybind_buttons
│   │       │   ├── decrease_volume_button
│   │       │   │   ├── decrease_volume_button.png
│   │       │   │   ├── decrease_volume_button_hovered.png
│   │       │   │   └── decrease_volume_button_pressed.png
│   │       │   ├── end_text_animation_button
│   │       │   │   ├── end_text_animation_button.png
│   │       │   │   ├── end_text_animation_button_hovered.png
│   │       │   │   └── end_text_animation_button_pressed.png
│   │       │   ├── increase_volume_button
│   │       │   │   ├── increase_volume_button.png
│   │       │   │   ├── increase_volume_button_hovered.png
│   │       │   │   └── increase_volume_button_pressed.png
│   │       │   ├── move_down_button
│   │       │   │   ├── move_down_button.png
│   │       │   │   ├── move_down_button_hovered.png
│   │       │   │   └── move_down_button_pressed.png
│   │       │   ├── move_left_button
│   │       │   │   ├── move_left_button.png
│   │       │   │   ├── move_left_button_hovered.png
│   │       │   │   └── move_left_button_pressed.png
│   │       │   ├── move_right_button
│   │       │   │   ├── move_right_button.png
│   │       │   │   ├── move_right_button_hovered.png
│   │       │   │   └── move_right_button_pressed.png
│   │       │   ├── move_up_button
│   │       │   │   ├── move_up_button.png
│   │       │   │   ├── move_up_button_hovered.png
│   │       │   │   └── move_up_button_pressed.png
│   │       │   └── no_task_advance_button
│   │       │       ├── no_task_advance_button.png
│   │       │       ├── no_task_advance_button_hovered.png
│   │       │       └── no_task_advance_button_pressed.png
│   │       └── start_button
│   │           ├── start_button.png
│   │           ├── start_button_hovered.png
│   │           └── start_button_pressed.png
│   └── music
│       ├── Challenge.wav
│       ├── Intro.wav
│       ├── Monster.wav
│       └── Start Challenge.wav
├── config.json
├── docs
│   ├── API.md
│   ├── ARCHITECTURE.md
│   ├── INSTALL.md
│   ├── README.md
│   └── CHANGELOG.md
├── tests
│   ├── __init__.py
│   ├── AssetsCreation_test.py
│   └── conftest.py
├── README.md
└── src
    ├── AssetsCreation.py
    ├── Config.py
    ├── levelBuilding
    │   ├── Button.py
    │   ├── Challenge.py
    │   ├── Dialogue.py
    │   ├── Enemy.py
    │   └── Maze.py
    ├── Main.py
    ├── playstates
    │   ├── BaseState.py
    │   ├── ChallengeState.py
    │   ├── DialogueState.py
    │   ├── MazeState.py
    │   └── MenuState.py
    ├── StoryScript.py
    └── Util.py
```

## Взаимодействие компонентов

Игра построена вокруг цикла состояний и скриптового управления сюжетом. Основные игровые режимы 
(лабиринт, диалог, задание, меню) реализованы как классы-состояния, наследующие BaseState. Переключение между ними 
контролируется StoryScript, а главный цикл Main.py вызывает методы текущего состояния и обрабатывает команды.

### Запуск игры и главный цикл

Main.py создаёт все объекты состояний, StoryScript загружает настройки. В цикле обрабатывает события Pygame, 
вызывает соответствующие методы текущего состояния, а затем команды, которые могут изменить состояние, завершить игру
или изменить FPS.

### Переключение состояний

StoryScript – центральный контроллер сюжета. Он отслеживает текущий прогресс, хранит данные комнат, обрабатывает переходы. 
Когда игрок завершает диалог, достигает выхода или наступает на монстра, StoryScript меняет `current_state_type` в Main.py и 
вызывает `associate_current_state()`, чтобы подставить нужный объект состояния.

### Настройки управления

В MenuState кнопки управления вызывают диалог ожидания нажатия. После ввода новая клавиша сохраняется в Config и записывается 
в файл. При запуске лабиринта или диалога Main.py передаёт привязки в соответствующие состояния, которые используют их в обработке ввода.