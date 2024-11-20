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
@click.option("--all", is_flag=True, help="Обновляет все уроки в каждом модуле")
def toc(filename, update, all):
    """Считывает toc-файл и обновляет курс (может обновлять урок или всю секцию)"""
    if all and update:
        raise click.UsageError("Вы должны использовать либо опцию --all, либо опцию -d")

    data: dict = None
    with open(filename, encoding="utf-8") as file:
        data = yaml.load(file, yaml.SafeLoader)

    title = data["title"]
    course_id = data["course_id"]
    base_dir = data["base_dir"]

    if all:
        ...  # Будет парс всех md-файлов и обновлены все уроки из каждого модуля

    elif update:
        section, lesson = str(update).split(".")

        for elem in data["toc"]:
            s, l = str(elem).split(".")

            if lesson:
                if section == s and lesson == l:
                    ...  # Будет вызван парс файла и обновлен урок
                    break
            else:
                if section == s:
                    ...  # Будет вызван парс всех файлов из модуля с номером section и обновлены все уроки модуля


@cli.command()
@click.argument(
    "filename",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
)
@click.option(
    "--step",
    "-s",
    type=click.IntRange(1, 16),
    help="Номер шага для обновления",
)
@click.option("--all", is_flag=True, help="Обновляет все шаги в уроке")
def lesson(filename, step, all):
    """Считывает файл и обновляет какой-то шаг или целый урок"""

    if all and step:
        raise click.UsageError("Вы должны использовать либо опцию --id, либо опцию -s")

    if all:
        ...  # Будет вызван парс файла и обновлены все шаги в уроке
    elif step:
        ...  # Будет вызван парс файла и обновлен только шаг с номером step


if __name__ == "__main__":
    cli()
