import os
import pprint

from src.parse_classes.step_parsers import StepTaskInLine
import pytest

from src.parse_classes.lesson_parsers import Lesson
from src.parse_classes.pyparse_formats import *

__do_debug = False


def test_Lesson_init():
    a1 = Lesson()
    # wrong calls ----------------------------------------------------------------
    with pytest.warns(Warning):
        a1_file = a1.read_file(r"..\files\sadmple_1.md")
    assert a1_file == []
    with pytest.warns(Warning):
        a1_file = a1.read_file(r"D:\.md")
    with pytest.warns(Warning):
        a1_file = a1.read_file(r"")
    assert a1_file == []
    assert a1.f_path is None
    # correct call ---------------------------------------------------------------
    a1_file = a1.read_file(r"..\files\test.md")
    assert a1_file == [
        "## This is a test file",
        "it is only used for testing purposes",
        "",
        "* 1",
        "* 2",
        "* 3",
        "",
        "\\n",
        "",
        "### Header 3",
    ]
    # path set
    a2 = Lesson(r"..\files\test.md")
    a1_file = a1.read_file(a2.f_path)

    a1.f_path = r"..\files\sample_1.md"
    a2_file = a2.read_file(a2.f_path)

    assert a1_file == a2_file
    assert a1.f_path != a2.f_path

    a1.id = 2
    assert a2.id != a1.id


def check_format_on_text(
    text: list[str],
    pp_format: pp.ParserElement,
    check_array: list[bool],
    match_list: None | list = None,
    match_dict: None | list[dict] = None,
    find_array: None | list[tuple[int, int]] = None,
):
    if __do_debug:
        print("-- check_format_on_text --")
    for i in range(len(text)):
        if __do_debug:
            print(f"line: {(text[i], )}", end="")
        assert check_array[i] == check_format(text[i], pp_format)
        if match_list is not None:
            assert match_list[i] == match_format(text[i], pp_format).asList()
        if match_dict is not None:
            assert match_dict[i] == match_format(text[i], pp_format).asDict()
        if find_array is not None:
            if find_array[i] == ():
                assert find_array[i] == find_format(text[i], pp_format)
            else:
                assert find_array[i] == find_format(text[i], pp_format)[0][1:]
        if __do_debug:
            print(" -- SUCCESS")

    if __do_debug:
        print("-- search_format_in_text --")
        for i in search_format_in_text(text, pp_format):
            print(i)


def test_format_lesson_name():
    if __do_debug:
        print()

    # format_lesson_name
    a = format_lesson_name.parseString("# 123")
    assert a.asList() == ["#", "123"]
    assert a.asDict() == {"lesson_name": "123"}

    with pytest.raises(pp.exceptions.ParseException):
        b = format_lesson_name.parseString("#123 123")
        if __do_debug:
            print("wrong parse: " + str([b]))

    with pytest.raises(pp.exceptions.ParseException):
        c = format_lesson_name.parseString("## 123")
        if __do_debug:
            print("Wrong parse: " + str([c]))

    d = format_lesson_name.parseString("# # 123")
    assert d.asList() == ["#", "# 123"]
    assert d.asDict() == {"lesson_name": "# 123"}

    e = format_lesson_name.parseString("#  \r   \t #  Lesson 1      ")
    assert e.asList() == ["#", "#  Lesson 1      "]
    assert e.asDict() == {"lesson_name": "#  Lesson 1      "}

    with pytest.raises(pp.exceptions.ParseException):
        f = format_lesson_name.parseString("### dfoeo dowaa;d")
        if __do_debug:
            print("Wrong parse: " + str([f]))

    text = [
        "# TEXT 123123123  ",
        "line of text",
        "##, wrong step name",
        "#1wrong header",
        "# not Another step name",
        "now # is later",
        "now we use \n 123",
        "again, but with \n # new header",
        "   # some spaces before text",
        "   # ",
        "#",
        "## TEXT Step name",
        "### Normal h3",
        "   # bad ## line # to ## live   ",
        "",
    ]
    check_arr = (
        True, False, False, False,
        True, False, False, False,
        True,
        True, False, False, False,
        True, False,
    )
    match_lst = (
        ["#", "TEXT 123123123  "], [], [], [],
        ["#", "not Another step name"], [], [], [],
        ["#", "some spaces before text"],
        ["#", ""], [], [], [],
        ["#", "bad ## line # to ## live   "], [],
    )
    match_dct = (
        {"lesson_name": "TEXT 123123123  "}, dict(), dict(), dict(),
        {"lesson_name": "not Another step name"}, dict(), dict(), dict(),
        {"lesson_name": "some spaces before text"},
        {"lesson_name": ""}, dict(), dict(), dict(),
        {"lesson_name": "bad ## line # to ## live   "}, dict(),
    )
    find_arr = (
        (0, 19), (), (), (),
        (0, 24),
        (4, 15), (),
        (18, 31),
        (3, 29),
        (3, 6), (),
        (1, 18),
        (2, 14),
        (3, 33), (),
    )

    check_format_on_text(
        text, format_lesson_name, check_arr, match_lst, match_dct, find_arr
    )


