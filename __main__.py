from src.Parse_Classes.OnlineTokens import OnlineStep, OnlineLesson

from src.Parse_Classes.PageParsers import *
from src.StepikAPI.stepik_api import StepikAPI, LoggedSession
import json, requests, yaml


def main():
    client_id, client_secret = None, None

    try:
        with open("cred.yaml") as file:
            s = yaml.load(file, yaml.SafeLoader)
            client_id = s["client_id"]
            client_secret = s["client_secret"]

    except FileExistsError:
        print('File "cred.yaml" does not exist!')

    except KeyError:
        print('There are no variables "client_id" or "client_secret"!')

    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
