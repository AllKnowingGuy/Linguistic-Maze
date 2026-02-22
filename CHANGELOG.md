# Changelog

## 2026-02-22 - Poly-logue update

- Implemented dialogue drawing and by-letter text outputting (inputting is on the way), as well as proper dialogue initiation
- Added placeholder dialogue sprites for reference and implemented loading them through AssetsCreation.py
- Renamed StateTemplate.py to BaseState.py and made all other playstates inherit from it
- Implemented playstate polymorphism: now Main.py calls generic playstate functions without checking for the playstate type
- Added execute functions: playstates can now send commands to the main game loop (such as stop, wait and change fps) at different moments of the iteration
- Created this CHANGELOG

## 2026-02-21 - Wall drawing update

- Overhauled the way walls are created and the conditions for different wall types
- Added wall connections for some eye candy
- Moved transforming with cache to AssetsLoading.py (now AssetsCreation.py) as a special class
- Removed some unnecessary and duplicating code

## 2026-02-20 - Initial commit

- Split the code across many different modules (level building, playstates and the rest)
- Made input handling and assets drawing multimodular through generic playstate function calls in Main
- Optimized the code and removed unnecessary functions
- Created Util.py for storing shared vars and enums
- Tweaked maze setup
- Disabled maze restart after completion
- Created README
