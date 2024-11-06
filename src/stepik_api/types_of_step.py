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
class QuizAnswer:
    text: str
    is_correct: bool


@dataclass
class StepQuiz(TypeStep):
    answers: list[QuizAnswer] = field(default_factory=list)
    is_multiple_choice: bool = False

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
                        "is_multiple_choice": self.is_multiple_choice,
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
class StepString(TypeStep):
    answer: str = None
    match_substring: bool = False
    case_sensitive: bool = False

    def body(self) -> dict:
        return {
            "stepSource": {
                "block": {
                    "name": "string",
                    "text": self.text,
                    "source": {
                        "pattern": self.answer,
                        "use_re": False,
                        "match_substring": self.match_substring,
                        "case_sensitive": self.case_sensitive,
                        "code": "",
                        "is_file_disabled": True,
                    },
                },
                "lesson": self.lesson_id,
                "position": self.position,
                "cost": self.cost,
            }
        }


@dataclass
class TaskTest:
    input: str = ""
    output: str = ""


@dataclass
class StepTask(TypeStep):
    samples_count: int = 1
    execution_time_limit: int = 5
    execution_memory_limit: int = 256
    test_cases: list[TaskTest] = field(default_factory=list)

    def body(self) -> dict:
        return {
            "stepSource": {
                "block": {
                    "name": "code",
                    "text": self.text,
                    "source": {
                        "code": "def generate():\n    return []\n\ndef check(reply, clue):\n    return reply.strip() == clue.strip()\n",
                        "samples_count": self.samples_count,
                        "execution_time_limit": self.execution_time_limit,
                        "execution_memory_limit": self.execution_memory_limit,
                        "templates_data": "",
                        "is_time_limit_scaled": True,
                        "is_memory_limit_scaled": True,
                        "is_run_user_code_allowed": True,
                        "manual_time_limits": [],
                        "manual_memory_limits": [],
                        "test_archive": [],
                        "test_cases": [
                            [test.input, test.output] for test in self.test_cases
                        ],
                    },
                },
                "lesson": self.lesson_id,
                "position": self.position,
                "cost": self.cost,
            }
        }


@dataclass
class StepSorting(TypeStep):
    sorted_answers: list[str] = field(default_factory=list)

    def body(self) -> dict:
        return {
            "stepSource": {
                "lesson": self.lesson_id,
                "position": self.position,
                "block": {
                    "name": "sorting",
                    "text": self.text,
                    "source": {
                        "options": [{"text": answer} for answer in self.sorted_answers]
                    },
                },
                "cost": self.cost,
            }
        }


@dataclass
class MatchingPair:
    first: str
    second: str


@dataclass
class StepMatching(TypeStep):
    preserve_firsts_order: bool = True
    pairs: list[MatchingPair] = field(default_factory=list)

    def body(self) -> dict:
        return {
            "stepSource": {
                "lesson": self.lesson_id,
                "position": self.position,
                "block": {
                    "name": "matching",
                    "text": self.text,
                    "source": {
                        "preserve_firsts_order": self.preserve_firsts_order,
                        "pairs": [
                            {"first": pair.first, "second": pair.second}
                            for pair in self.pairs
                        ],
                    },
                },
                "cost": self.cost,
            }
        }
