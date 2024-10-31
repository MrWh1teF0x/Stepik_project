from dataclasses import field, dataclass
import src.PyParseFormats as PPF
from abc import ABC, abstractmethod
import warnings


class TypeStep(ABC):
    json_data: dict = field(default_factory=dict)

    def __init__(self, markdown: list[str] | None = None):
        if markdown is not None:
            self.parse(markdown)

    @abstractmethod
    def parse(self, markdown: list[str]):
        pass

    @abstractmethod
    def build_body(self):
        self.json_data = {"block": {}}


class StepText(TypeStep):
    text: str = ""
    json_data: dict = field(default_factory=dict)

    def parse(self, markdown: list[str]) -> None:
        if not PPF.check_format(markdown[0], PPF.format_steptext):
            if not PPF.check_format(markdown[0], PPF.format_step_name[0]):
                raise SyntaxError(
                    "Step:Text was set or written incorrectly - Impossible ERROR"
                )

        self.text = "\n".join(markdown)

        self.build_body()

    def build_body(self) -> None:
        self.json_data = {
            "block": {
                "name": "text",
                "text": self.text,
            }
        }


class StepString(TypeStep):
    title: str = ""
    text: str = ""
    code: str = ""
    cost: int = 0
    json_data: dict = field(default_factory=dict)

    def __post_init__(self):
        self.json_data = {
            "stepSource": {
                "block": {
                    "name": "string",
                    "text": self.text,
                    "source": {
                        "code": self.code,
                    },
                },
                "cost": self.cost,
            }
        }

    def parse(self, markdown: list[str]) -> None:
        pass

    def body(self):
        pass


class StepNumber(TypeStep):
    title: str = ""
    text: str = ""
    answer: float = None
    max_error: float = None
    cost: int = 0
    json_data: dict = field(default_factory=dict)

    def __post_init__(self):
        self.json_data = {
            "stepSource": {
                "block": {
                    "name": "number",
                    "text": self.text,
                    "source": {
                        "options": [
                            {
                                "answer": str(self.answer),
                                "max_error": str(self.max_error),
                            }
                        ]
                    },
                },
                "cost": self.cost,
            }
        }

    def parse(self, markdown: list[str]) -> None:
        pass

    def body(self):
        pass


class StepQuiz(TypeStep):
    title: str = ""
    text: str = ""
    answers: list[tuple[str, bool]] = field(default_factory=list)
    cost: int = 0
    json_data: dict = field(default_factory=dict)

    def __post_init__(self):
        self.json_data = {
            "stepSource": {
                "block": {
                    "name": "choice",
                    "text": self.text,
                    "source": {
                        "options": [
                            {"is_correct": answer[1], "text": answer[0], "feedback": ""}
                            for answer in self.answers
                        ],
                        "is_always_correct": False,
                        "is_html_enabled": True,
                        "sample_size": len(self.answers),
                        "is_multiple_choice": False,
                        "preserve_order": False,
                        "is_options_feedback": False,
                    },
                }
            }
        }

    def parse(self, markdown: list[str]) -> None:
        pass

    def body(self):
        pass


class StepTask(TypeStep):
    title: str = ""
    text: str = ""
    code: str = ""
    test_cases: list[str] = field(default_factory=list)
    cost: int = 0
    json_data: dict = field(default_factory=dict)

    def __post_init__(self):
        self.json_data = {
            "stepSource": {
                "block": {
                    "name": "code",
                    "text": self.text,
                    "source": {
                        "code": self.code,
                        "samples_count": len(self.test_cases),
                        "test_cases": [self.test_cases],
                    },
                },
                "cost": self.cost,
            }
        }

    def parse(self, markdown: list[str]) -> None:
        pass

    def body(self):
        pass
