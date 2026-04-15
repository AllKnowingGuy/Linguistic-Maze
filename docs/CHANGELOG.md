# Changelog

## 2026-04-15 - The quick update - v1.0.1 (CRASH FIX)

- Made the app write all output to a log file instead of a console to fix issues where stdout was None in some checks
- Added some progress-tracking prints to `StoryScript`
- Added some funnies to the `MAILBOX`
- Slightly tweaked maze generation to make mazes even more chaotic

## 2026-04-14 - Pack it up(date) - v1.0 (GAME RELEASE)

- **Built the executable file** of the game (can be found in the Releases tab)
- Replaced all placeholder Paint-drawn assets with newer finger-drawn versions
- Changed the font again to support Yakut characters in gloss monster's challenge
- Implemented **sound and music volume control in-game**
- Added a **drumroll sound** that plays before the answer is stamped as correct or incorrect
- Made the game **zoom to the maze entrance** when pressing start
- Made the game launch with some models missing but warn the player when pressing start
- Greatly improved performance of the maze state when the player is idle and the moving monsters are out of sight
- Added 2 buttons to the main menu to show and hide the 8 settings buttons
- Made `ChallengeState` warn the player when trying to submit with unanswered questions
- Created `checker.py` in `level_building`, the new `Checker` object handles challenge answers checking as well as several dialogue input checks
- Removed `check_current_answer` from `Challenge` and most monster dialogue checks from `StoryScript`
- Improved button pressing in all playstates: at the moment of the mouse release the button under the cursor becomes hovered
- Fixed several issues with NLP models, Pymorphy params are now kept in the `assets` folder
- Made patrolling enemies avoid walking into doors
- Updated path building and checking to reduce `os` lib usage
- Updated some checks to reduce nesting
- Updated a ton of docstrings
- Fixed a jump error in the gloss monster's dialogue
- Fixed a critical post-challenge dialogue jump error when scoring 0 in challenges

## 2026-03-30 - W update

- Created **boss and outro dialogues** with proper transitions
- Added remaining monster checks to `StoryScript`
- Finished Room 3 and Room 4 planning
- Added remaining monster portraits and **all character portraits**
- Updated many graphic assets and added a bunch of **sounds and music**
- Implemented **win screen** and even better game restart
- Dialogue files now have info on whether they are story dialogues and require transparent boxes
- Dialogue files can now have info on the sound to be played before the line is printed if needed
- Dialogues can now set protagonists as right speakers, checking that they're different from the chosen one
- Changed the font to match the game vibe better
- Created a (not so) secret folder

## 2026-03-28 - Skin update
- Implemented differentiated skins for four playable characters, chosen during the intro
- `mazestate.py` has a new `self.player_name` attribute, which is responsible for different playable characters' tiles
- Created four playable character folders in `images/maze_tiles/player`, with the fifth one being the default one
- Added new monster sprites

## 2026-03-28 - L update

- Implemented **gameover** and proper game restart (on loss at least)
- Added **menu and gameover music**
- Wrote interaction scripts for several monsters in `StoryScript`, including checking existing words using **Pymorphy**
- Made `StoryScript` not only pass the chosen character to `DialogueState` but also remember the choice itself
- Tweaked "plainequality" challenge checker: it now makes the answer lowercase (as such, some challenge files were changed so that their reference answers exclude uppercase letters)
- Brought dialogue and challenge choice buttons closer together
- Resized dialogue portraits to the intended proportions
- Made the transformers model load only once at the app launch to improve performance
- Fixed various bugs and errors with door dialogue building and handling
- Fixed a bug with unsuccessful type checking in `dialogue.py` by using `isinstance`
- The game now has **its own icon**

## 2026-03-27 Running monsters update

- Implemented the `PatrollingEnemy` class in `Enemy.py` for enemies that run around the levels
- Changed the sprite loading functions for enemies. Each enemy now has its own personal sprite, as seen by the `enemy_name` parameter in `load_enemy_tile` in `assetscreation.py`
- Added `monsters` folders in maze tiles of each level, which hold individual monster sprites
- Changed `workflows` to work with poetry instead of pip

## 2026-03-26 - Supervized update 1

- **Renamed all Python files to use snake case instead of camel case**. As such, all content of `src` and `tests` has had capital letters replaced with lowercase ones, and `levelBuilding` has been renamed to `level_building`
- Put almost all file paths into `Path` objects
- Changed the gloss challenge in the 2nd maze room as the previous one contained an error
- Made saved dialogue answers **use line indices** and not line texts as dict keys
- Made dialogues check progress **between inputting answers and changing lines**
- Made door dialogues use the transparent box
- Fixed a bunch of errors caused by extra or missing commas in JSONs and changed places of several '\n's
- Added `.gitignore`

