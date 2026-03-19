"""
current JSON format:
{
    "left": CHARNAME1, # This is displayed in-game. Use "Протагонист" (will show current protag's name) or null
    "right": CHARNAME2, # This is displayed in-game. Use monster's name in Russian or null
    "rightsprite" FILEPATH, # The path to the monster's sprite from "monsters" folder, such as "level_1/monster.png"
    "lines": [
        {
            "speaker": SPEAKER, # "left" or "right". You can omit this key for no character
            "action": {
                "type": ACTIONTYPE, # "savetyped" or "choosefrom". You can omit this key for no action
                "options": [ # This key only and always exists when the action is "choosefrom"
                    OPTIONTEXT1,
                    OPTIONTEXT2,
                    ...and so on
                ],
                "jumps": [ # This key may not exist, but if it does, its length should be the length of "options"
                    LINEINDEX1, # Index -> jump to the line after pressing the button;
                                null -> just move on;
                                -1 -> end the dialogue
                    LINEINDEX2,
                    ...and so on
                ]
            }, # Put null as a value instead of this dict for no action
            "text": TEXT,
            "jump": LINEINDEX, # To show LINEINDEX line next; -1 -> end the dialogue here; omit to move on normally
            "bg": FILEPATH # The path from "backgrounds" folder, or "PREVSCREEN" (screenshot BG); omit to not change BG
        },
        ...and so on
    ]
}
"""

import json


class Dialogue:
    lines: list[dict[str, ...]]  # damn - Vsevolod
    left_character: str | None
    right_character: str | None
    right_character_path: str | None
    starts_challenge: bool

    saved_inputs: dict[str, str | None]
    saved_choices: dict[str, str | None]

    def __init__(self, path: str):
        # Переменные конкретного диалога
        self._read_and_fill(path)
        self.saved_inputs = {}
        self.saved_choices = {}

    def _read_and_fill(self, path: str):
        with open(path, 'r', encoding='utf-8') as f:
            dialogue_dict: dict = json.load(f)

        # Список сложно устроенных диалоговых строчек
        self.lines = dialogue_dict['lines']

        # Метаданные диалога
        self.left_character = dialogue_dict.get("left")
        self.right_character = dialogue_dict.get("right")
        self.right_character_path = dialogue_dict.get("rightsprite")
        self.respect_points = dialogue_dict.get("rpoints", 0)  # TODO: line respect points when awaiting input or choice

        self.ominous = dialogue_dict.get("ominous", False)
        self.music_path = dialogue_dict.get("music")
        self.starts_challenge = dialogue_dict.get("challenge", False)

    def get_line_speaker(self, line_ind: int) -> str | None:
        if line_ind >= len(self.lines):
            return None
        return self.lines[line_ind].get("speaker")

    def get_line_action_type(self, line_ind: int) -> str | None:
        if line_ind >= len(self.lines):
            return None
        supposed_action = self.lines[line_ind].get("action")
        if type(supposed_action) == dict:
            return supposed_action["type"]
        return None

    def get_line_choose_options(self, line_ind: int) -> list[str] | None:
        if line_ind >= len(self.lines):
            return None
        supposed_action = self.lines[line_ind].get("action")
        if type(supposed_action) == dict and supposed_action["type"] == "choosefrom":
            return supposed_action["options"]
        return None

    def get_line_choose_jumps(self, line_ind: int) -> list[int | None] | None:
        if line_ind >= len(self.lines):
            return None
        supposed_action = self.lines[line_ind].get("action")
        if type(supposed_action) == dict and supposed_action["type"] == "choosefrom":
            return supposed_action.get("jumps", [])
        return None

    def get_line_text(self, line_ind: int) -> str | None:
        if line_ind >= len(self.lines):
            return None
        return self.lines[line_ind]["text"]

    def get_line_bgswitch(self, line_ind: int) -> str | None:
        if line_ind >= len(self.lines):
            return None
        return self.lines[line_ind].get("bg")

    def get_line_jump(self, line_ind: int) -> int | None:
        if line_ind >= len(self.lines):
            return None
        return self.lines[line_ind].get("jump")
