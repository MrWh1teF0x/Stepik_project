import _io
import warnings

from src.Parse_Classes.PageParsers import Page


class OnlineStep:
    id: int = None
    position = None
    data: Page = None

    def __init__(self):
        pass


class OnlineLesson:
    id: int = None
    steps: list[OnlineStep] = []
    file: list[str] = None

    def __init__(self, file_path: str = ""):
        if file_path == "":
            self.read_file(file_path)

    def read_file(self, file_path: str):
        try:
            self.file = open(file_path, "r+", encoding="UTF-8").readlines()
        except FileNotFoundError or FileExistsError:
            warnings.warn(ImportWarning("File not found or doesn't exists"))
        except Exception:
            print(self.__repr__() + ":\n Unknown Error in open()")

    def parse(self):
        pass