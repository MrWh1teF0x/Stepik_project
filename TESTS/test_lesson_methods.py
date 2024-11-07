from src.stepik_api.online_tokens import *
from src.stepik_api.types_of_step import *
from src.stepik_api.logged_session import init_secret_fields, setup_logger
import pytest

setup_logger(1, 1)
init_secret_fields()

LESSON_ID = 1432805
STEP_IDS = [
    6166762,
    6165951,
    6166824,
    6170935,
    6205521,
    6203087,
    6203240,
    6203784,
    6204084,
]


def test_get_steps_ids():
    lesson = OnlineLesson(id=LESSON_ID)
    assert lesson.get_steps_ids() == STEP_IDS


def test_StepText():
    lesson = OnlineLesson(id=LESSON_ID)

    step_text = OnlineStep(
        StepText(
            text="Этот шаг был создан с помощью теста!",
            lesson_id=LESSON_ID,
            position=10,
        )
    )
    lesson.add_step(step_text)
    step_text_2 = OnlineStep(id=lesson.get_steps_ids()[-1])

    assert step_text_2.info() == step_text.info()

    lesson.delete_step(-1)

    assert lesson.get_steps_ids() == STEP_IDS


def test_StepQuiz():
    lesson = OnlineLesson(id=LESSON_ID)

    step_quiz = OnlineStep(
        StepQuiz(
            text="Сколько будет 5+3?",
            lesson_id=LESSON_ID,
            position=10,
            cost=5,
            answers=[
                Answer(text="3", is_correct=False),
                Answer(text="8", is_correct=True),
                Answer(text="1", is_correct=False),
                Answer(text="7", is_correct=False),
            ],
            is_multiple_choice=False,
        )
    )
    lesson.add_step(step_quiz)
    step_quiz_2 = OnlineStep(id=lesson.get_steps_ids()[-1])

    assert step_quiz_2.info() == step_quiz.info()

    lesson.delete_step(-1)

    assert lesson.get_steps_ids() == STEP_IDS