## 2026-03-23 - Path of the Linguist update

- Made dialogue and challenge texts splittable by '\n' and remade `draw_text_by_letter` in the respective states
- Added dialogue and challenge JSON files for real monsters of the game according to the story (levels 0-2)
- Replaced intro dialogue with the final one and changed intro dialogue processing in `StoryScript`
- Moved room structure from `StoryScript` to JSON files and added info about the monsters and the exit conditions
- Added custom dialogue images for several monsters (levels 0-2)
- Added a new transparent dialogue box for rich-BG dialogues and changed the texture of the standard one
- Made `setup_dialogue` accept not only JSON paths but also local dialogue dicts
- Made `StoryScript` build universal exit door dialogues based on player progress
- Implemented room regeneration (without moving to the next one) and attempt system
- Made `DialogueState` display character's name instead of 'Протагонист' based on player's intro dialogue choice
- Added music to the maze
- `StoryScript.py` now imports `Main` class, and the `game` argument of `update_game_progress` is now typed as `Main`
- `StoryScript` is now imported in `Main.__init__` in `Main.py` to avoid import conflicts
- Added some docstrings to `AssetsCreation.py`
- Fixed menu config changes not being used in the current game session
- Rebound text animation ending from Enter back to Esc

## 2026-03-22 - Documentation overhaul

- Created `API.md` with comprehensive descriptions of dialogue and challenge JSON formats, checkers, artifact system, and level creation
- Created `INSTALL.md` with step-by-step installation instructions for Windows, Linux, and macOS, including Poetry setup, `fasttext` wheel installation, and troubleshooting
- Added `ARCHITECTURE.md` detailing the project structure, component interaction, and control flow between `Main`, `StoryScript`, and playstates
- Extended `README.md` with clearer usage instructions, control schemes, and links to developer documentation
- Added Mermaid class diagram to visualize relationships between key classes (`Challenge`, `Dialogue`, `MazeState`, `StoryScript`, etc.) and their dependencies
- Documented the role of `StoryScript` as the central story manager and how states communicate via commands
- Moved this **CHANGELOG** to the docs folder

## 2026-03-21 - Artifact and choice support
- Added `can_skip_with_artifact` method to Challenge – allows skipping a task if the player has the required artifact (e.g., “дудка”)
- Added check_choice method for handling multiple‑choice actions (choosefrom); returns correctness, respect change, and awarded artifact
- Extended `_read_and_fill` to load optional metadata from the JSON file (e.g., background music, atmosphere settings)
- Added `get_window_artifact` getter to retrieve the artifact granted by a specific window (if any)
- Refactored `sentiment_rubert` checker to lazily initialize the Hugging Face pipeline only when first needed, preventing unnecessary model loading
- Minor linting and type hint improvements across the file

## 2026-03-21 - Test update 2
- Implemented pytest and workflow for `MazeState.py` and `ChallengeState.py`

## 2026-03-20 - Test update 1 (as in, the update that adds tests)
- Implemented pytest for `AssetsCreation.py`
- Fixed a date error in `CHANGELOG.md`
- Added workflows

## 2026-03-15 - Déjà vu update

- Created `MenuState.py` for the main menu; as of now it has a start button and keybind buttons, one for each keybind
- Implemented key binding **in game** through main menu buttons
- Rebound text animation ending from Esc to Enter
- Made the game **replayable** by changing the behavior of the last dialogue in `StoryScript` (it now redirects the player to the menu)
- Fixed a bug where `DialogueState` and `ChallengeState` would not forget answers to previous dialogues and challenges
- Linted out all Python files
- Answer checking has been moved from `ChallengeState` to `Challenge`
- Monster deactivation now uses `Enemy.deactivate` instead of directly modifying the enemy's attribute
- Added a nice on-beat loading percent animation to the challenge intro
- Added different moster portraits to different levels, basic monster portrait is now outside all level folders

## 2026-03-13 - Let it play update

- The game now uses Pygame's **mixer setup and functions** in order to control in-game music
- Added **music playback** to dialogues and challenges (before submitting)
- Dialogues can now be **ominous**, making the game play monster encounter music during them. These dialogues always end on music beat to make a transition to the challenge music
- A special sound now plays during the challenge intro to make a transition to the challenge music
- Dialogues now start playing on a special command different from `setup_dialogue` to not play music when the game is not in the dialogue state
- Dialogues and challenges are even more optimized now as they **cache large screen images** that are blitted on one another and not changed often
- Moved and resized some challenge content
- Made `draw_text_by_letter` in both `DialogueState` and `ChallengeState` move line cursor slower
- Removed `DialogueState.cursor_sym`: text pauses are handled by `draw_text_by_letter` now
- Fixed several challenge bugs by resetting more attributes in `setup_challenge`

