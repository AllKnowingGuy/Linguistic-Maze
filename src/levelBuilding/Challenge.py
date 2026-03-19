import json


class Challenge:
    windows: list[dict[str, ...]]
    answers: dict[int, str]

    def __init__(self, path: str):
        self._read_and_fill(path)

    def _read_and_fill(self, path: str):
        with open(path, 'r', encoding='utf-8') as f:
            challenge_dict: dict = json.load(f)

        self.windows = challenge_dict["windows"]
        # TODO: maybe add some metadata? like special music or background

    def get_window_title(self, window_ind: int) -> str | None:
        if window_ind >= len(self.windows) or window_ind < 0:
            return None
        return self.windows[window_ind].get("title")

    def get_window_task_text(self, window_ind: int) -> str | None:
        if window_ind >= len(self.windows) or window_ind < 0:
            return None
        return self.windows[window_ind].get("text", "")

    def get_window_image_path(self, window_ind: int) -> str | None:
        if window_ind >= len(self.windows) or window_ind < 0:
            return None
        return self.windows[window_ind].get("image")

    def get_window_action_type(self, window_ind: int) -> str | None:
        if window_ind >= len(self.windows) or window_ind < 0:
            return None
        supposed_action = self.windows[window_ind].get("action")
        if type(supposed_action) == dict:
            return supposed_action["type"]
        return None

    def get_window_choose_options(self, window_ind: int) -> list[str] | None:
        if window_ind >= len(self.windows) or window_ind < 0:
            return None
        supposed_action = self.windows[window_ind].get("action")
        if type(supposed_action) == dict and supposed_action["type"] == "choosefrom":
            return supposed_action["options"]
        return None

    def get_window_correct_answers(self, window_ind: int) -> list[str] | None:
        if window_ind >= len(self.windows) or window_ind < 0:
            return None
        supposed_action = self.windows[window_ind].get("action")
        if type(supposed_action) == dict:
            return supposed_action["answers"]
        return None

    def get_window_answers_checker(self, window_ind: int) -> str | None:
        if window_ind >= len(self.windows) or window_ind < 0:
            return None
        supposed_action = self.windows[window_ind].get("action")
        if type(supposed_action) == dict:
            return supposed_action.get("checker")
        return None

    def get_window_correct_tips(self, window_ind: int) -> list[str] | None:
        if window_ind >= len(self.windows) or window_ind < 0:
            return None
        supposed_action = self.windows[window_ind].get("action")
        if type(supposed_action) == dict:
            return supposed_action.get("correctcomments")
        return None

    def get_window_incorrect_tips(self, window_ind: int) -> list[str] | None:
        if window_ind >= len(self.windows) or window_ind < 0:
            return None
        supposed_action = self.windows[window_ind].get("action")
        if type(supposed_action) == dict:
            return supposed_action.get("incorrectcomments")
        return None

    def get_window_correct_respect_points(self, window_ind: int) -> int | None:
        if window_ind >= len(self.windows) or window_ind < 0:
            return None
        supposed_action = self.windows[window_ind].get("action")
        if type(supposed_action) == dict:
            return supposed_action.get("correctrpoints", 0)
        return None

    def get_window_incorrect_respect_points(self, window_ind: int) -> int | None:
        if window_ind >= len(self.windows) or window_ind < 0:
            return None
        supposed_action = self.windows[window_ind].get("action")
        if type(supposed_action) == dict:
            return supposed_action.get("incorrectrpoints", 0)
        return None

    def check_current_answer(self, window_ind: int):
        """Проверка текущего ответа на правильность методом, назначенным на это задание"""

        user_input = self.answers[window_ind]
        keys = self.get_window_correct_answers(window_ind)
        checker = self.get_window_answers_checker(window_ind)
        if checker:
            if checker == 'plainequality':
                return user_input.strip() in keys  # самый простой способ проверки
            # добавляйте других проверщиков через elif; возможно, потребуется написать для них отдельные функции
            else:
                raise ValueError(f'This checker cannot be recognized: {checker}')
        else:
            return user_input.strip() in keys  # если проверщик не указан, то проверяем как plainequality
