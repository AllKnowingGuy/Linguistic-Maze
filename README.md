# HOW TO WORK WITH THE FILES

## Assets folder

Basically put all assets you need in the folder, but please be reasonable and separate assets that are used for different levels and/or different playstates!

If you want to put existing assets in a different folder, do it ONLY through **Right click - Refactor** in PyCharm so that all file paths in modules are updated. And even still check the paths carefully in playstates, `AssetsCreation.py` and `StoryScript.py`!

And don't forget to implement image loading in `AssetsCreation.py`! You can use `add_right_speak_sprite` as a fine example. Then create an attribute in `__init__` function of your desired playstate to save the loaded sprite for further usage.

The best current example of how a dialogue file can be structured is `assets/data/dialogues/intro.json`. For challenges, refer to `assets/data/challenges/level_0/enemy_at_exit.json`.

## Source folder

- `Main.py` is what you should run to launch the game. It runs and updates the Pygame window and uses imported playstates to play different game modes. Playstate polymorphism allows calling current playstate functions without checking for the playstate type.
- `Util.py` keeps values, classes and functions used by many different modules, such as command enum and window size constants.
- `AssetsCreation.py` handles loading and transforming assets and adding them to Pygame. It caches transformed assets to reduce memory usage. Playstates use images created in `AssetsCreation.py` to make visuals for the game.
- `LevelBuilding` folder keeps backend modules such as maze and dialogue frameworks or structures of recurring objects like enemies and buttons. These modules just contain structure data and DO NOT handle any sprite work!
- `Playstates` folder keeps playstates, or game modes (maze, dialogue, challenge, etc.). These playstates have their own methods for displaying things on the screen and handling player inputs. They all inherit `BaseState` from `BaseState.py`.
- `StoryScript.py` handles state switching and checks player choices in the game. Playstates make `Main.py` check the script by passing a special command after handling inputs or drawing.
- `Config.py` handles saved game configuration reading and rewriting. Playstates that aren't meant to save data don't need to keep an attribute for `Config` class instance, as they use it only once for binds fields filling.

# GAME TESTING

## Controls

- In the maze, press arrow keys or WASD to move. That's it!
- In the dialogue, press Enter to advance, click on choice buttons with the mouse, and input text with the keyboard when there's an input field. You won't advance if the input field is empty!
- In the challenge, you can click on choice buttons and input text just like in the dialogue, but to move between questions, click on navigation buttons with the mouse. Once you've pressed a choice button in each set and filled every input field, you can submit the answers and see a nice verdict animation!
- If you see a text printing animation anywhere, you can press Esc to make it stop!
- And the best part is that most of these controls can be rebound in `config.json`! Currently you can only bind actions to buttons that have a character (letter, number or other typeable thing) associated with them, so you cannot bind to Shift or Ctrl. But Esc, Backspace, Delete and Enter work fine! You will need to retrieve the unicode of these buttons (for example, by printing `ord(event.unicode)` in `handle_input`) and enter it as a 4-digit number (add zeros to the left if the unicode is shorter than 4 digits!)

## Useful flags

- `DEBUG_DIALOGUE_SKIP` in `StoryScript.py`: when True, all generic dialogues play their first line and then finish. Scripted dialogues need to make use of this flag individually, especially if the choices made in them can affect the next state or even cause a gameover.
- `MazeState.darkness_enabled` in `MazeState.py`: when False, the maze's darkness effect is disabled. This is useful to see how the maze looks with the current skin.
- `move_by` in `MazeState.handle_input` in `MazeState.py`: controls the player's speed.
