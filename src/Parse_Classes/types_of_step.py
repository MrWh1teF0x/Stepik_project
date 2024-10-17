import src.PyParseFormats as PPF
from dataclasses import dataclass, field
from abc import ABC, abstractmethod


@dataclass
class TypeStep(ABC):
    title: str
    text: str
    json_data: dict = field(default_factory=dict)
    cost: int = 0
    lesson_id: int = -1
    id: int = -1

    @abstractmethod
    def parse(self, markdown: list[str]) -> None:
        pass

    @abstractmethod
    def body(self):
        pass


@dataclass
class StepText(TypeStep):

    def __post_init__(self):
        self.json_data = {
            "stepSource": {
                "block": {
                    "name": "text",
                    "text": self.text,
                },
                "lesson_id": self.id,
                "cost": self.cost,
            }
        }

    def parse(self, markdown: list[str]) -> None:
        pass

    def body(self):
        pass


@dataclass
class StepString(TypeStep):
    code: str = ""

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
                "lesson_id": self.id,
                "cost": self.cost,
            }
        }

    def parse(self, markdown: list[str]) -> None:
        pass

    def body(self):
        pass


@dataclass
class StepNumber(TypeStep):
    answer: float = None
    max_error: float = 0

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
                "lesson_id": self.id,
                "cost": self.cost,
            }
        }

    def parse(self, markdown: list[str]) -> None:
        pass

    def body(self):
        pass


@dataclass
class StepQuiz(TypeStep):
    answers: list[tuple[str, bool]] = field(default_factory=list)

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
                },
                "lesson_id": self.id,
                "cost": self.cost,
            }
        }

    def parse(self, markdown: list[str]) -> None:
        pass

    def body(self):
        pass


@dataclass
class StepTask(TypeStep):
    code: str = ""
    test_cases: list[str] = field(default_factory=list)

    def __post_init__(self):
        self.json_data = {
            {
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
                    "lesson_id": self.id,
                    "cost": self.cost,
                }
            }
        }

    def parse(self, markdown: list[str]) -> None:
        pass

    def body(self):
        pass
