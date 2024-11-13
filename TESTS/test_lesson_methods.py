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
    step_text_3 = OnlineStep(id=step_text.id)

    assert step_text.info() == step_text_2.info() == step_text_3.info()

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
    step_quiz_3 = OnlineStep(id=step_quiz.id)

    assert step_quiz.info() == step_quiz_2.info() == step_quiz_3.info()

    lesson.delete_step(-1)

    assert lesson.get_steps_ids() == STEP_IDS


def test_StepNumber():
    lesson = OnlineLesson(id=LESSON_ID)

    step_number = OnlineStep(
        StepNumber(
            text="Сколько будет 3*4?",
            lesson_id=LESSON_ID,
            cost=2,
            position=10,
            answer=12,
        )
    )
    lesson.add_step(step_number)

    step_number_2 = OnlineStep(id=lesson.get_steps_ids()[-1])
    step_number_3 = OnlineStep(id=step_number.id)

    assert step_number.info() == step_number_2.info() == step_number_3.info()

    lesson.delete_step(-1)

    assert lesson.get_steps_ids() == STEP_IDS


def test_StepString():
    lesson = OnlineLesson(id=LESSON_ID)

    step_string = OnlineStep(
        StepString(
            text="Как называется эта платформа?",
            cost=1,
            lesson_id=LESSON_ID,
            position=10,
            answer="Stepik",
            case_sensitive=False,
        )
    )
    lesson.add_step(step_string)

    step_string_2 = OnlineStep(id=lesson.get_steps_ids()[-1])
    step_string_3 = OnlineStep(id=step_string.id)

    assert step_string.info() == step_string_2.info() == step_string_3.info()

    lesson.delete_step(-1)

    assert lesson.get_steps_ids() == STEP_IDS


def test_StepTask():
    lesson = OnlineLesson(id=LESSON_ID)

    step_task = OnlineStep(
        StepTask(
            text="Напишите программу, которая считывает 2 числа и выводит сначала их произведение, а потом сумму. Вывести через пробел",
            cost=10,
            lesson_id=LESSON_ID,
            position=10,
            test_cases=[
                TaskTest("1 5\n", "5 6\n"),
                TaskTest("-1 1\n", "-1 0\n"),
                TaskTest("10 0\n", "0 10\n"),
                TaskTest("5 8\n", "40 13\n"),
            ],
            samples_count=1,
        )
    )
    lesson.add_step(step_task)

    step_task_2 = OnlineStep(id=lesson.get_steps_ids()[-1])
    step_task_3 = OnlineStep(id=step_task.id)

    # Здесь нужно несколько раз делать GET запрос, так как Stepik'у нужно некоторое время, чтобы добавить задачу на программирование
    info = step_task.info()
    while True:
        if info["steps"][0]["status"] == "ready":
            break
        info = step_task.info()

    assert step_task_2.info() == step_task_3.info() == step_task.info()

    lesson.delete_step(-1)

    assert lesson.get_steps_ids() == STEP_IDS
