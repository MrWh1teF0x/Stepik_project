import pyparsing as pp

# WARNING: pyparsing can cause errors with encodings (unicode) ----------------------------------------------------- !!!
import re


class HiddenFormats:
    _unexpected = pp.SkipTo(pp.LineEnd(), include=True)("Unexpected_string")
    _del_spaces = pp.Suppress(pp.White())
    _h1 = pp.Keyword("#")
    _h2 = pp.Keyword("##")
    # ------------------------------------------------------------------------------------------------------------------
    # format_answer            -> [("ANSWER:", *line_of_text*), {'answer': *line_of_text*}]
    f_ans = pp.Literal("ANSWER:") + _del_spaces + (pp.restOfLine())("answer")

    # format_reg_exp           -> [("ANSWER:", *line_of_text*), {'answer': *line_of_text*}]
    f_regexp = pp.Literal("REGEXP:") + _del_spaces + (pp.restOfLine())("answer")

    # format_lesson_id         -> [("lesson", "=", *number*) {'lesson': *number*}]
    f_les_id = pp.Literal("lesson") + "=" + pp.Word(pp.nums)("lesson_id")
    # ------------------------------------------------------------------------------------------------------------------
    # format_lesson_name       -> [("#", *line_of_text*), {'lesson_name': *line_of_text*}]
    f_les_name = _h1 + _del_spaces + (pp.restOfLine())("lesson_name")

    # format_step_name         -> [("##", *line_of_text*), {'step_name': *line_of_text*}]
    f_st_name = _h2 + _del_spaces + (pp.restOfLine())("step_name")

    # format_step_text_name    -> [("##", "TEXT", *line_of_text*), {'step_name': *line_of_text*}]
    f_st_t_name = _h2 + pp.Keyword("TEXT") + _del_spaces + (pp.restOfLine())("step_name")

    # format_step_string_name  -> [("##", "STRING", *line_of_text*), {step_name: *line_of_text*}]
    f_st_str_name = _h2 + pp.Keyword("STRING") + _del_spaces + (pp.restOfLine())("step_name")


format_answer = HiddenFormats.f_ans
format_reg_exp = 0
format_lesson_id = HiddenFormats.f_les_id

format_lesson_name = HiddenFormats.f_les_name
format_step_name = HiddenFormats.f_st_name
format_step_text_name = HiddenFormats.f_st_t_name
format_step_string_name = HiddenFormats.f_st_str_name



def search_format_in_text(
        text: list[str],
        parse_exp: pp.ParserElement,
        max_amount: int = -1,
        from_start: bool = False
):
    """returns tuple(ParseResults, line_index, start_index_in_line, end_index_in_line).
    if max_amount < 0, that means we search all inclusions of format"""
    if max_amount == 0:
        return ()

    ans = []
    for line_i in range(len(text)):

        if from_start:
            try:
                res = ((parse_exp.parseString(text[line_i]), 0, len(text[line_i])),)
                # TODO: add a way to find end of token in line
            except Exception:
                res = ()
        else:
            res = tuple(parse_exp.scan_string(text[line_i]))

        if res != ():
            for l_res in res:
                ans.append(
                    (l_res[0], line_i, l_res[1], l_res[2])
                )  # (ParseRes(), line_i, token_start, token_end)
                max_amount -= 1
                if max_amount == 0:
                    break

    return ans


def check_format(text: str, parse_exp: pp.ParserElement, from_start: bool = False) -> bool:
    if from_start:
        try:
            _ = parse_exp.parseString(text)
            result = True
        except Exception:
            result = False
    else:
        result = parse_exp.runTests(text, comment=None, printResults=False)[0]
    return result


def find_format(text: str, parse_exp: pp.ParserElement) -> tuple:
    match = tuple(parse_exp.scanString(text))
    return match


def match_format(text: str, parse_exp: pp.ParserElement):
    match = parse_exp.runTests(text, comment=None, printResults=False)
    if match[0]:
        return pp.ParseResults(match[1][0][1])

# def match_format(text: str, parse_exp):
#    pass
