import click
import yaml


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

    title = data["title"]
    course_id = data["course_id"]
    base_dir = data["base_dir"]

    if all:
        ...  # Будет парс всех md-файлов и обновлены все уроки из каждого модуля

    elif update:
        if update - int(update):
            if update not in data["toc"]:
                raise KeyError(f"Урок {update} не существует!")

            lesson_data = data["toc"][update]
            ...  # Будет вызван парс всех файлов из модуля с номером section и обновлены все уроки модуля
        else:
            lessons = list(filter(lambda elem: int(elem) == update, data["toc"]))

            if lessons:
                for lesson in lessons:
                    lesson_data = data["toc"][lesson]
                    ...  # Будет вызван парс файла и обновлен урок
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

    if step and id or step and all or id and all:
        raise click.UsageError(
            "Вы должны использовать либо опцию -s, либо опцию --id, либо опцию --all"
        )

    if all:
        ...  # Будет вызван парс файла и обновлены все шаги в уроке
    elif step:
        ...  # Будет вызван парс файла и обновлен шаг с номером step
    elif id:
        ...  # Будет вызван парс файла и обновлен урок с lesson_id равным id
    else:
        raise click.UsageError("Вы должны одну из опций: -s, --all или --id")


if __name__ == "__main__":
    cli()
