from typing import Any


class Dialogue:
    lines: list[tuple[str, ...]] # damn
    character: str
    starts_challenge: str | None
    choice_dict: dict[str, Any]

    def __init__(self, lines: list[str], character: str, starts_challenge: str = None):
        # Переменные конкретного диалога
        self.lines = []
        self._sep_text_from_meta(lines)
        self.character = character
        self.starts_challenge = starts_challenge
        self.choice_dict = {}

    def _sep_text_from_meta(self, lines: list[str]):
        for line in lines:
            self.lines.append(tuple(line.split('\t')))

    def get_line_speaker(self, line_ind: int):
        if line_ind >= len(self.lines):
            return None
        return self.lines[line_ind][0]

    def get_line_action(self, line_ind: int):
        if line_ind >= len(self.lines):
            return None
        return self.lines[line_ind][1]

    def get_line_text(self, line_ind: int):
        if line_ind >= len(self.lines):
            return None
        return self.lines[line_ind][2]
