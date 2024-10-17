import warnings
from dataclasses import field, dataclass

import src.PyParseFormats as PPF
from src.Parse_Classes.PageParsers import Page


class OnlineStep:
    id: int = None
    position = None
    data: Page = None

    def __init__(self, markdown: list[str] = None):
        pass

    def identify_step(self):
        pass

    def build_page(self, markdown: list[str]):
        self.data = Page()


class OnlineLesson:
    id: int = -1
    name: str = ""
    steps: list[OnlineStep] = None  # field(default_factory=list[OnlineStep])
    file: list[str] = None  # field(default_factory=list[str])
    f_path: str = ""

    def __init__(self, file_path: str = ""):
        self.set_path(file_path)

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

    def parse(self, f_path: str = ''):
        # check if there is something to parse
        if f_path is '':
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

        id_token = PPF.search_format_in_text(markdown[name_token[0][1] + 1:], PPF.format_lesson_id)
        if not id_token:
            warnings.warn(UserWarning("Lesson id is incorrect"), stacklevel=2)
            return

        self.name = name_token[0][0]["lesson_name"]
        self.id = int(id_token[0][0]["lesson_id"])

        # parse for steps
        step_lines = PPF.search_format_in_text(markdown[id_token[0][1] + 1:], PPF.format_step_name)
        for i in range(len(step_lines) - 1):
            step_text = markdown[step_lines[i][1]:step_lines[i+1][1]]
            new_step = self.create_step(step_text)
            self.add_step(new_step, i)

    def create_step(self, markdown: list[str]) -> OnlineStep:
        pass

    def add_step(self, step: OnlineStep, position: int = 0):
        pass
