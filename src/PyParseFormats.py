import pyparsing as pp
import markdown as md

# WARNING: pyparsing can cause errors with encodings (unicode) ----------------------------------------------------- !!!
import re

from pyparsing import ParserElement, Regex


def md_to_html(md_text: list[str] | str):
    if isinstance(md_text, list):
        md_text = "\n".join(md_text)
    return md.markdown(md_text, extensions=['extra'])


class HiddenFormats:

    @staticmethod
    def _to_bool(toks: pp.ParseResults):
        tok_lst = toks.asList()
        for i in range(len(tok_lst)):
            if tok_lst[i] == HiddenFormats._true:
                tok_lst[i] = True
            elif tok_lst[i] == HiddenFormats._false:
                tok_lst[i] = False
            else:
                tok_lst[i] = None
        return tok_lst

    @staticmethod
    def _to_int(toks: pp.ParseResults):
        tok_list = toks.asList()
        for i in range(len(tok_list)):
            if tok_list[i] == HiddenFormats._int_format:
                tok_list[i] = int(tok_list[i])
        return tok_list

    @staticmethod
    def _return_emtpy_string(toks: pp.ParseResults):
        tok_list = toks.asList()
        tok_list.append("")
        return tok_list

    _unexpected = pp.SkipTo(pp.LineEnd(), include=True)("Unexpected_string")
    _del_spaces = pp.Suppress(pp.White())
    _safe_del_spaces = pp.Optional(_del_spaces)
    _rest_of_token = pp.SkipTo(pp.StringEnd(), include=True)

    _upper_letter = pp.Char("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    _pos_int_format = pp.Word(pp.nums)
    _int_format = pp.Combine(pp.Optional("-") + _pos_int_format)
    _pos_integer = _pos_int_format.copy().setParseAction(_to_int)
    _integer = _int_format.copy().setParseAction(_to_int)
    _float_number = pp.Combine(_int_format + "," + _pos_int_format)
    _true = pp.Keyword("TRUE", caseless=True)
    _false = pp.Keyword("FALSE", caseless=True)
    _bool = pp.Or((_true, _false)).setParseAction(_to_bool)

    _t_default = pp.Empty().setParseAction(_return_emtpy_string)  # TODO: fix, so == to other types
    _t_text = pp.Keyword("TEXT")
    _t_string = pp.Keyword("STRING")
    _t_number = pp.Keyword("NUMBER")
    _t_quiz = pp.Keyword("QUIZ")

    _st_type = pp.Or((_t_text, _t_string, _t_number, _t_quiz))

    _AIKEN_option = pp.Combine(_upper_letter + pp.Suppress(pp.Char(".)")))
    _ans = pp.Literal("ANSWER:")
    _shuff = pp.Literal("SHUFFLE:")
    _h1 = pp.Keyword("#")
    _h2 = pp.Keyword("##")

    # ==================================================================================================================
    # format_string_answer     -> [("ANSWER:", *line_of_text*), {'answer': *line_of_text*}]
    f_str_ans = _ans + _del_spaces + (pp.restOfLine())("answer")

    # format_number_answer     -> [("ANSWER:", *number*, *number*), {'answer': *number*, 'error': *number* or None})]
    f_num_ans = _ans + _float_number("answer") + pp.Optional(pp.Suppress("±") + _float_number)("adm_err")

    # format_quiz_answer
    f_quiz_ans = _ans + (_upper_letter + pp.ZeroOrMore(pp.Suppress(",") + _upper_letter))("answer")

    # format_quiz_shuffle
    f_quiz_shuff = _shuff + _bool("do_shuffle")

    # format_reg_exp           -> [("ANSWER:", *line_of_text*), {'answer': *line_of_text*}]
    f_regexp = pp.Literal("REGEXP:") + _del_spaces + (pp.restOfLine())("reg_exp")

    # format_lesson_id         -> [("lesson", "=", *number*) {'lesson': *number*}]
    f_les_id = pp.Literal("lesson") + "=" + _pos_integer("lesson_id")
    # ------------------------------------------------------------------------------------------------------------------
    # format_lesson_name       -> [("#", *line_of_text*), {'lesson_name': *line_of_text*}]
    f_les_name = _h1 + _del_spaces + (pp.restOfLine())("lesson_name")

    # format_step_name         -> [("##", *line_of_text*), {'step_name': *line_of_text*}]
    f_st_name = _h2 + _del_spaces + pp.Or([_st_type("type") + _del_spaces, _t_default("type")])
    f_st_name = f_st_name + _rest_of_token("step_name")

    # format_step_string_name  -> [("##", "STRING", *line_of_text*), {step_name: *line_of_text*}]
    f_st_str_name = _h2 + _t_string("type") + _del_spaces + (pp.restOfLine())("step_name")

    # format_step_number_name  -> [("##", "NUMBER", *line_of_text*), {step_name: *line_of_text*}]
    f_st_num_name = _h2 + _t_number("type") + _del_spaces + (pp.restOfLine())("step_name")

    # format_step_quiz_name    -> [("##", "QUIZ", *line_of_text*), {step_name: *line_of_text*}]
    f_st_quiz_name = _h2 + _t_quiz("type") + _del_spaces + (pp.restOfLine())("step_name")
    # ------------------------------------------------------------------------------------------------------------------
    # format_text_begin
    f_t_beg = pp.Keyword("TEXTBEGIN") + _safe_del_spaces + pp.restOfLine()("text")
    # format_text_end
    f_t_end = pp.Keyword("TEXTEND")
    # format_quiz_option
    f_quiz_opt = _AIKEN_option("letter") + _safe_del_spaces + pp.restOfLine()("text")
    # format


format_text_begin = HiddenFormats.f_t_beg
''' After parsing: \n
ParseResults( [ "TEXTBEGIN", *line_of_text* ], { 'text': *line_of_text* }, ) '''
format_text_end = HiddenFormats.f_t_end
''' After parsing: \n
ParseResults( [ "TEXTEND" ], {}, ) '''
format_quiz_option = HiddenFormats.f_quiz_opt
'''After parsing: \n
ParseResults( [ *AIKEN_option*, *line_of_text* ],
{ 'letter': *AIKEN_option*, 'text': *line_of_text* }, ) '''

format_string_answer = HiddenFormats.f_str_ans
'''After parsing: \n
ParseResults( [ "ANSWER:", *line_of_text* ], { 'answer': *line_of_text* } )'''
format_reg_exp = HiddenFormats.f_regexp
'''After parsing: \n
ParseResults( [ "REGEXP:", *line_of_text* ], { 'reg_exp': *line_of_text* } )'''
format_number_answer = HiddenFormats.f_num_ans
'''After parsing: \n
ParseResults( [ "ANSWER:", *float_number_1*, *float_number2* ],
{ 'answer': *float_number1*, 'adm_err': *float_number_2* } )'''
format_quiz_answer = HiddenFormats.f_quiz_ans
'''After parsing: \n
ParseResults( [ "ANSWER:", *arr_of_letters* ], { 'answer': *arr_of_letters* } )'''
format_quiz_shuffle = HiddenFormats.f_quiz_shuff
'''After parsing: \n
ParseResults( [ "SHUFFLE:", *bool* ], { 'do_shuffle': *bool* } )'''
format_lesson_id = HiddenFormats.f_les_id
'''After parsing: \n
ParseResults( [ "lesson", "=", *pos_integer* ], { 'lesson_id': *pos_integer* } )'''

format_lesson_name = HiddenFormats.f_les_name
'''After parsing: \n
ParseResults( [ "#", *line_of_text* ], { 'lesson_name': *line_of_text* } )'''
format_step_name = HiddenFormats.f_st_name
'''After parsing: \n
ParseResults( [ "##", *step_type*, *line_of_text* ], 
{ 'type': *step_type*, 'step_name': *line_of_text* } )'''


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
    _to_line = _to_line % len(text) if 0 > _to_line >= -len(text) else _to_line
    _to_line = min(len(text), _to_line)

    ans: list[tuple[pp.ParseResults, int, int, int]] = []
    for line_i in range(_from_line, _to_line):
        if _from_start:
            try:
                res = ((parse_exp.parse_string(text[line_i]), 0, len(text[line_i])),)
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
    try:
        _ = parse_exp.parse_string(text)
        result = True
    except Exception:
        result = False
    return result


def find_format(text: str, parse_exp: pp.ParserElement, _from_start: bool = False, _amount: int = 1) -> tuple:
    # TODO: add _from_start
    match = tuple(parse_exp.scan_string(text, max_matches=_amount))
    return match


def match_format(text: str, parse_exp: pp.ParserElement, _match_all: bool = False) -> pp.ParseResults:
    try:
        match = parse_exp.parseString(text, parse_all=_match_all)
        return match
    except Exception:
        return pp.ParseResults([])

# def match_format(text: str, parse_exp):
#    pass
