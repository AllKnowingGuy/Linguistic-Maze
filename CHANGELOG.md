# Changelog

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
