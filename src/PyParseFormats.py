import pyparsing as pp

# WARNING: pyparsing can cause errors with language coding (unicode) ----------------------------------------------- !!!
import re


class HiddenFormats:
    _unexpected = pp.SkipTo(pp.LineEnd(), include=True)("Unexpected_string")
    _hash_symb = pp.Literal("#")
    # ------------------------------------------------------------------------------------------------------------------
    # format_lesson_id      -> [("lesson", "=", *number*) {'lesson': *number*}]
    f_les_id = pp.Literal("lesson") + "=" + pp.Word(pp.nums)("lesson_id")
    # format_lesson_name    -> [("#", *line_of_text*), {lesson_name: *line_of_text*}]
    f_les_name = (
        pp.Keyword("#") + pp.Suppress(pp.White()) + (pp.restOfLine())("lesson_name")
    )
    # format_step_name      -> [("##", *line_of_text*), {step_name: *line_of_text*}]
    f_st_name = (
        pp.Keyword("##") + pp.Suppress(pp.White()) + (pp.restOfLine())("step_name")
    )
    # format_steptext_name  -> [("##", "TEXT", *line_of_text*), {step_name: *line_of_text*}]
    f_st_t_name = pp.Keyword("##") + pp.Keyword("TEXT") + (pp.restOfLine())("step_name")


format_lesson_id = HiddenFormats.f_les_id
format_lesson_name = HiddenFormats.f_les_name
format_step_name = HiddenFormats.f_st_name
format_steptext = HiddenFormats.f_st_t_name


def search_format_in_text(
    text: list[str], parse_exp: pp.ParserElement, max_amount: int = -1
):
    """returns tuple(ParseResults, line_index, start_index_in_line, end_index_in_line).
    if max_amount < 0, that means we search all inclusions of format"""
    if max_amount == 0:
        return ()

    ans = []
    for line_i in range(len(text)):

        res = tuple(parse_exp.scanString(text[line_i]))
        if res != ():
            for l_res in res:
                ans.append(
                    (l_res[0], line_i, l_res[1], l_res[2])
                )  # (ParseRes(), line_i, token_start, token_end)
                max_amount -= 1
                if max_amount == 0:
                    break

    return ans


def check_format(
    text: str, parse_exp: pp.ParserElement, from_start: bool = False
) -> bool:
    result = parse_exp.runTests(text, comment=None, printResults=False)
    return result[0]


def find_format(text: str, parse_exp: pp.ParserElement) -> tuple:
    match = tuple(parse_exp.scanString(text))
    return match


# def match_format(text: str, parse_exp):
#    pass
