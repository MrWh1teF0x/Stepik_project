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

    def parse(self, markdown: list[str]) -> None:
        pass

    def build_body(self):
        self.json_data = {
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
