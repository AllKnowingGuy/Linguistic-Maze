import re
from pathlib import Path

from httpx import ConnectError
from mawo_pymorphy3 import create_analyzer
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline

from src.util import resource_path

EXISTING_WORDS_ANALYZER_PATH = resource_path(
    Path("assets\\models\\existing_words_analysis\\dicts_ru")
)

RUBERT_MODEL = "seara/rubert-base-cased-russian-sentiment"
LOCAL_ROBERT_MODEL_PATH = resource_path(
    Path("assets\\models\\sentiment_analysis\\rubert_sentiment_model")
)


def _load_tf_model(model_name: str, offline_path: str):
    try:
        model = AutoModelForSequenceClassification.from_pretrained(model_name)
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model.save_pretrained(offline_path)
        tokenizer.save_pretrained(offline_path)
        print("Модель Transformers загружена и сохранена локально!")
        return True
    except ConnectError:
        print("Ошибка загрузки модели Transformers: нет подключения к интернету")
        return False


class Checker:
    """Проверщик ответов, используемый в диалогах и испытаниях"""

    def __init__(self):
        self.existing_words_analyzer = create_analyzer(EXISTING_WORDS_ANALYZER_PATH)
        self._setup_tf_pipeline(
            RUBERT_MODEL,
            LOCAL_ROBERT_MODEL_PATH,
            saved=LOCAL_ROBERT_MODEL_PATH.exists(),
        )

    def _setup_tf_pipeline(
        self, model_name: str, offline_path: str, saved: bool = False
    ):
        if not saved:
            if not _load_tf_model(model_name, offline_path):
                self.tf_pipeline = None
                return
        else:
            print("Используется загруженная модель Transformers!")
        new_pipeline = pipeline(
            "text-classification", model=str(offline_path).replace("\\", "/")
        )
        self.tf_pipeline = new_pipeline

    def check(
        self,
        answer: str,
        keys: list[str] | tuple[str] = (),
        checker: str = "plainequality",
    ):
        if not checker in (
            "plainequality",
            "rematch",
            "sentiment_rubert",
            "existing_words",
        ):
            # если проверщик некорректный, то проверяем как plainequality
            print("Проверщик не распознан")
            return answer.strip().lower() in keys

        if checker == "plainequality":
            return answer.strip().lower() in keys  # самый простой способ проверки

        elif checker == "rematch":
            return any(re.search(pat, answer, re.IGNORECASE) for pat in keys)

        elif checker == "sentiment_rubert":
            try:
                result = self.tf_pipeline(answer)[0]
                positive_score = float(result["score"])
                threshold = 0.6
                if not 0 <= threshold <= 1:
                    raise ValueError(
                        f"Threshold must be between 0 and 1, got {threshold}"
                    )
                return positive_score > threshold
            except Exception as e:
                print(f"Ошибка в sentiment_rubert: {e}")
                return any(
                    w in answer.lower() for w in ("хорош", "помог", "помоч", "привет")
                )

        elif checker == "existing_words":
            punctuation = r"""[\.,:;\?!<>\(\)\[\]"'&~]"""
            text = re.sub(punctuation, "", answer).split()
            # TODO: probably make the check softer
            return all(
                [
                    1 in [form.score for form in self.existing_words_analyzer.parse(w)]
                    for w in text
                ]
            )

        else:
            raise ValueError(f"This checker cannot be recognized: {checker}")
