import json
from typing import Generator

from src.util import resource_path


def extract_decimal_code(bind: str) -> int:
    if len(bind) == 1:
        return ord(bind)
    elif len(bind) == 4:
        return int(bind, 16)
    else:
        raise ValueError(
            f"String {bind} is not a single character or a 4-digit hexadecimal Unicode code."
        )


def extract_character(bind: str) -> str:
    if len(bind) == 1:
        return bind
    elif len(bind) == 4:
        return chr(int(bind, 16))
    else:
        raise ValueError(
            f"String {bind} is not a single character or a 4-digit hexadecimal Unicode code."
        )


def revert_to_unicode(bind: str) -> str:
    if len(bind) == 1:
        hex_uni = hex(ord(bind))[2:]
        return "0" * (4 - len(hex_uni)) + hex_uni
    elif len(bind) == 4 and all([char in "0123456789aAbBcCdDeEfF" for char in bind]):
        return bind
    else:
        raise ValueError(
            f"String {bind} is not a single character or a 4-digit hexadecimal Unicode code."
        )


class Config:
    def __init__(self):
        with open(resource_path("config.json"), "r", encoding="utf-8") as f:
            self.config_dict: dict = json.load(f)

    def get_all_controls(self) -> dict[str, str]:
        return dict(
            zip(
                self.config_dict["controls"].keys(),
                [
                    extract_character(control)
                    for control in self.config_dict["controls"].values()
                ],
            )
        )

    def get_sound_controls(self) -> tuple[int, int]:
        return (
            extract_decimal_code(self.config_dict["controls"]["increase_volume"]),
            extract_decimal_code(self.config_dict["controls"]["decrease_volume"]),
        )

    def get_maze_controls(self) -> Generator[int]:
        for control in ("move_up", "move_down", "move_left", "move_right"):
            yield extract_decimal_code(self.config_dict["controls"][control])

    def get_dialogue_controls(self) -> tuple[int, int]:
        return (
            extract_decimal_code(self.config_dict["controls"]["end_text_animation"]),
            extract_decimal_code(self.config_dict["controls"]["no_task_advance"]),
        )

    def get_challenge_controls(self) -> int:
        return extract_decimal_code(self.config_dict["controls"]["end_text_animation"])

    def set_controls(self, controls: dict[str, str]):
        if all(
            [
                bind in controls
                for bind in (
                    "move_up",
                    "move_down",
                    "move_left",
                    "move_right",
                    "end_text_animation",
                    "no_task_advance",
                    "increase_volume",
                    "decrease_volume",
                )
            ]
        ):
            self.config_dict["controls"] = dict(
                zip(
                    controls.keys(),
                    [revert_to_unicode(control) for control in controls.values()],
                )
            )
            self.update_config_json()

    def update_config_json(self):
        with open(resource_path("config.json"), "w", encoding="utf-8") as f:
            json.dump(self.config_dict, f, indent=4)
