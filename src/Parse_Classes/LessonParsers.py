from src.Parse_Classes.StepParsers import *
import src.PyParseFormats as PPF


STEP_MAP = {PPF.format_step_text_name: StepText}
default_step_format = StepText


class Lesson:
    id: int = -1
    name: str = ""
    steps: list[TypeStep] = field(default_factory=list[TypeStep])
    f_path: str = ""

    def __init__(self, file_path: str = ""):
        self.set_path(file_path)

    def __repr__(self):
        return f"Lesson('{self.name}', {self.id})"

    def set_path(self, file_path: str):
        self.f_path = file_path

    def read_file(self, file_path: str) -> list[str]:
        try:
            text_file = open(file_path, "r+", encoding="UTF-8").read().splitlines()
            return text_file
        except FileNotFoundError or FileExistsError:
            warnings.warn(UserWarning("File not found or doesn't exist"), stacklevel=2)
        except Exception:
            warnings.warn(UserWarning("Unknown Error in read_file()"), stacklevel=2)

        return []

    def parse(self, f_path: str = ""):
        # check if there is something to parse
        if f_path is "":
            if self.f_path is None:  # file wasn't loaded
                warnings.warn(UserWarning("Nothing to parse"), stacklevel=2)
                return 0
            f_path = self.f_path

        markdown = self.read_file(f_path)

        # parse for lesson_name and lesson_id
        name_token = PPF.search_format_in_text(markdown, PPF.format_lesson_name)
        if not name_token:
            warnings.warn(UserWarning("Lesson name is incorrect"), stacklevel=2)
            return

        id_token = PPF.search_format_in_text(
            markdown[name_token[0][1] + 1 :], PPF.format_lesson_id
        )
        if not id_token:
            warnings.warn(UserWarning("Lesson id is incorrect"), stacklevel=2)
            return

        self.name = name_token[0][0]["lesson_name"]
        self.id = int(id_token[0][0]["lesson_id"])

        # parse for steps
        step_lines = PPF.search_format_in_text(
            markdown[id_token[0][1] + 1 :], PPF.format_step_name
        )
        for i in range(len(step_lines) - 1):
            step_text = markdown[step_lines[i][1] : step_lines[i + 1][1]]
            new_step = self.create_step(step_text)
            self.add_step(new_step, i)

    def identify_step(self, header_line: str):
        for step_format, step_type in STEP_MAP.items():
            if PPF.check_format(header_line, step_format):
                return step_format
        return default_step_format

    def create_step(self, markdown: list[str]) -> TypeStep:
        Step = self.identify_step(markdown[0])
        step = Step()

    def add_step(self, step: TypeStep, position: int = 0):
        pass
