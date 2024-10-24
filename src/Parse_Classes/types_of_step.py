from dataclasses import dataclass, field
from abc import ABC, abstractmethod


@dataclass
class TypeStep(ABC):
    title: str = ""
    text: str = ""
    cost: int = 0
    lesson_id: int = None
    position: int = None

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
                "lesson": self.lesson_id,
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
                "lesson": self.lesson_id,
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
                "lesson": self.lesson_id,
                "position": self.position,
                "cost": self.cost,
            }
        }


@dataclass
class QuizAnswer:
    text: str
    is_correct: bool


@dataclass
class StepQuiz(TypeStep):

    answers: list[QuizAnswer] = field(default_factory=list)

    def body(self) -> dict:
        return {
            "stepSource": {
                "block": {
                    "name": "choice",
                    "text": self.text,
                    "source": {
                        "options": [
                            {
                                "is_correct": answer.is_correct,
                                "text": answer.text,
                                "feedback": "",
                            }
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
                "lesson": self.lesson_id,
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
                "lesson": self.lesson_id,
                "position": self.position,
                "cost": self.cost,
            }
        }
