import warnings

from src.Parse_Classes.StepParsers import *
import src.PyParseFormats as PPF


class Lesson:
    id: int = -1
    name: str = ""
    steps: list[TypeStep] = field(default_factory=list[TypeStep])
    f_path: str | None = None

    def __init__(self, file_path: str | None = None):
        if file_path is not None:
            self.set_path(file_path)  # TODO: swap to parse and add PATH_obj

    def __repr__(self):
        return f"Lesson('{self.name}', {self.id})"

    def set_path(self, file_path: str):
        self.f_path = file_path

    @staticmethod
    def read_file(file_path: str) -> list[str]:
        try:
            text_file = open(file_path, "r+", encoding="UTF-8").read().splitlines()
            return text_file
        except FileNotFoundError or FileExistsError:
            warnings.warn(UserWarning("File not found or doesn't exist"), stacklevel=2)
        except Exception:
            warnings.warn(UserWarning("Unknown Error in Lesson.read_file()"), stacklevel=2)

    def parse(self, f_path: str = ""):
        self.steps = []
        # check if there is something to parse ------------------------------
        if f_path == "":
            if self.f_path is None:  # file wasn't loaded
                warnings.warn(UserWarning("Nothing to parse"), stacklevel=2)
                return
            f_path = self.f_path

        markdown = self.read_file(f_path)

        # parse for lesson_name and lesson_id ---------------------------------
        name_token = PPF.search_format_in_text(
            markdown, PPF.format_lesson_name, _amount=1, _from_start=True)
        if not name_token:
            warnings.warn(UserWarning("Lesson name is incorrect"), stacklevel=2)
            return
        self.name = name_token[0][0]["lesson_name"]

        id_token = PPF.search_format_in_text(
            markdown, PPF.format_lesson_id, _from_line=name_token[0][1] + 1, _amount=1)
        if not id_token:  # ID is not always given in file
            self.id = -1
            id_token = (("_", name_token[0][1]),)
        else:
            self.id = int(id_token[0][0]["lesson_id"])

        # parse for steps ---------------------------------------------------
        step_lines = PPF.search_format_in_text(
            markdown, PPF.format_step_name, _from_line=id_token[0][1] + 1,  _from_start=True)

        if len(step_lines) != 0:
            step_text = markdown[step_lines[-1][1]:]
            new_step = self.create_step(step_text)
            self.add_step(new_step)
            for i in range(len(step_lines) - 1):
                step_text = markdown[step_lines[i][1]: step_lines[i + 1][1]]
                new_step = self.create_step(step_text)
                self.add_step(new_step)
        elif id_token[0][1] + 1 < len(markdown) - 2:  # if no steps, but lots of lines
            warnings.warn(
                UserWarning(f"Lesson {self.name} contains lots of excessive lines"),
                stacklevel=2)

    @staticmethod
    def identify_step(header_line: str):
        for step_format, step_type in STEP_MAP.items():
            if PPF.check_format(header_line, step_format):
                return step_type
        return default_step_format

    def create_step(self, markdown: list[str]) -> TypeStep:
        Step = self.identify_step(markdown[0])
        step = Step(markdown)
        return step

    def add_step(self, step: TypeStep, position: int = -1):
        if position == -1:
            self.steps.append(step)
        else:
            self.steps.insert(position, step)
