import json
from pathlib import Path


class Dialogue:
    dialogue_dict: dict[str, ...]

    lines: list[dict[str, ...]]  # damn - Vsevolod
    left_character: str | None
    right_character: str | None
    right_character_path: str | None
    starts_challenge: bool

    respect_checks: list[int] | None
    respect_jumps: list[int] | None

    saved_inputs: dict[int, str | None]
    saved_choices: dict[int, str | None]

    def __init__(self, path_or_dict: Path | dict[str, ...]):
        # Переменные конкретного диалога
        self._read_and_fill(path_or_dict)
        self.saved_inputs = {}
        self.saved_choices = {}
        self.collected_respect_points = {}

    def _read_and_fill(self, path_or_dict: Path | dict[str, ...]):
        if type(path_or_dict) is Path:
            with open(path_or_dict, 'r', encoding='utf-8') as f:
                dialogue_dict: dict = json.load(f)
        elif type(path_or_dict) is dict:
            dialogue_dict = path_or_dict
        else:
            raise ValueError(f'The argument must be Path or dict, not {type(path_or_dict)}')

        # Список сложно устроенных диалоговых строчек
        self.lines = dialogue_dict['lines']

        # Метаданные диалога
        self.left_character = dialogue_dict.get("left", "")
        self.right_character = dialogue_dict.get("right", "")
        self.right_character_path = dialogue_dict.get("rightsprite")

        self.ominous = dialogue_dict.get("ominous", False)
        self.music_path = dialogue_dict.get("music")
        self.starts_challenge = dialogue_dict.get("challenge", False)
        self.respect_checks = dialogue_dict.get("challengerpoints")
        self.respect_jumps = dialogue_dict.get("challengejumps")

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

    def get_line_text(self, line_ind: int) -> list[str] | None:
        if line_ind >= len(self.lines):
            return None
        return self.lines[line_ind]["text"].split("\n")

    def get_line_bgswitch(self, line_ind: int) -> str | None:
        if line_ind >= len(self.lines):
            return None
        return self.lines[line_ind].get("bg")

    def get_line_musicswitch(self, line_ind: int) -> str | None:
        if line_ind >= len(self.lines):
            return None
        return self.lines[line_ind].get("music")

    def get_line_jump(self, line_ind: int) -> int | None:
        if line_ind >= len(self.lines):
            return None
        return self.lines[line_ind].get("jump")

    def get_line_respect_points(self, line_ind: int) -> int:
        if line_ind >= len(self.lines):
            return 0
        return self.lines[line_ind].get("rpoints", 0)

    def record_collected_respect_points(self, line_ind: int):
        self.collected_respect_points[line_ind] = True

    def get_line_artifact(self, line_ind: int) -> str | None:
        if line_ind >= len(self.lines):
            return None
        return self.lines[line_ind].get("artifact")

    def get_line_challenge_cancel(self, line_ind: int) -> bool:
        if line_ind >= len(self.lines):
            return False
        return self.lines[line_ind].get("cancelchallenge", False)

    def get_line_room_switch(self, line_ind: int) -> bool:
        if line_ind >= len(self.lines):
            return False
        return self.lines[line_ind].get("nextroom", False)

    def get_line_room_restart(self, line_ind: int) -> bool:
        if line_ind >= len(self.lines):
            return False
        return self.lines[line_ind].get("restartroom", False)

    def get_line_gameover(self, line_ind: int) -> bool:
        if line_ind >= len(self.lines):
            return False
        return self.lines[line_ind].get("gameover", False)
