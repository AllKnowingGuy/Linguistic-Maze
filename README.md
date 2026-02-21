# HOW TO WORK WITH THE FILES

## Assets folder

Basically put all assets you need in the folder, but please separate assets that are used for different levels and/or different playstates!

If you want to put existing assets in a different folder, do it ONLY through Right click - Refactor in PyCharm so that all filepaths in modules are updated.

## Source folder

- Main.py is what you should run to launch the game. It runs the Pygame window and updates and uses imported playstates to play different game scenaros.
- AssetsCreation.py handles loading and transforming assets and adding them to Pygame. Playstates use sprites created in this module to make visuals for the game.
- Util.py keeps objects shared by many different modules, such as wall type enum.
- LevelBuilding folder keeps backend modules such as maze and dialogue framework which contain structure data for these things.
- Playstates folder keeps playstates, or game modes (maze, dialogue, challenge, etc.). These playstates have their own methods for displaying things on the screen and handling inputs. An example state can be found in this folder for reference.
