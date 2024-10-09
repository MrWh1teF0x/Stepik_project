import io
import warnings
import requests
import json


from src.Parse_Classes.PageParsers import Page
import src.Parse_Classes.RegExpFormats as REF
from src.Parse_Classes.PageParsers import Page
from src.StepikAPI.logged_session import LoggedSession


class OnlineStep:
    lesson_id: int = None
    id: int = None
    position = None
    data: Page = None
    payload: dict = None

    def __init__(
        self,
        lesson_id: int,
        id: int = -1,
        position: int = 0,
        markdown: list[str] = None,
    ):
        self.lesson_id = lesson_id
        self.id = id
        self.position = position

    def build_page(self, markdown: list[str]):
        self.data = Page()


class OnlineLesson:
    id: int = None
    name: str = None
    steps: list[OnlineStep] = []
    file: list[str] = None
    url = "https://stepik.org/api/lessons"

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

    def update(self, session: LoggedSession, steps: list[OnlineStep]):
        url = "https://stepik.org/api/step-sources"

        old_step_ids = self.get_steps_ids(session)

        steps_for_delete = list(
            set(old_step_ids).difference(set(step.id for step in steps))
        )
        for i in range(len(steps_for_delete)):
            responce = requests.delete(
                url=f"{url}/{steps_for_delete[i]}",
                headers=session.headers(),
            )

        for step in steps:
            if step.id in old_step_ids:
                responce = requests.put(
                    url=f"{url}/{step.id}", json=step.payload, headers=session.headers()
                )
            else:
                responce = requests.post(
                    url=url, json=step.payload, headers=session.headers()
                )
                step.id = json.loads(responce.text)["step-sources"][0]["id"]

    def get_steps_ids(self, session: LoggedSession):
        responce = requests.get(url=f"{self.url}/{self.id}", headers=session.headers())
        return json.loads(responce.text)["lessons"][0]["steps"]


class OnlineCourse:
    id: int = None
    lessons: list[OnlineLesson] = []
    url = "https://stepik.org/api/courses"

    def __init__(self, id: int):
        self.id = id
