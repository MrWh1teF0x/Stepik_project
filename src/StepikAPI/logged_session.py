import requests
import json


class LoggedSession:
    api_host = "https://stepik.org"

    def __init__(self, client_id="", client_secret="") -> None:
        self.__session = requests.Session()

        # Получаем токен
        self.__auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
        response = requests.post(
            f"{self.api_host}/oauth2/token/",
            data={"grant_type": "client_credentials"},
            auth=self.__auth,
        )
        self.__token = json.loads(response.text)["access_token"]

    def request(self):
        pass

    def token(self):
        return self.__token

    def headers(self):
        pass
