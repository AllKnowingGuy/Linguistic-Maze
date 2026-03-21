# Changelog

## 2026-03-21 - Test update 2
- Implemented pytest and workflow for `MazeState.py` and `ChallengeState.py`

## 2026-03-20 - Test update 1 (as in, the update that adds tests)
- Implemented pytest for `AssetsCreation.py`
- Fixed a date error in `CHANGELOG.md`
- Added workflows

## 2026-03-15 - Déjà vu update

- Created `MenuState.py` for the main menu; as of now it has a start button and keybind buttons, one for each keybind
- Implemented key binding **in game** through main menu buttons
- Rebound text animation ending fron Esc to Enter
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
