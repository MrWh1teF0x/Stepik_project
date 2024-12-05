import pyparsing as pp
import markdown as md

# WARNING: pyparsing can cause errors with encodings (unicode) ----------------------------------------------------- !!!
import re


def md_to_html(md_text: list[str] | str):
    if isinstance(md_text, list):
        md_text = "\n".join(md_text)
    return md.markdown(md_text, extensions=['extra'])


class HiddenFormats:
    _unexpected = pp.SkipTo(pp.LineEnd(), include=True)("Unexpected_string")
    _del_spaces = pp.Suppress(pp.White())
    _h1 = pp.Keyword("#")
    _h2 = pp.Keyword("##")
    # ------------------------------------------------------------------------------------------------------------------
    # format_answer            -> [("ANSWER:", *line_of_text*), {'answer': *line_of_text*}]
    f_ans = pp.Literal("ANSWER:") + _del_spaces + (pp.restOfLine())("answer")
    _float_number = pp.Combine(pp.Optional("-") + pp.Word(pp.nums) + "," + pp.Word(pp.nums))
    _ans = pp.Literal("ANSWER:")
    # format_number_answer     -> [("ANSWER:", *number*, *number*), {'answer': *number*, 'error': *number* or None})]
    f_num_ans = _ans + _float_number("answer") + pp.Optional(pp.Suppress("±") + _float_number)("adm_err")


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

    # format_step_number_name  -> [("##", "NUMBER", *line_of_text*), {step_name: *line_of_text*}]
    f_st_num_name = _h2 + pp.Keyword("NUMBER") + _del_spaces + (pp.restOfLine())("step_name")

format_reg_exp = 0
format_string_answer = HiddenFormats.f_str_ans
'''**]==parse==>** [ ("ANSWER:", *line_of_text*), {'answer': *line_of_text*} ]'''
format_number_answer = HiddenFormats.f_num_ans
format_lesson_id = HiddenFormats.f_les_id

format_lesson_name = HiddenFormats.f_les_name
format_step_name = HiddenFormats.f_st_name
format_step_text_name = HiddenFormats.f_st_t_name
format_step_string_name = HiddenFormats.f_st_str_name
format_step_number_name = HiddenFormats.f_st_num_name


def search_format_in_text(
        text: list[str],
        parse_exp: pp.ParserElement,
        _from_line: int | None = None,
        _to_line: int | None = None,
        _amount: int = -1,
        _from_start: bool = False, ) -> list[tuple[pp.ParseResults, int, int, int]]:
    """Returns: tuple[ParseResults, line_index, start_index_in_line, end_index_in_line].

    - ``_from_line`` index of line to search from (works like with slices).
    - ``_to_line`` index of line to end your search (works like with slices).
    - ``_amount`` how many tokens to search for (if _amount < 0, then search for all inclusions).
    - ``_from_start`` if True: will be searching for token from the start of a line.
    """
    if _amount == 0:
        return []

    _from_line = 0 if _from_line is None else _from_line
    _from_line = _from_line % len(text) if _from_line >= -len(text) else _from_line
    _from_line = max(_from_line, 0)

    _to_line = len(text) if _to_line is None else _to_line
    _to_line = _to_line % len(text) if _to_line >= -len(text) else _to_line
    _to_line = min(len(text), _to_line)

    ans: list[tuple[pp.ParseResults, int, int, int]] = []
    for line_i in range(_from_line, _to_line):
        if _from_start:
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
                _amount -= 1
                if _amount == 0:
                    break

    return ans


def check_format(text: str, parse_exp: pp.ParserElement, _from_start: bool = False) -> bool:
    if _from_start:
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


def match_format(text: str, parse_exp: pp.ParserElement) -> pp.ParseResults:
    match = parse_exp.runTests(text, comment=None, printResults=False)
    if match[0]:
        return match[1][0][1]

# def match_format(text: str, parse_exp):
#    pass
