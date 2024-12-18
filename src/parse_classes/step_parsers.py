import warnings
import src.parse_classes.pyparse_formats as PPF

from dataclasses import field, dataclass
from abc import ABC, abstractmethod


@dataclass
class StepType(ABC):
    title: str = ""
    text: str = ""
    cost: int = 0
    lesson_id: int = None
    position: int = None

    def __repr__(self):
        return f"StepType('{self.title}')"

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
class StepText(StepType):
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
class StepString(StepType):
    match_substring: bool = False
    case_sensitive: bool = False
    use_re: bool = False
    answer: str | None = None

    def __repr__(self):
        return f"StepString('{self.title}')"

    def _parse(self, markdown: list[str]) -> None:
        text = []
        for line in markdown:
            if not (self.answer is None) and PPF.check_format(line, PPF.format_string_answer, _match_all=True):
                self.answer = PPF.match_format(line, PPF.format_string_answer)["answer"]
            else:
                text.append(line)
        self.text = PPF.md_to_html(text)

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
class StepNumber(StepType):
    answer: float = None
    max_error: float = 0
    cost: int = 1

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
class StepQuiz(StepType):
    answers: list[tuple[str, bool]] = field(default_factory=list)
    do_shuffle: bool = True
    is_multiple_choice: bool = True
    cost: int = 1

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
                    if PPF.check_format(markdown[line_i], PPF.format_text_end, _match_all=True):
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


class StepTaskInLine(StepType):
    code: str = ""
    pre_code: str = ""
    post_code: str = ""
    test_cases: list[TaskTest] = field(default_factory=list)
    # config params
    code_lang: str = ""
    samples_count: int = 1
    execution_time_limit: int = 5
    execution_memory_limit: int = 256

    def __repr__(self):
        return f"StepTaskInLine('{self.title}')"

    def _parse(self, markdown: list[str]) -> None:
        default_section_parse = self._parse_text
        sections = {"CONFIG": self._parse_config,
                    "CODE": self._parse_code,
                    "HEADER": self._parse_header,
                    "FOOTER": self._parse_footer,
                    "TEST": self._parse_tests,
                    "": None, }

        section_list = PPF.search_format_in_text(
            markdown, PPF.format_taskinline_sectors, _from_start=True)
        section_list.append((None, len(markdown), 0, 0))  # so that last section will parse

        if len(section_list) != 0:
            default_section_parse(markdown[:section_list[0][1]])
            for i in range(len(section_list) - 1):
                k = section_list[i][0].get("section_type", "")
                parse_func = sections[k]
                section_text = markdown[section_list[i][1]:section_list[i + 1][1]]
                if parse_func is not None:
                    parse_func(section_text)
                else:
                    default_section_parse(section_text)
                    warnings.warn(
                        f"Wrong section token in {self}: {section_list[i][0]}",
                        Warning, stacklevel=2)

    def _parse_text(self, markdown: list[str]):
        self.text = PPF.md_to_html(markdown)

    def _parse_code(self, markdown: list[str]):
        self.code = "\n".join(markdown[1:])

    def _parse_header(self, markdown: list[str]):
        self.pre_code = "\n".join(markdown[1:])

    def _parse_footer(self, markdown: list[str]):
        self.post_code = "\n".join(markdown[1:])

    def _parse_tests(self, markdown: list[str]):
        self.test_cases = []

        test = [[], []]
        state = "input"
        for i in range(1, len(markdown)):
            if PPF.check_format(markdown[i], PPF.format_test_data_seperator):
                if state != "input":
                    warnings.warn(
                        f"Wrong test format in {self}: IN->OUT seperator in wrong place (testline index: {i})",
                        Warning, stacklevel=2
                    )
                    return
                state = "output"
            elif PPF.check_format(markdown[i], PPF.format_tests_seperator):
                self.test_cases.append(TaskTest("\n".join(test[0]), "\n".join(test[1])))
                test = [[], []]
                state = "input"

            elif state == "input":
                test[0].append(markdown[i])
            elif state == "output":
                test[1].append(markdown[i])

    def _parse_config(self, markdown: list[str]):
        for i in range(1, len(markdown)):
            res = PPF.match_format(markdown[i], PPF.format_taskinline_parameter)
            if not res.asList():
                continue

            if hasattr(self, res['parameter']):
                setattr(self, res['parameter'], res['value'])
            else:
                warnings.warn(
                    f"In {self}: config section has excessive parameter - '{res['parameter']}'"
                )

    def build_code_template(self):
        if not self.code_lang:
            return ''
        s = f'::{self.code_lang}\n'
        if self.pre_code:
            s = s + '::header\n' + self.pre_code + '\n'
        if self.post_code:
            s = s + '::footer\n' + self.post_code + '\n'
        return s

    def body(self) -> dict:
        return {
            "stepSource": {
                "block": {
                    "name": "code",
                    "text": self.text,
                    "source": {
                        "code": self.code,
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
    cost: int = 5

    def _parse(self, markdown: list[str]) -> None:
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
class StepMatch(StepType):
    preserve_firsts_order: bool = True
    pairs: list[MatchPair] = field(default_factory=list)
    cost: int = 5

    def _parse(self, markdown: list[str]) -> None:
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

    def _parse(self, markdown: list[str]) -> None:
        pass

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

    def _parse(self, markdown: list[str]) -> None:
        pass

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
    cost: int = 5

    def _parse(self, markdown: list[str]) -> None:
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
class StepTable(StepType):
    table: Table = None
    is_randomize_rows: bool = False
    is_randomize_columns: bool = False
    is_always_correct: bool = False
    description: str = ""
    cost: int = 10

    def _parse(self, markdown: list[str]) -> None:
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


default_step = StepText

STEP_MAP = {
    "": default_step,
    "TEXT": StepText,
    "STRING": StepString,
    "NUMBER": StepNumber,
    "QUIZ": StepQuiz,
    "TASKINLINE": StepTaskInLine,
}
