from dataclasses import field, dataclass
import src.PyParseFormats as PPF
from abc import ABC, abstractmethod
import warnings


class TypeStep(ABC):
    json_data: dict = field(default_factory=dict)

    def __init__(self, markdown: list[str] | None = None):
        if markdown is not None:
            self.parse(markdown)

    def __repr__(self):
        return f"TypeStep()"

    @abstractmethod
    def parse(self, markdown: list[str]) -> None:
        pass

    @abstractmethod
    def build_body(self):
        self.json_data = {"block": {}}


class StepText(TypeStep):
    text: str = ""
    json_data: dict = field(default_factory=dict)

    def __repr__(self):
        return f"StepText()"

    def parse(self, markdown: list[str]) -> None:
        if not PPF.check_format(markdown[0], PPF.format_step_text_name):
            if not PPF.check_format(markdown[0], PPF.format_step_name):
                raise SyntaxError(
                    "Step:Text was set or written incorrectly - Impossible ERROR"
                )

        self.text = PPF.md_to_html(markdown)

        self.build_body()

    def build_body(self) -> None:
        self.json_data = {
            "block": {
                "name": "text",
                "text": self.text,
            }
        }


class StepString(TypeStep):
    text: str = ""
    match_substring: bool = False
    case_sensitive: bool = False
    use_re: bool = False
    answer: str = ""
    json_data: dict = field(default_factory=dict)

    def __repr__(self):
        return f"StepString()"

    def parse(self, markdown: list[str]) -> None:
        if not PPF.check_format(markdown[0], PPF.format_step_string_name, _from_start=True):
            raise SyntaxError("Step:String was set incorrectly")

        text = []
        for line in markdown:
            if PPF.check_format(line, PPF.format_string_answer, _from_start=True):
                # TODO: might want to check for a several answer tokens
                self.answer = PPF.match_format(line, PPF.format_string_answer)["answer"]
            else:
                text.append(line)
        self.text = PPF.md_to_html(text)

        self.build_body()

    def build_body(self) -> None:
        self.json_data = {
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
            }
        }


class StepNumber(TypeStep):
    title: str = ""
    text: str = ""
    answer: float = None
    max_error: float = None
    cost: int = 0
    json_data: dict = field(default_factory=dict)

    def __repr__(self):
        return f"StepNumber()"

    def parse(self, markdown: list[str]) -> None:
        if not PPF.check_format(markdown[0], PPF.format_step_number_name, _from_start=True):
            raise SyntaxError("Step:Number was set incorrectly")

        text = []
        for line in markdown:
            if PPF.check_format(line, PPF.format_number_answer, _from_start=True):
                a = PPF.match_format(line, PPF.format_number_answer)
                self.answer = a["answer"]
                self.max_error = a.get("adm_err", 0)
                del a
            else:
                text.append(line)
        self.text = PPF.md_to_html(text)

        self.build_body()

    def build_body(self):
        self.json_data = {
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
            }
        }


class StepQuiz(TypeStep):
    title: str = ""
    text: str = ""
    answers: list[tuple[str, bool]] = field(default_factory=list)
    cost: int = 0
    json_data: dict = field(default_factory=dict)
    do_shuffle: bool

    def __repr__(self):
        return f"StepQuiz()"

    def parse(self, markdown: list[str]) -> None:
        if not PPF.check_format(markdown[0], PPF.format_step_number_name, _from_start=True):
            raise SyntaxError("Step:Number was set incorrectly")

        text, options = [], []
        status, i, running = "None", 0, True
        # parse for text ------------------------------------------------------
        while running:
            line = markdown[i]

            if PPF.check_format(line, PPF.format_text_begin, _from_start=True):
                status = "Text"
                text.append(PPF.match_format(line, PPF.format_text_begin)["text"])
                i += 1
                while i < len(markdown) and status == "Text":
                    text.append(markdown[i])
                    if PPF.check_format(markdown[i], PPF.format_text_end, _from_start=True):
                        status = "None"
                        text.pop(-1)
                    i += 1

                if status == "Text":
                    raise SyntaxError(f"In {self}: no closure TEXTEND for TEXTBEGIN")
            elif not PPF.check_format(line, PPF.format_quiz_option):
                text.append(line)
                i += 1
            else:
                p_res = PPF.match_format(line, PPF.format_quiz_option)
                if p_res["letter"] == "A":
                    running = False
                else:
                    i += 1

            if i >= len(markdown):
                raise SyntaxError(f"In {self}: no AIKEN quiz options given")

        # parse for quiz options ----------------------------------------------

        running = True
        while running:
            line = markdown[i]

            if PPF.check_format(line, PPF.format_quiz_option):
                options[-1][1] = "\n".join(options[-1][1])
                p_res = PPF.match_format(line, PPF.format_quiz_option)
                options.append([p_res["letter"], [p_res["text"]]])
                i += 1
            elif not PPF.check_format(line, PPF.format_quiz_answer) or \
                    not PPF.check_format(line, PPF.format_quiz_shuffle):
                options[-1][1].append(line)
                i += 1
            else:
                options[-1][1] = "\n".join(options[-1][1])
                running = False

            if i >= len(markdown):
                raise SyntaxError(f"In {self}: no ANSWER(s) given")

        for i in range(1, len(options)):
            if ord(options[i][0]) - ord(options[i - 1][0]) != 1:
                raise SyntaxError(
                    f"""In {self}: expected "{chr(ord(options[i - 1][0]) + 1)}" after "{options[i - 1][0]}", \
got "{options[i][0]}" instead""")

        # parse for params and answer options ---------------------------------
        ans = set()
        do_shuffle = None
        running = True
        while running:
            line = markdown[i]
            if not ans and PPF.check_format(line, PPF.format_quiz_answer):
                ans = set(PPF.match_format(line, PPF.format_quiz_answer)["answer"])
            elif (do_shuffle is None) and PPF.check_format(line, PPF.format_quiz_shuffle):
                do_shuffle = PPF.match_format(line, PPF.format_quiz_shuffle)["do_shuffle"]

            i += 1
            if i >= len(markdown):
                running = False

        self.text = PPF.md_to_html(text)
        self.answers = [(PPF.md_to_html(text), letter in ans) for letter, text in options]
        self.do_shuffle = True if do_shuffle is None else do_shuffle

        self.build_body()

    def build_body(self):
        self.json_data = {
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
                    "is_multiple_choice": len(self.answers) > 1,
                    "preserve_order": not self.do_shuffle,
                    "is_options_feedback": False,
                },
            }
        }


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


STEP_MAP = {
    PPF.format_step_text_name: StepText,
    PPF.format_step_string_name: StepString,
    PPF.format_step_number_name: StepNumber,
    PPF.format_step_quiz_name: StepQuiz,
}

default_step_format = StepText