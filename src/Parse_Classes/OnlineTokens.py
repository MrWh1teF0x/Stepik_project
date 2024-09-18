import warnings

import src.RegExpFormats as REF
from src.Parse_Classes.PageParsers import Page


class OnlineStep:
    id: int = None
    position = None
    data: Page = None

    def __init__(self, markdown: list[str] = None):
        pass

    def build_page(self, markdown: list[str]):
        self.data = Page()


class OnlineLesson:
    id: int = None
    name: str = None
    steps: list[OnlineStep] = None
    file: list[str] = None

    def __init__(self, file_path: str = ""):
        if file_path != "":
            self.read_file(file_path)

    def read_file(self, file_path: str):
        try:
            self.file = open(file_path, "r+", encoding="UTF-8").read().splitlines()
        except FileNotFoundError or FileExistsError:
            warnings.warn(UserWarning("File not found or doesn't exist"), stacklevel=2)
        except Exception:
            warnings.warn(UserWarning("Unknown Error in read_file()"), stacklevel=2)

    def parse(self, markdown: list[str] = None):
        if markdown is None:
            if self.file is None:  # file wasn't loaded
                warnings.warn(UserWarning("Nothing to parse"), stacklevel=2)
                return 0
            markdown = self.file

        if REF.check_format(markdown[0], REF.format_lesson_name) is None:
            warnings.warn(UserWarning("Lesson name is incorrect"), stacklevel=2)
        if REF.check_format(markdown[2], REF.format_lesson_id):
            warnings.warn(UserWarning("Lesson id is incorrect"), stacklevel=2)

        self.id = int(markdown[2].split()[2])
        self.name = markdown[0].split()[1]

        #   splits remaining markdown on steps
        step_markdown = [markdown[4]]
        for line in markdown[5:]:
            if REF.check_format(line, REF.format_lesson_name) is None:
                self.steps.append(OnlineStep(step_markdown))
                step_text = []
            step_markdown.append(line)
