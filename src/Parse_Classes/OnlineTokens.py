import _io
import warnings

from Parse_Classes.PageParsers import Page


class OnlineStep:
    id: int = None
    position = None
    data: Page = None

    def __init__(self):
        pass


class OnlineLesson:
    id: int = None
    steps: list[OnlineStep] = []
    file: _io.TextIOWrapper = None

    def __init__(self, file_path: str = ""):
        if file_path == "":
            self.open_file(file_path)

    def open_file(self, file_path: str):
        try:
            file = open(file_path, "r+", encoding="UTF-8")
            self.file = file
        except FileNotFoundError or FileExistsError:
            warnings.warn(ImportWarning("File not found or doesn't exists"))
        except Exception:
            print(self.__repr__() + ":\n Unknown Error in open()")

    def parse(self):
        pass