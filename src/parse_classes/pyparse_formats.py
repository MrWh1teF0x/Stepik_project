import pyparsing as pp
import markdown as md
from markdown.preprocessors import Preprocessor
from markdown.extensions import Extension
import re

# WARNING: pyparsing can cause errors with encodings (unicode) ----------------------------------------------------- !!!
from pyparsing import ParserElement, Regex


# TO THE SOLUTION THANKS TO https://github.com/selcuk ===================================================
urlfinder = re.compile(r'((([A-Za-z]{3,9}:(?:\/\/)?)(?:[\-;:&=\+\$,\w]+@)?[A-Za-z0-9\.\-]+(:[0-9]+)?|'
                       r'(?:www\.|[\-;:&=\+\$,\w]+@)[A-Za-z0-9\.\-]+)((?:/[\+~%/\.\w\-_]*)?\??'
                       r'(?:[\-\+=&;%@\.\w_]*)#?(?:[\.!/\\\w]*))?)')


class URLify(Preprocessor):
    def run(self, lines):
        return [urlfinder.sub(r'<\1>', line) for line in lines]


class URLifyExtension(Extension):
    def extendMarkdown(self, md):
        md.preprocessors.register(URLify(md), 'urlify', 0)
# =======================================================================================================


def md_to_html(md_text: list[str] | str):
    #urlify_ext = URLifyExtension()
    if isinstance(md_text, list):
        md_text = "\n".join(md_text)
    extentions = ["extra"] #urlify_ext
    return md.markdown(md_text, extensions=extentions)


class HiddenFormats:
    _unexpected = pp.SkipTo(pp.LineEnd(), include=True)("Unexpected_string")
    _del_spaces = pp.Suppress(pp.White())
    _safe_del_spaces = pp.Optional(_del_spaces)
    _rest_of_string = pp.SkipTo(pp.StringEnd(), include=True)

# ------  types tokens  -----------------------------------------------------------------------------------------------
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

    _param_key = pp.Combine(pp.Word(pp.alphas + "_") + pp.ZeroOrMore(pp.Word(pp.alphanums + "_")))
    _param_val = pp.Combine(_safe_del_spaces + pp.SkipTo(pp.White() ^ pp.LineEnd(), include=False))

    _upper_letter = pp.Char("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    _AIKEN_option = pp.Combine(_upper_letter + pp.Suppress(pp.Char(".)")))

    _pos_int_format = pp.Word(pp.nums)
    _int_format = pp.Combine(pp.Optional("-") + _pos_int_format)
    _pos_integer = _pos_int_format.copy().setParseAction(_to_int)
    _integer = _int_format.copy().setParseAction(_to_int)
    _pos_float_number = pp.Combine(_pos_int_format + pp.Optional("." + _pos_int_format))
    _float_number = pp.Combine(_int_format + pp.Optional("." + _pos_int_format))

    _true = pp.Keyword("TRUE", caseless=True)
    _false = pp.Keyword("FALSE", caseless=True)
    _bool = pp.Or((_true, _false)).setParseAction(_to_bool)

# ------  step types  -------------------------------------------------------------------------------------------------
    @staticmethod
    def _return_emtpy_string(toks: pp.ParseResults):
        tok_list = toks.asList()
        tok_list.append("")
        return tok_list

    _t_default = pp.Empty().setParseAction(_return_emtpy_string)
    _t_text = pp.Keyword("TEXT")
    _t_string = pp.Keyword("STRING")
    _t_number = pp.Keyword("NUMBER")
    _t_quiz = pp.Keyword("QUIZ")
    # _t_task = pp.Keyword("TASK")
    _t_taskinline = pp.Keyword("TASKINLINE")

    _st_type = pp.Or((_t_text, _t_string, _t_number, _t_quiz, _t_taskinline))

# ------  section tokens  ---------------------------------------------------------------------------------------------
    _ans = pp.Combine(pp.Literal("ANSWER")("section_type") + ":")
    _reg_exp = pp.Combine(pp.Literal("REGEXP")("section_type") + ":")
    _shuff = pp.Combine(pp.Literal("SHUFFLE")("section_type") + ":")
    _t_begin = pp.Keyword("TEXTBEGIN")("section_type")
    _t_end = pp.Keyword("TEXTEND")("section_type")
    _code = pp.Keyword("CODE")("section_type")
    _pre_code = pp.Keyword("HEADER")("section_type")
    _post_code = pp.Keyword("FOOTER")("section_type")
    _code_tests = pp.Keyword("TEST")("section_type")
    _config = pp.Keyword("CONFIG")("section_type")
    _h1 = pp.Keyword("#")
    _h2 = pp.Keyword("##")