def test_format_lesson_id():
    if __do_debug:
        print()

    a = format_lesson_id.parseString("lesson = 12312")
    assert a.asList() == ["lesson", "=", 12312]
    assert a.asDict() == {"lesson_id": 12312}

    b = format_lesson_id.parseString("lesson=20685133")
    assert b.asList() == ["lesson", "=", 20685133]
    assert b.asDict() == {"lesson_id": 20685133}

    with pytest.raises(pp.exceptions.ParseException):
        c = format_lesson_id.parseString(" = 213349")
        if __do_debug:
            print("Wrong parse: " + str([c]))

    with pytest.raises(pp.exceptions.ParseException):
        d = format_lesson_id.parseString("lesson = -19124815")
        if __do_debug:
            print("Wrong parse: " + str([d]))

    with pytest.raises(pp.exceptions.ParseException):
        e = format_lesson_id.parseString("lesson = ")
        if __do_debug:
            print("Wrong parse: " + str([e]))

    f = format_lesson_id.parseString(" \n lesson = 0")
    assert f.asList() == ["lesson", "=", 0]
    assert f.asDict() == {"lesson_id": 0}

    text = [
        "# Lesson name",
        "leson = 123",
        "",
        "lesson = 456",
        "",
        " lesson = -000 \n lesson = 000",
        "## TEXT step with lesson = 789",
        "",
        "   lesson = 789",
    ]
    check_arr = (False, False, False, True, False, False, False, False, True)
    match_lst = ([], [], [], ["lesson", "=", 456], [], [], [], [], ["lesson", "=", 789])
    match_dct = (
        dict(),
        dict(),
        dict(),
        {"lesson_id": 456},
        dict(),
        dict(),
        dict(),
        dict(),
        {"lesson_id": 789},
    )
    find_arr = ((), (), (), (0, 12), (), (17, 29), (18, 30), (), (3, 15))

    check_format_on_text(
        text, format_lesson_id, check_arr, match_lst, match_dct, find_arr
    )


def test_format_step_name():
    if __do_debug:
        print()

    a = format_step_name.parseString("##  \tTEXT#Нет \n после Ashley Jackson")
    assert a.asList() == ["##", "", "TEXT#Нет \n после Ashley Jackson"]
    assert a.asDict() == {"type": "", "step_name": "TEXT#Нет \n после Ashley Jackson"}

    b = format_step_name.parseString("##  \tTEXT this is a stepText")
    assert b.asList() == ["##", "TEXT", "this is a stepText"]
    assert b.asDict() == {"type": "TEXT", "step_name": "this is a stepText"}

    # f*ck python and it's "\t". i give up  >_<
    # c = format_step_name.parseString("##  \t a \n b \t c \r TEXT \n QUIZ")
    # assert c.asList() == ["##", "", "a \n b \t c \t TEXT \n QUIZ"]
    # assert c.asDict() == {'type': "", 'step_name': "a \n b \t c \t TEXT \n QUIZ"}

    c = format_step_name.parseString("##  \t a \n b \f c \r TEXT \n QUIZ")
    assert c.asList() == ["##", "", "a \n b \f c \r TEXT \n QUIZ"]
    assert c.asDict() == {"type": "", "step_name": "a \n b \f c \r TEXT \n QUIZ"}

    with pytest.raises(pp.exceptions.ParseException):
        d = format_lesson_id.parseString("###     h3, not h2")
        if __do_debug:
            print("Wrong parse: " + str([d]))

    e = format_step_name.parseString("## dq21eoi1 231o231238")
    assert e.asList() == ["##", "", "dq21eoi1 231o231238"]
    assert e.asDict() == {"type": "", "step_name": "dq21eoi1 231o231238"}

    f = format_step_name.parseString("## 123")
    assert f.asList() == ["##", "", "123"]
    assert f.asDict() == {"type": "", "step_name": "123"}

    with pytest.raises(pp.exceptions.ParseException):
        g = format_step_name.parseString("")
        if __do_debug:
            print("Wrong parse: " + str([g]))


def test_number_answer_format():
    if __do_debug:
        print()
    """
    a = format_lesson_id.parseString("lesson = 12312")
    assert a.asList() == ["lesson", "=", 12312]
    assert a.asDict() == {"lesson_id": 12312}

    with pytest.raises(pp.exceptions.ParseException):
        c = format_lesson_id.parseString(" = 213349")
        if __do_debug:
            print("Wrong parse: " + str([c]))
    """

    a = format_number_answer.parseString("ANSWER: 123")
    assert a.asList() == ["ANSWER:", "123"]
    assert a.asDict() == {"answer": "123", 'section_type': 'ANSWER'}

    b = format_number_answer.parseString("ANSWER: 123.123")
    assert b.asList() == ["ANSWER:", "123.123"]
    assert b.asDict() == {"answer": "123.123", 'section_type': 'ANSWER'}

    with pytest.raises(pp.exceptions.ParseException):
        c = format_number_answer.parseString("ANSWER 123.123")
        if __do_debug:
            print("Wrong parse: " + str([c]))

    d = format_number_answer.parseString("ANSWER: 123±657")
    assert d.asList() == ["ANSWER:", "123", "657"]
    assert d.asDict() == {"answer": "123", "adm_err": "657", 'section_type': 'ANSWER'}

    e = format_number_answer.parseString("ANSWER: 123.567±9.11")
    assert e.asList() == ["ANSWER:", "123.567", "9.11"]
    assert e.asDict() == {"answer": "123.567", "adm_err": "9.11", 'section_type': 'ANSWER'}

    f = format_number_answer.parseString("ANSWER: -152±28.2")
    assert f.asList() == ["ANSWER:", "-152", "28.2"]
    assert f.asDict() == {"answer": "-152", "adm_err": "28.2", 'section_type': 'ANSWER'}

    with pytest.raises(pp.exceptions.ParseException):
        g = format_number_answer.parseString("ANSWER: -59±-21243.1", parse_all=True)
        if __do_debug:
            print("Wrong parse: " + str([g]))


