# HOW TO WORK WITH THE FILES

## Assets folder

Basically put all assets you need in the folder, but please separate assets that are used for different levels and/or different playstates!

If you want to put existing assets in a different folder, do it ONLY through Right click - Refactor in PyCharm so that all filepaths in modules are updated.

And don't forget to implement sprites loading in AssetsCreation.py! You can use load_dialogue_box as a fine example.

## Source folder

- Main.py is what you should run to launch the game. It runs and updates the Pygame window and uses imported playstates to play different game scenarios. Playstate polymorphism allows getting current playstate functions without checking for the playstate type.
- AssetsCreation.py handles loading and transforming assets and adding them to Pygame. It caches transformed assets to reduce memory usage. Playstates use sprites created in AssetsCreation.py to make visuals for the game.
- Util.py keeps objects and values shared by many different modules, such as command enum and window size.
- LevelBuilding folder keeps backend modules such as maze and dialogue frameworks. They just contain structure data and DO NOT handle any sprite work!
- Playstates folder keeps playstates, or game modes (maze, dialogue, challenge, etc.). These playstates have their own methods for displaying things on the screen and handling inputs. They all inherit BaseState from BaseState.py.