# ====== MAJOR FORMATS ================================================================================================
    # format_lesson_name  and  format_lesson_id
    f_les_name = _h1 + _del_spaces + _rest_of_string("lesson_name")
    f_les_id = pp.Literal("lesson") + "=" + _pos_integer("lesson_id")
    # format_step_name
    f_st_name = _h2 + _del_spaces + pp.Or([_st_type("type") + _del_spaces, _t_default("type")])
    f_st_name = f_st_name + _rest_of_string("step_name")
    # check formats
    f_config = _config + pp.StringEnd()
    f_test_data_sep = pp.Literal("----") + pp.StringEnd()
    f_test_sep = pp.Literal("====") + pp.StringEnd()
    # universal formats
    f_t_beg = _t_begin + _safe_del_spaces + _rest_of_string("text")
    f_t_end = _t_end + pp.StringEnd()

# ------  step sections  ----------------------------------------------------------------------------------------------
    # Step string
    f_str_ans = _ans + _safe_del_spaces + _rest_of_string("answer")
    f_str_regexp = _reg_exp + _del_spaces + _bool("reg_exp")
    f_str_sect = pp.Or([f_config, f_str_ans, f_str_regexp])

    # Step number
    f_num_ans = _ans + _float_number("answer") + pp.Optional(pp.Suppress("±") + _pos_float_number("adm_err"))
    f_num_sect = pp.Or([f_config, f_num_ans])

    # Step quiz
    f_quiz_ans = _ans + (_upper_letter + pp.ZeroOrMore(pp.Suppress(",") + _upper_letter))("answer")
    f_quiz_shuff = _shuff + _bool("do_shuffle")
    f_quiz_opt = _AIKEN_option("letter") + _safe_del_spaces + pp.restOfLine()("text")
    f_quiz_sect = pp.Or([f_config, f_t_beg, f_t_end, f_quiz_ans, f_quiz_shuff, f_quiz_opt])

    # Step task_in_line
    f_til_param = _param_key("parameter") + "=" + _param_val("value")
    f_til_code = _code + pp.StringEnd()
    f_til_pre_code = _pre_code + pp.StringEnd()
    f_til_post_code = _post_code + pp.StringEnd()
    f_til_test = _code_tests + pp.StringEnd()
    f_til_sect = pp.Or([f_config, f_til_code,
                        f_til_pre_code, f_til_post_code, f_til_test])


format_lesson_name = HiddenFormats.f_les_name
'''After parsing: \n
ParseResults( [ "#", *line_of_text* ], { 'lesson_name': *line_of_text* } )'''
format_lesson_id = HiddenFormats.f_les_id
'''After parsing: \n
ParseResults( [ "lesson", "=", *pos_integer* ], { 'lesson_id': *pos_integer* } )'''
format_step_name = HiddenFormats.f_st_name
'''After parsing: \n
ParseResults( [ "##", *step_type*, *line_of_text* ], 
{ 'type': *step_type*, 'step_name': *line_of_text* } )'''
format_config = HiddenFormats.f_config
'''Simple parse, if format: \n
ParseResults( [ "CONFIG" ], {} )'''
format_test_data_seperator = HiddenFormats.f_test_data_sep
'''Simple parse, if format: \n
ParseResults( [ "----" ], {} )'''
format_tests_seperator = HiddenFormats.f_test_sep
'''Simple parse, if format: \n 
ParseResults( [ "====" ], {} )'''

format_text_begin = HiddenFormats.f_t_beg
''' After parsing: \n
ParseResults( [ "TEXTBEGIN", *line_of_text* ], { 'text': *line_of_text* } ) '''
format_text_end = HiddenFormats.f_t_end
''' After parsing: \n
ParseResults( [ "TEXTEND" ], {} ) '''