# search_format_in_text (max_amount = 0)


def test_Lesson_parse_id_and_name():
    a1 = Lesson(r"..\files\test.md")
    a2 = Lesson()
    a3 = Lesson(r"..\files\sample_1.md")
    a4 = Lesson()

    with pytest.warns(Warning):
        a1.parse()
    assert a1.name == ""
    assert a1.id == -1

    a2.parse(r"..\files\sample_1.md")
    assert a2.name == "Установка python"
    assert a2.id == 483387

    a3.parse(r"..\files\sample_2.md")
    assert a3.name == "read, readline, readlines"
    assert a3.id == 496523

    with pytest.warns(Warning):
        a4.parse()
    assert a4.name == ""
    assert a4.id == -1


def test_Steps_creation():
    if __do_debug:
        print()
        print("Start: test_Steps_creation")
    lesson1 = Lesson(r"..\files\sample_1.md")
    lesson1.parse()
    assert lesson1.name == "Установка python"
    assert lesson1.id == 483387
    if __do_debug:
        print(lesson1.f_path)
        print(lesson1.steps)

    lesson2 = Lesson(r"..\files\debug.md")
    lesson2.parse()
    assert lesson2.name == "Установка python"
    assert lesson2.id == 483387
    if __do_debug:
        print(lesson2.f_path)
        print(lesson2.steps)

    lesson3 = Lesson(r"..\files\sample_2.md")
    lesson3.parse()
    assert lesson3.name == "read, readline, readlines"
    assert lesson3.id == 496523
    if __do_debug:
        print(lesson3.f_path)
        print(lesson3.steps)


def test_Steps_formats():
    if __do_debug:
        print()
        res = match_format("A. B)", format_quiz_option)
        print([res])
        res = match_format("    A. B)", format_quiz_option)
        print([res])
        res = match_format("  . B. A) asdasd", format_quiz_option)
        print([res])
        res = match_format("ANSWER: A, B", format_quiz_answer)
        print([res])
        res = match_format("TRUE", HiddenFormats._bool)
        print([res])
        res = match_format("SHUFFLE: TRuE", format_quiz_shuffle)
        print([res])
        res = match_format("_test_data = 103", HiddenFormats.f_til_param)
        print([res])
        res = match_format("_test_data = 103 ", HiddenFormats.f_til_param)
        print([res])
        res = match_format("_test_data = ", HiddenFormats.f_til_param)
        print([res])
        res = match_format("_test_data = 103 123dada123", HiddenFormats.f_til_param)
        print([res])
    a = "A. `len(s)`"
    assert check_format(a, format_quiz_option)
    b = "A."
    assert check_format(b, format_quiz_option)


def test_Step_Quiz():
    text = ["## QUIZ quiz",
            "some text",
            "more text",
            "",
            "A) a"
            "B) b"
            "",
            "ANSWER: A, B"
            ]


def test_Step_TaskInLine():
    if __do_debug:
        print()
    text = [
        "## TASKINLINE Задача написанная в .md",
        "",
        "Should parse like plain text",
        "some more text",
        "",
        "text after emtpy line",
        "singleword",
        "",
        "```python",
        "def func(a, b):",
        "    # put code here",
        "",
        "a, b = map(float, input().split())  # read params",
        "s = func(a, b)                      # call function",
        "print(s)                            # output result",
        "```",
        "TEST",
        "1 2",
        "----",
        "2.0",
        "====",
        "-10.1 10",
        "----",
        "-101.0",
        "====",
        "CODE",
        "def func(a, b):",
        "    # put code here",
        "",
        "a, b = map(float, input().split())  # read params",
        "s = func(a, b)                      # call function",
        "print(s)                            # output result",
        "",
        "CONFIG",
        "code_lang = python3",
        "cost = 100",
        "check_format = std_float_seq",
        "wrong_param = wrong_value",
        "HEADER",
        "HEADER IT IS",
        "FOOTER",
        "print(\"hi\")",
    ]

    step = StepTaskInLine()
    step.parse(text)
    if __do_debug:
        print([step.pre_code])
        print([step.post_code])
        pprint.pprint(step.body())
