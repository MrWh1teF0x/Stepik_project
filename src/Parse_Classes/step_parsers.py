from dataclasses import field, dataclass
import src.parse_classes.pyparse_formats as PPF
from abc import ABC, abstractmethod
import warnings


@dataclass
class TypeStep(ABC):
    title: str = ""
    text: str = ""
    cost: int = 0
    lesson_id: int = None
    position: int = None

    def __repr__(self):
        return f"TypeStep('{self.title}')"

    def _pre_parse(self, markdown: list[str]):
        self.title = PPF.match_format(markdown[0], PPF.format_step_name)["step_name"]
        markdown[0] = "## " + self.title

        # TODO: parse for config

    @abstractmethod
    def _parse(self, markdown: list[str]):
        pass

    def parse(self, markdown: list[str]) -> None:
        self._pre_parse(markdown)
        self._parse(markdown)

    @abstractmethod
    def body(self) -> dict:
        return {}


@dataclass
class StepText(TypeStep):
    def __repr__(self):
        return f"StepText('{self.title}')"

    def _parse(self, markdown: list[str]) -> None:
        self.text = PPF.md_to_html(markdown)

        self.body()

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
    match_substring: bool = False
    case_sensitive: bool = False
    use_re: bool = False
    answer: str = ""

    def __repr__(self):
        return f"StepString('{self.title}')"

    def _parse(self, markdown: list[str]) -> None:
        text = []
        for line in markdown:
            if PPF.check_format(line, PPF.format_string_answer, _match_all=True):
                # TODO: might want to check for a several answer tokens
                self.answer = PPF.match_format(line, PPF.format_string_answer)["answer"]
            else:
                text.append(line)
        self.text = PPF.md_to_html(text)

        self.body()

    def body(self) -> dict:
        return {
            "stepSource": {
                "block": {
                    "name": "string",
                    "text": self.text,
                    "source": {
                        "pattern": self.answer,
                        "code": "",
                        "match_substring": self.match_substring,
                        "case_sensitive": self.case_sensitive,
                        "use_re": self.use_re,
                        "is_file_disabled": True,
                        "is_text_disabled": False,
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
    max_error: float = None

    def __repr__(self):
        return f"StepNumber('{self.title}')"

    def _parse(self, markdown: list[str]) -> None:
        text = []
        for line in markdown:
            if PPF.check_format(line, PPF.format_number_answer, _match_all=True):
                a = PPF.match_format(line, PPF.format_number_answer)
                self.answer = a["answer"]
                self.max_error = a.get("adm_err", 0)
                del a
            else:
                text.append(line)
        self.text = PPF.md_to_html(text)

        self.body()

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
class StepQuiz(TypeStep):
    answers: list[tuple[str, bool]] = field(default_factory=list)
    do_shuffle: bool = True
    is_multiple_choice: bool = True

    def __repr__(self):
        return f"StepQuiz('{self.title}')"

    def _parse(self, markdown: list[str]) -> None:
        text, options = [], []
        status, line_i, running = "None", 0, True
        # parse for text ------------------------------------------------------
        while running:
            line = markdown[line_i]

            if PPF.check_format(line, PPF.format_text_begin, _match_all=True):
                status = "Text"
                text.append(PPF.match_format(line, PPF.format_text_begin)["text"])
                line_i += 1
                while line_i < len(markdown) and status == "Text":
                    text.append(markdown[line_i])
                    if PPF.check_format(
                        markdown[line_i], PPF.format_text_end, _match_all=True
                    ):
                        status = "None"
                        text.pop(-1)
                    line_i += 1

                if status == "Text":
                    raise SyntaxError(f"In {self}: no closure TEXTEND for TEXTBEGIN")
            elif not PPF.check_format(line, PPF.format_quiz_option):
                text.append(line)
                line_i += 1
            else:
                p_res = PPF.match_format(line, PPF.format_quiz_option)
                if p_res["letter"] == "A":
                    running = False
                else:
                    line_i += 1

            if line_i >= len(markdown):
                raise SyntaxError(f"In {self}: no AIKEN quiz options given")

        # parse for quiz options ----------------------------------------------
        running = True
        while running:
            line = markdown[line_i]
            if PPF.check_format(line, PPF.format_quiz_option):
                p_res = PPF.match_format(line, PPF.format_quiz_option)
                options.append([p_res["letter"], [p_res["text"]]])
                line_i += 1
            elif not PPF.check_format(
                line, PPF.format_quiz_answer
            ) and not PPF.check_format(line, PPF.format_quiz_shuffle):
                options[-1][1].append(line)
                line_i += 1
            else:
                running = False

            if line_i >= len(markdown):
                raise SyntaxError(f"In {self}: no ANSWER(s) given")

        for i in range(1, len(options)):
            if ord(options[i][0]) - ord(options[i - 1][0]) != 1:
                raise SyntaxError(
                    f"""In {self}: expected "{chr(ord(options[i - 1][0]) + 1)}" after "{options[i - 1][0]}", \
got "{options[i][0]}" instead"""
                )

        # parse for params and answer options ---------------------------------
        ans = set()
        do_shuffle = None
        running = True
        while running:
            line = markdown[line_i]
            if not ans and PPF.check_format(line, PPF.format_quiz_answer):
                ans = set(PPF.match_format(line, PPF.format_quiz_answer)["answer"])
            elif (do_shuffle is None) and PPF.check_format(
                line, PPF.format_quiz_shuffle
            ):
                do_shuffle = PPF.match_format(line, PPF.format_quiz_shuffle)[
                    "do_shuffle"
                ]

            line_i += 1
            if line_i >= len(markdown):
                running = False

        self.text = PPF.md_to_html(text)
        self.answers = [
            (PPF.md_to_html(text), letter in ans) for letter, text in options
        ]
        self.is_multiple_choice = len(ans) > 1
        self.do_shuffle = self.do_shuffle if do_shuffle is None else do_shuffle

        self.body()

    def body(self) -> dict:
        return {
            "stepSource": {
                "block": {
                    "name": "choice",
                    "text": self.text,
                    "source": {
                        "options": [
                            {"text": ans[0], "is_correct": ans[1], "feedback": ""}
                            for ans in self.answers
                        ],
                        "is_always_correct": False,
                        "is_html_enabled": True,  # allow html in options
                        "sample_size": len(self.answers),
                        "is_multiple_choice": self.is_multiple_choice,
                        "preserve_order": not self.do_shuffle,
                        "is_options_feedback": False,
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


class StepTask(TypeStep):
    code: str = ""
    samples_count: int = 1
    execution_time_limit: int = 5
    execution_memory_limit: int = 256
    test_cases: list[TaskTest] = field(default_factory=list)

    def __parse(self, markdown: list[str]) -> None:
        pass

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
class StepSort(TypeStep):
    sorted_answers: list[str] = field(default_factory=list)

    def parse(self, markdown: list[str]) -> None:
        pass

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
class StepMatch(TypeStep):
    preserve_firsts_order: bool = True
    pairs: list[MatchPair] = field(default_factory=list)

    def parse(self, markdown: list[str]) -> None:
        pass

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
class Answer:
    text: str
    is_correct: bool


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
class StepFill(TypeStep):
    is_case_sensitive: bool = False
    is_detailed_feedback: bool = False
    is_partially_correct: bool = False
    components: list[BlankType] = field(default_factory=list)

    def parse(self, markdown: list[str]) -> None:
        pass

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
    rows: dict[str, list[bool]] = field(default_factory=dict)
    columns: list[str] = field(default_factory=list)

    def rows_body(self):
        return [
            {"name": key, "columns": [{"choice": choice} for choice in self.rows[key]]}
            for key in self.rows.keys()
        ]

    def columns_body(self):
        return [{"name": self.columns[i]} for i in range(len(self.columns))]


@dataclass
class StepTable(TypeStep):
    table: Table = None
    is_randomize_rows: bool = False
    is_randomize_columns: bool = False
    is_always_correct: bool = False
    description: str = ""

    def parse(self, markdown: list[str]) -> None:
        pass

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


default_step_format = StepText

STEP_MAP = {
    "": default_step_format,
    "TEXT": StepText,
    "STRING": StepString,
    "NUMBER": StepNumber,
    "QUIZ": StepQuiz,
}