## 2026-03-13 - Todos done update

- Filled `config.json` with game settings data
- Created `Config.py` for keeping, providing and changing loaded config settings
- Implemented **key binding** for almost all possible key presses in all playstates (finally - [AllKnowingGuy](https://github.com/AllKnowingGuy))
- Slightly reorganized `handle_input` of `DialogueState`
- Moved button state switches on mouse clicks to `BaseState`
- Prohibited entering even more unrenderable characters in input fields
- Implemented loading and using different backgrounds in `DialogueState`, and moved the placeholder BG to `images\dialogue\backgrounds`
- Renamed `add_player_speak_sprite` and `add_character_speak_sprite` to `add_left_speak_sprite` and `add_right_speak_sprite` respectively
- Added optional custom path loading for `add_left_speak_sprite`
- Made a `Util.py` function for retrieving coordinates needed for centering objects on the screen
- Added several constants to `AssetsCreation.py`
- Made the tip card in challenges smaller and more centered
- Removed image scaling in `add_window_image` of `AssetsCreation.py`

## 2026-03-12 - Draw suppression update

- **Greatly optimized** all 3 game modes by making their states only redraw game components if one or more of them have changed position or have been replaced
- Added a `needs_screen_update` attribute to `BaseState` so that every playstate is able to optimize its drawing
- `DialogueState` now only re-renders texts when they are updated
- `ChallengeState` now makes use of `execute_before_draw`
- Added respect points to dialogues (currently only per dialogue points) and challenge tasks
- Made `StoryScript` add monster's dialogue points to the current room score
- Made `ChallengeState` give or take points based on correctness and show the challenge score on the result screen
- Moved text field updates on typing and button state switches on mouse hovering to `BaseState` to reduce shared code between `DialogueState` and `ChallengeState`
- Made image scaling optional when loading them in `AssetsCreation.py`

## 2026-03-12 - Visual update #1

- Added the 4th frame to the player walk cycle, as well as an overall update to player's design
- Added a variety of wall tiles and enemies for future levels

## 2026-03-11 - Challenging update

- Created `ChallengeState.py` (inspired by `DialogueState.py`)
- Created challenge data structure in `Challenge.py` and added a test challenge file to `assets`
- Implemented starting a challenge after talking to a monster
- Maze rooms are now levelled starting from 0 instead of 1
- Implemented maze checks before transition (thanks for the pull request [ddmoreva](https://github.com/ddmoreva)!)
- Reorganized `StoryScript` to reduce unnecessary code duplication
- Added many attributes of several classes to their `__init__`s to avoid potential exploits and test falls
- Made a debug flag in `StoryScript.py` to skip dialogues by only playing the 1st line of each
- Removed `ENCOUNTER_ENEMY` command for the lack of use, monster collision is now checked when `CHECK_PROGRESS` is sent

## 2026-03-09 - Dialogue independence update

- **Overhauled the dialogue system** to store dialogues and their meta in JSON files, which are read in `Dialogue` class
- Dialogue data sent to `Dialogue` object initialization now may include **right character sprite path** and **jumps info** for lines and buttons that need to redirect the dialogue to specific lines (the redirection was previously done in `StoryScript`)
- Separated main game display and FPS counter into **2 different layers** to be blitted on the main Pygame display. Playstates only work with the first layer
- Extracted all button data from `DialogueState` and put it into the new `Button` class, it can be imported in any playstate that has buttons
- Implemented playstate support for **key and mouse release functions**
- Improved dialogue buttons to check mouse hovering in a separate function and execute their functionality only after the mouse is released while hovering over them
- Reworked all mouse functions to use info of their respective events instead of collecting the mouse data anew
- The player now starts a dialogue with any monster they encounter, and the monster is removed after the dialogue
- Modernized `assets` folder to have different folders for images and text data and created folder structure for `dialogue` image folder
- Speaker's name is now shown when they speak
- Tweaked new maze character and monster sprites handling

## 2026-03-07 - Spooky Scary update

- Added the `Enemy` class, located in brand new `Enemy.py`. Very raw functionality for now
- New `ENCOUNTER_ENEMY` command in `Util.py` for future coding
- Added enemy sprites into the level sprites folders
- The playable character is now **animated** at glorious 5 frames per second!
- Relocated the playable character sprite into its own folder within the `tiles` folder
- Darkness effect is now implemented. It can be turned off by changing the `darkness_enabled` flag in `MazeState.py`

## 2026-03-06 - Better experience update

- Dialogue system now supports **background changing** (custom backgrounds will be added to `DialogueState` later)
- Added the functionality of capturing the previous frame and using it as a dialogue BG (to make dialogues visually appear just above maze rooms)
- Temporary removed FPS display from the screen for proper screen capturing in its current state
- Expanded `setup_maze` docstring and added dialogue structure hints to `Dialogue.py`
- Restructured `StoryScript` by splitting checks into functions for each individual dialogue and room
- Flags for specific individual dialogues, rooms and challenges are now stored in separate dicts in `StoryScript`
- Changed the structure of the second level maze and added a transition dialogue between the two rooms (different from the intro dialogue)

## 2026-03-06 - Camera follow update

- Implemented drawn maze components shifting based on player's position to be able to see parts of large mazes that are initially offscreen
- Fixed a bug where the maze player was able to slide into a wall when its center was between tiles
- Made maze player's speed dependent on their size
- Moved player position updating from `handle_input` to a new function
- Added **FPS info** to the main display
- Changed screen width and height, as well as maze player and tile sizes

## 2026-03-05 - Smooth walking update

- Reimplemented **held button processing** in form of a `handle_hold_input` function for playstates
- Revamped maze player position system, it is now based on screen pixels rather than maze structure coordinates
- Made the maze player "slide" through the maze when holding buttons
- Made player size different from tile size
- Dialogues now stop playing output animation and show the text entirely when pressing Esc
- The main game loop now terminates when closing the window rather than pressing Esc

## 2026-03-04 - Multiple levels update

- Creating multiple levels with different skins is now possible
- `StoryScript` now takes note of the levels already completed
- `MazeState` now has a `set_level()` method, as well as a `current_level` attribute, which take note of the current level and change the set of tiles needed for it
- Each maze sprite function in `AssetCreation.py` now has a level parameter to load level skins
- Directory changes: `assets/tiles` -> `assets/tiles/level_[1,2,3...]`

## 2026-03-03 - True story update

- Created `StoryScript.py` for defining how the story should go, in what order states are switched and how special actions are processed
- Added a main loop command for checking the script to make player inputs change how the story goes
- Made overridden `BaseState` functions able to send bunches of game loop commands instead of just one 
- Moved StateType enum to `Util.py`
- Removed `running` from game loop in favor of `Main.running`
- Slightly reorganized `Util.py`
- Added docstrings and todos to some modules
- Completely removed maze resetting and commented out win message code
- Made **CHANGELOG** and **README** look prettier and updated some of their info

## 2026-02-27

- Implemented choice and input saving to the `Dialogue` class (preformed in `DialogueState`)
- Changed slashes to backslashes in `AssetsCreation.py` paths

## 2026-02-25

- Reorganized `AssetsCreation.py` to reduce code duplication

## 2026-02-23 - Interactive dialogue update

- Implemented **choice buttons** and **input field** for dialogues (choice and input saving is on the way)
- Implemented **mouse event handling** in `Main.py` and playstates
- Optimized pressed key checks, now they activate on corresponding game events and not everytime
- Temporarily made the maze character only move on key presses and not holds (as a result of the previous change)
- Set FPS to stable 60 to prevent button lightening lag and reduce wait time between maze character movements
- Made keypad and mouse handling functions able to send commands to the main game loop, just like execute functions

## 2026-02-22 - Poly-logue update

- Implemented **dialogue** drawing and by-letter text outputting (inputting is on the way), as well as proper dialogue initiation
- Added placeholder dialogue sprites for reference and implemented loading them through `AssetsCreation.py`
- Renamed `StateTemplate.py` to `BaseState.py` and made all other playstates inherit from `BaseState`
- Implemented **playstate polymorphism**: now `Main` calls generic playstate functions without checking for the playstate type
- Added **execute functions**: playstates can now send commands to the main game loop (such as `STOP`, `WAIT` and `SET_FPS`) at different moments of an iteration
- Created this **CHANGELOG**

## 2026-02-21 - Wall drawing update

- Overhauled the way walls are created and the conditions for different wall types
- Added wall connections for some eye candy
- Moved transforming with cache to `AssetsLoading.py` (now `AssetsCreation.py`) as a special class
- Removed some unnecessary and duplicating code

## 2026-02-20 - Initial commit

- Split the code across many different modules (level building, playstates and the rest)
- Made input handling and assets drawing multimodular through generic playstate function calls in `Main`
- Optimized the code and removed unnecessary functions
- Created `Util.py` for storing shared vars and enums
- Tweaked maze setup
- Disabled maze restart after completion
- Created **README**
