import requests
import json
import pathlib
import logging
import pathlib
import yaml
from enum import Enum


class TypeRequest(Enum):
    POST = "post"
    GET = "get"
    PUT = "put"
    DELETE = "delete"


path = pathlib.Path(__file__).parent.parent.parent / "cred.yaml"
client_id, client_secret = None, None


def init_secret_fields() -> None:
    try:
        with path.open("r") as file:
            s = yaml.load(file, yaml.SafeLoader)
            global client_id, client_secret
            client_id = s["client_id"]
            client_secret = s["client_secret"]

    except FileExistsError:
        print('File "cred.yaml" does not exist!')

    except KeyError:
        print('There are no variables "client_id" or "client_secret"!')

    except Exception as e:
        print(e)


LOGGER_NAME = "stepik"
logger: logging.Logger = None


def setup_logger(log_cli_level, log_file_level) -> None:
    """
    Use own logger for logging into out.log file and console(?)
    """
    global logger

    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(max(log_cli_level, log_file_level))

    # create_by_type file handler which logs even debug messages

    current = pathlib.Path(__file__).parent.parent.resolve()
    full_filename = str(current.joinpath("out.log"))

    fh = logging.FileHandler(full_filename, mode="w", encoding="utf-8")
    fh.setLevel(log_file_level)

    # create_by_type console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(log_cli_level)

    # create_by_type formatter and add it to the handlers
    formatter_full = logging.Formatter(
        "%(asctime)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s",
        datefmt="%m-%d %H:%M:%S",
    )
    formatter_short = logging.Formatter(
        "%(levelname)8s: %(message)s", datefmt="%m-%d %H:%M:%S"
    )
    # formatter = logging.Formatter('%(message)s')
    fh.setFormatter(formatter_full)
    # ch.setFormatter(formatter_short)

    # add the handlers to the logger
    # logger.addHandler(ch)
    logger.addHandler(fh)


class LoggedSession:
    api_host = "https://stepik.org"
    course_host = "https://stepik.org/teach/courses"

    def __init__(
        self,
        log_url: bool = True,
        log_header: bool = True,
        log_data: bool = True,
        log_http_code: bool = True,
        log_resp_data=True,
    ) -> None:
        self.__session = requests.Session()

        # что именно логировать в запросе и ответе
        self.log_url = log_url
        self.log_header = log_header
        self.log_data = log_data
        self.log_http_code = log_http_code
        self.log_resp_data = log_resp_data

        # игнорировать ошибки ssl сертификата
        self.ignore_ssl_certificate_errors = False

        global client_id, client_secret

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

    def request(
        self,
        method: TypeRequest,
        url,
        stacklevel: int = 3,
        log_response_data: bool = True,
        json_data: dict = None,
    ) -> requests.Response:
        if self.log_url:
            logger.info(f"{method.value} {url}", stacklevel=stacklevel)
        if self.log_header:
            logger.info(
                f"Request Headers: {json.dumps(self.headers())}",
                stacklevel=stacklevel,
            )
            logger.info(
                f"Request Cookies: {json.dumps(self.cookie())}",
                stacklevel=stacklevel,
            )

        if self.log_data:
            logger.info(f"json = {json.dumps(json_data)}", stacklevel=stacklevel)

        res = self.__session.request(
            method=method.value,
            url=url,
            verify=not self.ignore_ssl_certificate_errors,
            json=json_data,
        )
        if self.log_http_code:
            logger.info(f"Status Code: {res.status_code}", stacklevel=stacklevel)

        if res.status_code >= 400:
            logger.info(f"response.text = {res.text}", stacklevel=stacklevel)
        elif log_response_data:
            if not res.content or json.dumps(res.json()) is None:
                logger.info(f"response.text = {res.text}", stacklevel=stacklevel)
            else:
                logger.info(
                    f"response.json = {json.dumps(res.json())}", stacklevel=stacklevel
                )

        logger.info("-" * 10, stacklevel=stacklevel)
        return res

    def token(self) -> str:
        return self.__token

    def cookie(self) -> str:
        return self.__cookie

    def headers(self) -> dict:
        return {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.__token,
            "Cookie": self.__cookie,
        }
