import json
from typing import Generator


def extract_or_cast_unicode(bind: str):
    if len(bind) == 1:
        return ord(bind)
    elif len(bind) == 4:
        return int(bind)
    else:
        raise ValueError(f'String {bind} is not a single character or a 4-digit Unicode code.')


class Config:
    def __init__(self):
        with open('..\\config.json', 'r', encoding='utf-8') as f:
            self.config_dict: dict = json.load(f)

    def get_maze_controls(self) -> Generator[int]:
        for control in ('move_up', 'move_down', 'move_left', 'move_right'):
            yield extract_or_cast_unicode(self.config_dict['controls'][control])

    def get_dialogue_controls(self):
        return (extract_or_cast_unicode(self.config_dict['controls']['end_text_animation']),
                extract_or_cast_unicode(self.config_dict['controls']['no_task_advance']))

    def get_challenge_controls(self):
        return extract_or_cast_unicode(self.config_dict['controls']['end_text_animation'])
