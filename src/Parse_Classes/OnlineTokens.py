import io
import warnings
import requests
import json
from dataclasses import dataclass, field
from src.StepikAPI.logged_session import LoggedSession as Session

import src.PyParseFormats as PPF
from src.Parse_Classes.PageParsers import Page


@dataclass
class OnlineStep:
    lesson_id: int
    step_data: TypeStep
    id: int = None
    position: int = None
    api_url = "https://stepik.org/api/step-sources"

    def identify_step(self, markdown: list[str]):
        pass

    def build_page(self, markdown: list[str]):
        self.identify_step(markdown)

        self.data = Page()

    def info(self, session: Session):
        pass

    def create(self, session: Session, step_data: TypeStep = None):
        responce = None

        if step_data:
            self.step_data = step_data

        self.step_data.json_data["stepSource"]["lesson"] = self.lesson_id
        self.step_data.json_data["stepSource"]["position"] = self.position

        responce = requests.post(
            url=self.api_url, json=self.step_data.json_data, headers=session.headers()
        )

        json_data = json.loads(responce.text)
        self.id = json_data["step-sources"][0]["id"]

    def update(self, session: Session, step_data: TypeStep = None):
        if self.id:
            raise AttributeError("This step has no id!")

        if step_data.json_data:
            self.step_data = step_data
        responce = requests.put(
            url=f"{self.api_url}/{self.id}",
            json=self.step_data.json_data,
            headers=session.headers(),
        )

    def delete(self, session: Session):
        if self.id:
            responce = requests.delete(
                url=f"{self.api_url}/{self.id}", headers=session.headers()
            )
            self.id = None
            self.position = None


@dataclass
class OnlineLesson:
    id: int = -1
    name: str = ""
    steps: list[OnlineStep] = field(default_factory=list)
    file: list[str] = None  # field(default_factory=list[str])
    f_path: str = ""
    api_url = "https://stepik.org/api/lessons"
        self.set_path(file_path)
    def __init__(self, file_path: str = ""):

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

    def add_step(self, step: OnlineStep, position: int = 0):
        if not (0 <= position <= len(self.steps) - 1 or position == 0):
            raise IndexError("Wrong position of the step!")

        if position == 0 or position == -1:
            self.steps.append(step)
        else:
            if position > 0:
                self.steps.insert(position - 1, step)
            else:
                self.steps.insert(position + 1, step)

    def update(self, session: Session, steps: list[OnlineStep]):
        url = "https://stepik.org/api/step-sources"

        new_step_ids = [step.id for step in steps]
        old_step_ids = []

        for old_step in self.steps:
            if old_step.id not in new_step_ids:
                old_step.delete(session)
            else:
                old_step_ids.append(old_step.id)

        for step in steps:
            if step.id not in old_step_ids:
                step.create(session)
            else:
                step.update(session)

    def get_steps_ids(self, session: Session):
        responce = requests.get(
            url=f"{self.api_url}/{self.id}", headers=session.headers()
        )
        return json.loads(responce.text)["lessons"][0]["steps"]


@dataclass
class OnlineUnit:
    section_id: int
    lesson_id: int
    id: int = None
    api_url = "https://stepik.org/api/units"


@dataclass
class OnlineSection:
    course_id: int
    id: int = None
    position: int = None
    units: list[OnlineUnit] = field(default_factory=list)
    api_url = "https://stepik.org/api/sections"


@dataclass
class OnlineCourse:
    id: int
    sections: list[OnlineSection] = field(default_factory=list)
    api_url = "https://stepik.org/api/courses"
