import pyparsing as pp
# WARNING: pyparsing can cause errors with language coding (unicode) ----------------------------------------------- !!!
import re


class HiddenFormats:
    _unexpected = pp.SkipTo(pp.LineEnd(), include=True)("Unexpected_string")
    _hash_symb = pp.Literal('#')
    # ------------------------------------------------------------------------------------------------------------------
    # format_lesson_id      -> [("lesson", "=", *number*) {'lesson': *number*}]
    f_les_id = pp.Literal("lesson") + "=" + pp.Word(pp.nums)("lesson")
    # format_lesson_name    -> [("#", *line_of_text*), {lesson_name: *line_of_text*}]
    f_les_name = pp.Keyword("#") + pp.Suppress(pp.White()) + (pp.restOfLine())("lesson_name")
    # format_step_name      -> [("##", *line_of_text*), {step_name: *line_of_text*}]
    f_st_name = pp.Keyword("##") + pp.Suppress(pp.White()) + (pp.restOfLine())("step_name")


format_lesson_id = HiddenFormats.f_les_id
format_lesson_name = HiddenFormats.f_les_name
format_step_name = HiddenFormats.f_st_name


def check_format(text: str, parse_exp: pp.ParserElement) -> bool:
    result = parse_exp.runTests(text, comment=None, printResults=False)
    return result[0]


def find_format(text: str, parse_exp: pp.ParserElement) -> tuple:
    match = tuple(parse_exp.scanString(text))
    return match


def match_format(text: str, parse_exp):
    pass


"""
a_res = format_lesson_id.parseString("lesson = 123")
# нужен тест на пробелы
print(f"{a_res=}")
b_res = format_lesson_name.parseString("#    Lesson 1      ")
print(f"{b_res=}")
c_res = format_step_name.parseString("##\t\t\t dq21eoi1 231o231238")
print(f"{c_res=}")
print()

a = format_lesson_id.runTests("lesson = 123", printResults=False)
print(a)
b = format_lesson_name.runTests("#    Lesson 1      ", comment=None, printResults=False)
print(b)


match_b = list(format_lesson_name.scanString("# lesson 1 \n # 123123123"))
print(f"{match_b}")
"""