format_string_answer = HiddenFormats.f_str_ans
'''After parsing: \n
ParseResults( [ "ANSWER:", *line_of_text* ], { 'answer': *line_of_text* } )'''
format_string_reg_exp = HiddenFormats.f_str_regexp
'''After parsing: \n
ParseResults( [ "REGEXP:", *bool* ], { 'reg_exp': *bool* } )'''
format_string_sectors = HiddenFormats.f_str_sect
'''Will parse, if formats found: \n
CONFIG:
    ParseResults( [ "CONFIG" ], {} )
ANSWER:
    ParseResults( [ "ANSWER:", *line_of_text* ], { 'answer': *line_of_text* } )
REGEXP: 
    ParseResults( [ "REGEXP:", *line_of_text* ], { 'reg_exp': *line_of_text* } )'''

format_number_answer = HiddenFormats.f_num_ans
'''After parsing: \n
ParseResults( [ "ANSWER:", *float_number_1*, *float_number2* ],
{ 'answer': *float_number1*, 'adm_err': *float_number_2* } )'''
format_number_sectors = HiddenFormats.f_num_sect
'''Will parse, if formats found: \n
CONFIG:
    ParseResults( [ "CONFIG" ], {} )
ANSWER:
    ParseResults( [ "ANSWER:", *float_number_1*, *float_number2* ],
    { 'answer': *float_number1*, 'adm_err': *float_number_2* } )'''

format_quiz_answer = HiddenFormats.f_quiz_ans
"""After parsing: \n
ParseResults( [ "ANSWER:", *arr_of_letters* ], { 'answer': *arr_of_letters* } )"""
format_quiz_shuffle = HiddenFormats.f_quiz_shuff
'''After parsing: \n
ParseResults( [ "SHUFFLE:", *bool* ], { 'do_shuffle': *bool* } )'''
format_quiz_option = HiddenFormats.f_quiz_opt
'''After parsing: \n
ParseResults( [ *AIKEN_option*, *line_of_text* ],
{ 'letter': *AIKEN_option*, 'text': *line_of_text* } ) '''
format_quiz_sectors = HiddenFormats.f_quiz_sect
'''Will parse, if formats found: \n
CONFIG:
    ParseResults( [ "CONFIG" ], {} )
TEXTBEGIN:
    ParseResults
TEXEND:
    ParseResults
ANSWER:
    ParseResults( [ "ANSWER:", *arr_of_letters* ], { 'answer': *arr_of_letters* } )
SHUFFLE:
    ParseResults( [ "SHUFFLE:", *bool* ], { 'do_shuffle': *bool* } )
OPTION:
    ParseResults( [ *AIKEN_option*, *line_of_text* ],
    { 'letter': *AIKEN_option*, 'text': *line_of_text* } )'''

format_taskinline_parameter = HiddenFormats.f_til_param
'''After parsing: \n
ParseResults( [ *parameter_name*, "=", *single_word* ],
{ 'parameter': *parameter_name*, 'value': *single_word* } )'''
format_taskinline_sectors = HiddenFormats.f_til_sect
'''Will parse, if formats found: \n
CONFIG:
    ParseResults( [ "CONFIG" ], {} )
CODE:
    ParseResults( [ "CODE" ], {} )
HEADER:
    ParseResults( [ "HEADER" ], {} )
FOOTER:
    ParseResults( [ "FOOTER" ], {} )
TEST:
    ParseResults( [ "TEST"], {} )'''


def search_format_in_text(
    text: list[str],
    parse_exp: pp.ParserElement,
    _from_line: int | None = None,
    _to_line: int | None = None,
    _amount: int = -1,
    _from_start: bool = False,
) -> list[tuple[pp.ParseResults, int, int, int]]:
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


def check_format(text: str, parse_exp: pp.ParserElement, _match_all: bool = True) -> bool:
    try:
        _ = parse_exp.parse_string(text, parse_all=_match_all)
        result = True
    except Exception:
        result = False
    return result


def find_format(
    text: str, parse_exp: pp.ParserElement, _from_start: bool = False, _amount: int = 1
) -> tuple:
    # TODO: add _from_start
    match = tuple(parse_exp.scan_string(text, max_matches=_amount))
    return match


def match_format(
    text: str, parse_exp: pp.ParserElement, _match_all: bool = False
) -> pp.ParseResults:
    try:
        match = parse_exp.parseString(text, parse_all=_match_all)
        return match
    except Exception:
        return pp.ParseResults([])


# def match_format(text: str, parse_exp):
#    pass
