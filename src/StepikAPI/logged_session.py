import requests
import json


class LoggedSession:
    api_host = "https://stepik.org"
    course_host = "https://stepik.org/teach/courses"

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

        # Получаем cookie
        cookie_responce = requests.get(self.course_host)
        self.__cookie = f'csrftoken={cookie_responce.cookies["csrftoken"]}; sessionid={cookie_responce.cookies["sessionid"]}'

    def request(self):
        pass

    def token(self):
        return self.__token

    def cookie(self):
        return self.__cookie

    def headers(self):
        pass
