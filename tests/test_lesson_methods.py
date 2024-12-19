import pytest

from time import sleep
from src.stepik_api.online_tokens import *
from src.parse_classes.step_parsers import *
from src.stepik_api.logged_session import init_secret_fields, setup_logger

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
    6428822,
    6278724,
]


def wait_ready(step: OnlineStep):
    info = step.info()
    while True:
        if info["steps"][0]["status"] == "ready":
            break
        sleep(1)
        info = step.info()

    return info


def test_get_steps_ids():
    lesson = OnlineLesson(id=LESSON_ID)
    assert lesson.get_steps_ids() == STEP_IDS


def test_StepText():
    lesson = OnlineLesson(id=LESSON_ID)

    position = 4

    step_text = OnlineStep(
        StepText(
            text="Этот шаг был создан с помощью теста!",
            lesson_id=LESSON_ID,
            position=position,
        )
    )
    lesson.add_step(step_text)

    step_text_2 = OnlineStep(id=lesson.get_steps_ids()[position])
    step_text_3 = OnlineStep(id=step_text.id)

    assert wait_ready(step_text) == step_text_2.info() == step_text_3.info()

    lesson.delete_step(position + 1)

    assert lesson.get_steps_ids() == STEP_IDS


def test_StepQuiz():
    lesson = OnlineLesson(id=LESSON_ID)

    position = 2

    step_quiz = OnlineStep(
        StepQuiz(
            text="Сколько будет 5+3?",
            lesson_id=LESSON_ID,
            position=position,
            cost=5,
            answers=[
                ("3", False),
                ("8", True),
                ("1", False),
                ("7", False),
            ],
            is_multiple_choice=False,
        )
    )
    lesson.add_step(step_quiz)

    step_quiz_2 = OnlineStep(id=lesson.get_steps_ids()[position])
    step_quiz_3 = OnlineStep(id=step_quiz.id)

    assert wait_ready(step_quiz) == step_quiz_2.info() == step_quiz_3.info()

    lesson.delete_step(position + 1)

    assert lesson.get_steps_ids() == STEP_IDS


def test_StepNumber():
    lesson = OnlineLesson(id=LESSON_ID)

    position = 7

    step_number = OnlineStep(
        StepNumber(
            text="Сколько будет 3*4?",
            lesson_id=LESSON_ID,
            cost=2,
            position=position,
            answer=12,
        )
    )
    lesson.add_step(step_number)

    step_number_2 = OnlineStep(id=lesson.get_steps_ids()[position])
    step_number_3 = OnlineStep(id=step_number.id)

    assert wait_ready(step_number) == step_number_2.info() == step_number_3.info()

    lesson.delete_step(position + 1)

    assert lesson.get_steps_ids() == STEP_IDS


def test_StepString():
    lesson = OnlineLesson(id=LESSON_ID)

    position = 5

    step_string = OnlineStep(
        StepString(
            text="Как называется эта платформа?",
            cost=1,
            lesson_id=LESSON_ID,
            position=position,
            answer="Stepik",
            case_sensitive=False,
        )
    )
    lesson.add_step(step_string)

    step_string_2 = OnlineStep(id=lesson.get_steps_ids()[position])
    step_string_3 = OnlineStep(id=step_string.id)

    assert wait_ready(step_string) == step_string_2.info() == step_string_3.info()

    lesson.delete_step(position + 1)

    assert lesson.get_steps_ids() == STEP_IDS


