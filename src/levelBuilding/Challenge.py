import json
from transformers import pipeline


class Challenge:
    windows: list[dict[str, ...]]
    answers: dict[int, str]

    def __init__(self, path: str):
        self._read_and_fill(path)
        self._rubert_model = pipeline(
            "text-classification",
            model="seara/rubert-base-cased-russian-sentiment"
        )

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

    #в сюжете есть монстры, которых можно пропустить, показав артефакт (например, дудку)

    def can_skip_with_artifact(self, window_ind: int, artifacts: list[str]) -> bool:
        """Проверяет, можно ли пропустить задание, имея нужный артефакт."""
        action = self.windows[window_ind].get("action", {})
        required = action.get("requires_artifact")
        if required and required in artifacts:
            return True
        return False

    def check_choice(self, window_ind: int, choice_index: int) -> tuple[bool, int, str | None]:
        """Проверяет выбор варианта.
        Возвращает (правильно, изменение респекта, название артефакта (если есть)).
        """

        action = self.windows[window_ind].get("action", {})
        if action.get("type") != "choosefrom":
            raise ValueError("Not a choosefrom window")

        options = action.get("options", [])
        if choice_index < 0 or choice_index >= len(options):
            return False, 0, None

        answers = action.get("answers", [])
        correct = options[choice_index] in answers
        delta = action.get("correctrpoints" if correct else "incorrectrpoints", 0)
        artifact = action.get("artifact") if correct else None
        return correct, delta, artifact

    def check_current_answer(self, window_ind: int):
        """Проверка текущего ответа на правильность методом, назначенным на это задание"""

        user_input = self.answers[window_ind]
        keys = self.get_window_correct_answers(window_ind)
        supposed_action = self.windows[window_ind].get("action", {})
        checker = self.get_window_answers_checker(window_ind)
        if checker:
            if checker == 'plainequality':
                return user_input.strip() in keys  # самый простой способ проверки
            elif checker == 'ling_terms':
                import re
                pattern = r'(лингвист|язык|лингв|термин|фонет|социо|нейро)'
                return bool(re.search(pattern, user_input, re.IGNORECASE))
            elif checker == 'wordmatch':
                import re
                patterns = supposed_action.get("patterns", [])
                return any(re.search(p, user_input, re.IGNORECASE) for p in patterns)
            elif checker == 'sentiment_rubert':
                try:
                    result = self._rubert_model(user_input)[0]
                    positive_score = float(result['score'])
                    threshold = supposed_action.get("threshold", 0.6)
                    return positive_score > threshold
                except Exception as e:
                    print(f"Ошибка в sentiment_rubert: {e}")
                    return any(w in user_input.lower() for w in ['хорошо', 'помощь'])
            else:
                raise ValueError(f'This checker cannot be recognized: {checker}')
        else:
            return user_input.strip() in keys  # если проверщик не указан, то проверяем как plainequality
