import requests
import json
from src.StepikAPI.logged_session import LoggedSession
from src.Parse_Classes.OnlineTokens import OnlineStep, OnlineLesson


class StepikAPI:
    session: LoggedSession = None
    url = "https://stepik.org/api/step-sources"

    def __init__(self, session: LoggedSession) -> None:
        self.session = session

    def step_create(self, payload: dict) -> OnlineStep:
        responce = requests.post(
            url=self.url, json=payload, headers=self.session.headers()
        )
        json_data = json.loads(responce.text)
        return OnlineStep(
            json_data["step-sources"][0]["id"], json_data["step-sources"][0]["position"]
        )

    def step_delete(self, id: int) -> None:
        responce = requests.delete(
            url=self.url + f"/{id}", headers=self.session.headers()
        )

    def step_update(self, payload: dict, id: int) -> None:
        responce = requests.put(
            url=self.url + f"/{id}",
            json=payload,
            headers=self.session.headers(),
        )

    def fetch_objects() -> None:
        pass

    @staticmethod
    def get_session(self, client_id: str, client_secret: str) -> LoggedSession:
        session = LoggedSession(client_id, client_secret)
        return session
