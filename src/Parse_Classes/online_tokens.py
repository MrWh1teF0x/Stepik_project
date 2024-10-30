import requests
import json
from dataclasses import dataclass, field

from src.Parse_Classes.types_of_step import *
from src.StepikAPI.logged_session import LoggedSession as Session


host = "https://stepik.org"


@dataclass
class OnlineStep:
    step_data: TypeStep = None
    id: int = None
    url = f"{host}/api/step-sources"

    def info(self):
        if not self.id:
            raise AttributeError("This step has no id!")

        session = Session()
        responce = session.request(method="get", url=f"{host}/api/steps/{self.id}")
        return json.loads(responce.text)

    def create(self, step_data: TypeStep = None):
        if step_data:
            self.step_data = step_data

        session = Session()
        responce = session.request(
            method="post", url=self.url, json_data=self.step_data.body()
        )

        json_data = json.loads(responce.text)
        self.id = json_data["step-sources"][0]["id"]

    def update(self, step_data: TypeStep = None):
        if step_data:
            self.step_data = step_data

        session = Session()
        session.request(
            "put",
            f"{self.url}/{self.id}",
            json_data=self.step_data.body(),
        )

    def delete(self):
        if not self.id:
            raise AttributeError("This step has no id!")

        session = Session()
        session.request("delete", url=f"{self.url}/{self.id}")
        self.step_data = None


@dataclass
class OnlineLesson:
    id: int = None
    name: str = ""
    steps: list[OnlineStep] = field(default_factory=list)
    url = f"{host}/api/lessons"

    def __post_init__(self):
        if not self.id:
            return

        json_data = self.info()["lessons"][0]

        for step_id in json_data["steps"]:
            self.steps.append(OnlineStep(id=step_id))

    def info(self):
        if not self.id:
            raise AttributeError("This lesson has no id!")

        session = Session()
        responce = session.request(method="get", url=f"{self.url}/{self.id}")
        return json.loads(responce.text)

    def add_step(self, step: OnlineStep):
        position = step.step_data.position
        self.steps.insert(position, step)

        step.create()

    def update(self, steps: list[OnlineStep]):
        if not self.id:
            raise AttributeError("This lesson has no id!")

        if len(self.steps) > len(steps):
            while len(self.steps) != len(steps):
                index = len(self.steps) - 1
                self.steps[index].delete()
                del self.steps[index]

        for i, new_step in enumerate(steps):
            if len(self.steps) > i:
                new_step.id = self.steps[i].id
                self.steps[i] = new_step
                new_step.update()
            else:
                self.add_step(new_step)

    def get_steps_ids(self):
        session = Session()
        responce = session.request("get", url=f"{self.url}/{self.id}")
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
