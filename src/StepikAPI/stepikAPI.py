import requests
import json
from logged_session import LoggedSession


class StepikAPI:
    session: LoggedSession = None
    url = "https://stepik.org/api/step-sources"

    def __init__(self, session: LoggedSession, token: str, cookie: str) -> None:
        self.session = session
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token,
            "Cookie": cookie,
        }

    def login():
        pass

    def step_create(self, payload: dict):

        responce = requests.post(
            url=self.url, data=json.dumps(payload), headers=self.headers
        )

    def step_delete():
        pass

    def step_update():
        pass

    def fetch_objects():
        pass
