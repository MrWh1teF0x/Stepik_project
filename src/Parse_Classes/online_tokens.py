import requests
import json
from dataclasses import dataclass, field

from src.Parse_Classes.types_of_step import *
from src.StepikAPI.logged_session import LoggedSession as Session
from src.StepikAPI.logged_session import TypeRequest


host = "https://stepik.org"


@dataclass
class OnlineStep:
    step_data: TypeStep = None
    id: int = None
    url = f"{host}/api/step-sources"

    def __post_init__(self):
        if not self.id:
            return

        step_info = self.info()["steps"][0]

        lesson_id = step_info["lesson"]
        position = step_info["position"]
        text = step_info["block"]["text"]
        self.step_data = StepText(text=text, lesson_id=lesson_id, position=position)

    def info(self):
        if not self.id:
            raise AttributeError("This step has no id!")

        session = Session()
        responce = session.request(
            method=TypeRequest.GET, url=f"{host}/api/steps/{self.id}"
        )
        return json.loads(responce.text)

    def create(self, step_data: TypeStep = None):
        if step_data:
            self.step_data = step_data

        session = Session()
        responce = session.request(
            method=TypeRequest.POST, url=self.url, json_data=self.step_data.body()
        )

        json_data = json.loads(responce.text)
        self.id = json_data["step-sources"][0]["id"]

    def update(self, step_data: TypeStep = None):
        if step_data:
            self.step_data = step_data

        session = Session()
        session.request(
            TypeRequest.PUT,
            f"{self.url}/{self.id}",
            json_data=self.step_data.body(),
        )

    def delete(self):
        session = Session()
        session.request(TypeRequest.DELETE, url=self.url)
        self.step_data = None


@dataclass
class OnlineLesson:
    id: int = None
    name: str = ""
    steps: list[OnlineStep] = field(default_factory=list)
    url = f"{host}/api/lessons"

    def __post_init__(self):
        if self.id:
            return

        json_data = self.info()["lessons"][0]

        for step_id in json_data["steps"]:
            print(step_id)
            self.add_step(OnlineStep(id=step_id))

    def info(self):
        if not self.id:
            raise AttributeError("This lesson has no id!")

        session = Session()
        responce = session.request(method=TypeRequest.GET, url=f"{self.url}/{self.id}")
        return json.loads(responce.text)

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

    def update(self, steps: list[OnlineStep]):
        new_step_ids = [step.id for step in steps]
        old_step_ids = []

        for old_step in self.steps:
            if old_step.id not in new_step_ids:
                old_step.delete()
            else:
                old_step_ids.append(old_step.id)

        for step in steps:
            if step.id not in old_step_ids:
                step.step_data.lesson_id = self.id
                step.create()
            else:
                step.update()

    def get_steps_ids(self):
        session = Session()
        responce = session.request(TypeRequest.GET, url=f"{self.url}/{self.id}")
        return json.loads(responce.text)["lessons"][0]["steps"]


@dataclass
class OnlineUnit:
    section_id: int
    lesson_id: int
    id: int = None
    url = f"{host}/api/units"


@dataclass
class OnlineSection:
    course_id: int
    id: int = None
    position: int = None
    units: list[OnlineUnit] = field(default_factory=list)
    url = f"{host}/api/sections"


@dataclass
class OnlineCourse:
    id: int
    sections: list[OnlineSection] = field(default_factory=list)
    url = f"{host}/api/courses"