def test_StepTask():
    lesson = OnlineLesson(id=LESSON_ID)

    position = 1

    step_task = OnlineStep(
        StepTask(
            text="Напишите программу, которая считывает 2 числа и выводит сначала их произведение, а потом сумму. Вывести через пробел",
            cost=10,
            lesson_id=LESSON_ID,
            position=position,
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

    step_task_2 = OnlineStep(id=lesson.get_steps_ids()[position])
    step_task_3 = OnlineStep(id=step_task.id)

    # Здесь нужно несколько раз делать GET запрос, так как Stepik'у нужно некоторое время, чтобы добавить задачу на программирование
    # info = step_task.info()
    # while True:
    #     if info["steps"][0]["status"] == "ready":
    #         break
    #     sleep(1)
    #     info = step_task.info()

    assert wait_ready(step_task) == step_task_2.info() == step_task_3.info()

    lesson.delete_step(position + 1)

    assert lesson.get_steps_ids() == STEP_IDS


def test_StepSort():
    lesson = OnlineLesson(id=LESSON_ID)

    position = 0

    step_sort = OnlineStep(
        StepSort(
            text="Расставь от самого маленького до самого большого животного.",
            cost=4,
            lesson_id=LESSON_ID,
            position=position,
            sorted_answers=["Мышь", "Собака", "Слон", "Синий кит"],
        )
    )
    lesson.add_step(step_sort)

    step_sort_2 = OnlineStep(id=lesson.get_steps_ids()[position])
    step_sort_3 = OnlineStep(id=step_sort.id)

    assert wait_ready(step_sort) == step_sort_2.info() == step_sort_3.info()

    lesson.delete_step(position + 1)

    assert lesson.get_steps_ids() == STEP_IDS


def test_StepMatch():
    lesson = OnlineLesson(id=LESSON_ID)

    position = 3

    step_match = OnlineStep(
        StepMatch(
            text="Расставь правильно вид и царство, к которому принадлежит вид",
            cost=4,
            lesson_id=LESSON_ID,
            position=position,
            pairs=[
                MatchPair("Опята", "Грибы"),
                MatchPair("Муравей", "Животные"),
                MatchPair("Шиповник", "Растения"),
                MatchPair("Инфузория туфелька", "Бактерии"),
            ],
        )
    )
    lesson.add_step(step_match)

    step_match_2 = OnlineStep(id=lesson.get_steps_ids()[position])
    step_match_3 = OnlineStep(id=step_match.id)

    assert wait_ready(step_match) == step_match_2.info() == step_match_3.info()

    lesson.delete_step(position + 1)

    assert lesson.get_steps_ids() == STEP_IDS


def test_StepFill():
    lesson = OnlineLesson(id=LESSON_ID)

    position = 8

    step_fill = OnlineStep(
        StepFill(
            cost=4,
            lesson_id=LESSON_ID,
            position=position,
            components=[
                BlankText(text="Висит груша, нельзя скушать. Что это?"),
                BlankInput(answers=[Answer("лампочка", is_correct=True)]),
                BlankText(text="Выбери животное, которое быстрее всех бегает."),
                BlankSelect(
                    answers=[
                        Answer(text="Гепард", is_correct=True),
                        Answer(text="Черепаха", is_correct=False),
                        Answer(text="Олень", is_correct=False),
                    ]
                ),
            ],
        )
    )
    lesson.add_step(step_fill)

    step_fill_2 = OnlineStep(id=lesson.get_steps_ids()[position])
    step_fill_3 = OnlineStep(id=step_fill.id)

    assert wait_ready(step_fill) == step_fill_2.info() == step_fill_3.info()

    lesson.delete_step(position + 1)

    assert lesson.get_steps_ids() == STEP_IDS


def test_StepTable():
    lesson = OnlineLesson(id=LESSON_ID)

    position = 6

    step_table = OnlineStep(
        StepTable(
            cost=4,
            lesson_id=LESSON_ID,
            position=position,
            description="Страны",
            table=Table(
                rows={
                    "Никарагуа": [False, False, False, False, True],
                    "Франция": [False, True, False, False, False],
                    "Германия": [False, False, False, True, False],
                    "Россия": [True, False, False, False, False],
                    "Япония": [False, False, True, False, False],
                },
                columns=["Москва", "Париж", "Токио", "Берлин", "Манагуа"],
            ),
        )
    )
    lesson.add_step(step_table)

    step_table_2 = OnlineStep(id=lesson.get_steps_ids()[position])
    step_table_3 = OnlineStep(id=step_table.id)

    assert wait_ready(step_table) == step_table_2.info() == step_table_3.info()

    lesson.delete_step(position + 1)

    assert lesson.get_steps_ids() == STEP_IDS
