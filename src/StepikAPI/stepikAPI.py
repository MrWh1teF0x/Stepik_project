import requests
import json
from logged_session import LoggedSession


class StepikAPI:
    session: LoggedSession = None
    url = "https://stepik.org/api/step-sources"

    def __init__(self, session: LoggedSession) -> None:
        self.session = session

    def login():
        pass

    def step_create(self, payload: dict):
        requests.post(
            url=self.url, data=json.dumps(payload), headers=self.session.headers()
        )

    def step_delete():
        pass

    def step_update(self, payload: dict, id: int):
        requests.put(
            url=self.url + f"/{id}",
            data=json.dumps(payload),
            headers=self.session.headers(),
        )

    def fetch_objects():
        pass
