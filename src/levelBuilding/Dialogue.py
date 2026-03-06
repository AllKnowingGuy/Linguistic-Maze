# current line format: CHAR\tACTION\tTEXT\tCHANGEBGTO
# NO EMPTY LINES!


class Dialogue:
    lines: list[tuple[str, ...]] # damn
    character: str
    starts_challenge: str | None
    saved_inputs: dict[str, str | None]
    saved_choices: dict[str, str | None]

    def __init__(self, lines: list[str], character: str, starts_challenge: str = None):
        # Переменные конкретного диалога
        self.lines = []
        self._sep_text_from_meta(lines)
        self.character = character
        self.starts_challenge = starts_challenge
        self.saved_inputs = {}
        self.saved_choices = {}

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

    def get_line_bgswitch(self, line_ind: int):
        if line_ind >= len(self.lines):
            return None
        return self.lines[line_ind][3] if len(self.lines[line_ind]) > 3 else None
