from src.stepik_api.online_tokens import *
from src.stepik_api.types_of_step import *
from src.stepik_api.logged_session import init_secret_fields, setup_logger
import pytest

setup_logger(1, 1)
init_secret_fields()

LESSON_ID = 1432805
STEP_IDS = [6166762, 6165951, 6166824, 6170935, 6170948]


def test_get_steps_ids():
    lesson = OnlineLesson(id=LESSON_ID)
    assert lesson.get_steps_ids() == STEP_IDS
