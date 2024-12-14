import click
import yaml
from src.Parse_Classes.LessonParsers import Lesson
from src.Parse_Classes.StepParsers import *
from src.stepik_api.online_tokens import *
from src.stepik_api.logged_session import *


def update_lesson(file: str, lesson_id, step_number: int = None) -> None:
    lesson = Lesson(file)
    lesson.parse()
    if lesson_id is None:
        if lesson.id == -1:
            raise AttributeError("Id of lesson is unknown!")
        lesson_id = lesson.id

    online_steps: list[OnlineStep] = []
    for i, step in enumerate(lesson.steps):
        step.lesson_id = lesson_id
        step.position = i
        online_steps.append(OnlineStep(step))

    online_lesson = OnlineLesson(id=lesson_id)
    if step_number is None:
        online_lesson.update(online_steps)
    else:
        online_lesson.steps[step_number - 1].update(
            online_steps[step_number - 1].step_data
        )


@click.group()
def cli():
    pass


@cli.command()
@click.argument(
    "filename",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
)
@click.option(
    "--update", "-d", type=click.FLOAT, help="Обновляет какой-то урок или целую секцию"
)
@click.option(
    "--step",
    "-s",
    type=click.INT,
    help="Номер шага для обновления",
)
@click.option("--all", is_flag=True, help="Обновляет все уроки в каждом модуле")
def toc(filename, update, all, step):
    """Считывает toc-файл и обновляет курс (может обновлять урок или всю секцию)"""
    if all and update or all and step:
        raise click.UsageError(
            "Вы должны использовать либо опцию --all, либо опцию -d, либо опции -d и -s вместе"
        )
    if step and not (update and update - int(update)):
        raise click.UsageError(
            "Вы должны использовать -d (номер модуля или урока) или -d (номер урока) -s (номер шага)"
        )

    data: dict = None
    with open(filename, encoding="utf-8") as file:
        data = yaml.load(file, yaml.SafeLoader)

    course_id = data["course_id"]
    lessons = data["toc"]
    lesson_id = None

    if all:
        for lesson in lessons:
            if "lesson_id" in data["toc"][lesson]:
                lesson_id = data["toc"][lesson]["lesson_id"]
            update_lesson(data["toc"][lesson]["path"], lesson_id)
            lesson_id = None

    elif update:
        if update - int(update):
            if update not in data["toc"]:
                raise KeyError(f"Урок {update} не существует!")

            if "lesson_id" in data["toc"][update]:
                lesson_id = data["toc"][update]["lesson_id"]
            update_lesson(lessons[update]["path"], lesson_id, step)

        else:
            lessons_of_section = list(
                filter(lambda elem: int(elem) == update, data["toc"])
            )

            if lessons_of_section:
                for lesson in lessons_of_section:
                    if "lesson_id" in data["toc"][lesson]:
                        lesson_id = data["toc"][lesson]["lesson_id"]
                    update_lesson(data["toc"][lesson]["path"], lesson_id)
                    lesson_id = None
            else:
                raise KeyError(f"Модуль {int(update)} не существует!")
    else:
        raise click.UsageError("Вы должны одну из опций: --all или -d")


@cli.command()
@click.argument(
    "filename",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
)
@click.option(
    "--step",
    "-s",
    type=click.INT,
    help="Номер шага для обновления",
)
@click.option(
    "--id", type=click.INT, help="Обновляет все шаги в уроке с lesson_id равным id"
)
@click.option("--all", is_flag=True, help="Обновляет все шаги в уроке")
def lesson(filename, step, id, all):
    """Считывает файл и обновляет какой-то шаг или целый урок"""

    if step and all:
        raise click.UsageError(
            "Вы должны использовать либо опцию -s, либо опцию --id, либо опцию --all"
        )

    if all:
        update_lesson(filename, id)
    elif step:
        update_lesson(filename, id, step)
    else:
        raise click.UsageError("Вы должны одну из опций: -s или --all")


def main():
    setup_logger(1, 1)
    init_secret_fields()


if __name__ == "__main__":
    main()
    cli()
