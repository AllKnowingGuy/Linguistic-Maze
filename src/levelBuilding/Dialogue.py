from typing import Any


class Dialogue:
    text: list[str]
    character: str
    starts_challenge: str | None
    choice_dict: dict[str, Any]

    def __init__(self, text: list[str], character: str, starts_challenge: str = None) -> None:
        # Переменные конкретного диалога
        self.text = text
        self.character = character
        self.starts_challenge = starts_challenge
        self.choice_dict = {}



dialogue_text = """left\tnoaction\tЯ студент и я умею говорить!
right\tnoaction\tА я монстр, но я пока не знаю, как меня зовут.
left\tnoaction\tЗато я знаю, сейчас скажу)
nochar\tsavetyped\tА как зовут монстра? Напишите ответ: 
nochar\tchoosefrom{Да, Нет}\tВы уверены, что это правда?"""

dialogue = Dialogue(dialogue_text.split('\n'), 'Говорящий монстр')
