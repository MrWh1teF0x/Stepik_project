from dataclasses import dataclass, field
from abc import ABC, abstractmethod


@dataclass
class TypeStep(ABC):
    title: str
    text: str
    cost: int = 0
    lesson_id: int = None
    position: int = None
    id: int = None

    @abstractmethod
    def body(self) -> dict:
        pass


@dataclass
class StepText(TypeStep):

    def body(self) -> dict:
        return {
            "stepSource": {
                "block": {
                    "name": "text",
                    "text": self.text,
                },
                "lesson_id": self.id,
                "position": self.position,
                "cost": self.cost,
            }
        }


@dataclass
class StepString(TypeStep):
    code: str = ""

    def body(self) -> dict:
        return {
            "stepSource": {
                "block": {
                    "name": "string",
                    "text": self.text,
                    "source": {
                        "code": self.code,
                    },
                },
                "lesson_id": self.id,
                "position": self.position,
                "cost": self.cost,
            }
        }


@dataclass
class StepNumber(TypeStep):
    answer: float = None
    max_error: float = 0

    def body(self) -> dict:
        return {
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
                "position": self.position,
                "cost": self.cost,
            }
        }


@dataclass
class StepQuiz(TypeStep):
    answers: list[tuple[str, bool]] = field(default_factory=list)

    def body(self) -> dict:
        return {
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
                "position": self.position,
                "cost": self.cost,
            }
        }


@dataclass
class StepTask(TypeStep):
    code: str = ""
    test_cases: list[str] = field(default_factory=list)

    def body(self) -> dict:
        return {
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
                "position": self.position,
                "cost": self.cost,
            }
        }
