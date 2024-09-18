import re

format_lesson_id = re.compile(r"^lesson\s=\s[0-9]+")
format_lesson_name = re.compile(r"^#\s.+")


def check_format(text: str, reg_exp: re.Pattern) -> tuple:
    match: re.Match = reg_exp.search(text)
    if match is not None:
        return match.span()
    return ()
