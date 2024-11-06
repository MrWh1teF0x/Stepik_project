from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import Dict, List


@dataclass
class StepType(ABC):
    title: str = ""
    text: str = ""
    cost: int = 0
    lesson_id: int = None
    position: int = None

    @abstractmethod
    def body(self) -> dict:
        pass


@dataclass
class StepText(StepType):
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
class Answer:
    text: str
    is_correct: bool


@dataclass
class StepQuiz(StepType):
    answers: list[Answer] = field(default_factory=list)
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
class StepNumber(StepType):
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
class StepString(StepType):
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
class StepTask(StepType):
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
class StepSort(StepType):
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
class MatchPair:
    first: str
    second: str


@dataclass
class StepMatch(StepType):
    preserve_firsts_order: bool = True
    pairs: list[MatchPair] = field(default_factory=list)

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


@dataclass
class BlankType(ABC):
    @abstractmethod
    def body(self) -> dict:
        pass


@dataclass
class BlankText(BlankType):
    text: str

    def body(self) -> dict:
        return {"type": "text", "text": self.text, "options": []}


@dataclass
class BlankInput(BlankType):
    answers: list[Answer] = field(default_factory=list)

    def body(self) -> dict:
        return {
            "type": "input",
            "text": "",
            "options": [
                {"text": answer.text, "is_correct": answer.is_correct}
                for answer in self.answers
            ],
        }


@dataclass
class BlankSelect(BlankType):
    answers: list[Answer] = field(default_factory=list)

    def body(self) -> dict:
        return {
            "type": "select",
            "text": "",
            "options": [
                {"text": answer.text, "is_correct": answer.is_correct}
                for answer in self.answers
            ],
        }


@dataclass
class StepFill(StepType):
    is_case_sensitive: bool = False
    is_detailed_feedback: bool = False
    is_partially_correct: bool = False
    components: list[BlankType] = field(default_factory=list)

    def body(self) -> dict:
        return {
            "stepSource": {
                "lesson": self.lesson_id,
                "position": self.position,
                "block": {
                    "name": "fill-blanks",
                    "text": self.text,
                    "source": {
                        "components": [
                            component.body() for component in self.components
                        ],
                        "is_case_sensitive": self.is_case_sensitive,
                        "is_detailed_feedback": self.is_detailed_feedback,
                        "is_partially_correct": self.is_partially_correct,
                    },
                },
                "cost": self.cost,
            }
        }


@dataclass
class Table:
    is_checkbox: bool = False
    rows: Dict[str, List[bool]] = field(default_factory=dict)
    columns: list[str] = field(default_factory=list)

    def rows_body(self):
        return [
            {"name": key, "columns": [{"choice": choice} for choice in self.rows[key]]}
            for key in self.rows.keys()
        ]

    def columns_body(self):
        return [{"name": self.columns[i]} for i in range(len(self.columns))]


@dataclass
class StepTable(StepType):
    table: Table = None
    is_randomize_rows: bool = False
    is_randomize_columns: bool = False
    is_always_correct: bool = False
    description: str = ""

    def body(self) -> dict:
        return {
            "stepSource": {
                "lesson": self.lesson_id,
                "position": self.position,
                "block": {
                    "name": "table",
                    "text": self.text,
                    "source": {
                        "columns": self.table.columns_body(),
                        "rows": self.table.rows_body(),
                        "options": {
                            "is_checkbox": self.table.is_checkbox,
                            "is_randomize_rows": self.is_randomize_rows,
                            "is_randomize_columns": self.is_randomize_columns,
                            "sample_size": -1,
                        },
                        "description": self.description,
                        "is_always_correct": self.is_always_correct,
                    },
                },
                "cost": self.cost,
            }
        }
