from src.Parse_Classes.OnlineTokens import OnlineLesson
from src.PyParseFormats import *
import pytest


def test_Lesson_init():
    a1 = OnlineLesson()

    # wrong calls ----------------------------------------------------------------
    assert a1.file is None
    with pytest.warns(UserWarning):
        a1.read_file(r"..\files\sadmple_1.md")
    assert a1.file is None
    with pytest.warns(UserWarning):
        a1.read_file(r"D:\.md")
    with pytest.warns(UserWarning):
        a1.read_file(r"")
    assert a1.file is None
    # correct call ---------------------------------------------------------------
    a1.read_file(r"..\files\test.md")
    assert a1.file == ["# This is a test file", "it is only used for testing purposes", "",
                       "* 1", "* 2", "* 3", "", "\\n", "", "### Header 3"]
    # wrong call, file not changed -----------------------------------------------
    with pytest.warns(UserWarning):
        a1.read_file(r"")
    assert a1.file is not None
    # clear ----------------------------------------------------------------------
    a1 = OnlineLesson()
    assert a1.file is None


def test_PyParse_check_format():
    a_res = format_lesson_id.parseString("lesson = 123")
    # нужен тест на пробелы
    assert a_res.asList() == ["lesson", '=', '123']
    assert a_res.asDict() == {'lesson_id': '123'}
    b_res = format_lesson_name.parseString("#    Lesson 1      ")
    assert b_res.asList() == ['#', 'Lesson 1      ']
    assert b_res.asDict() == {'lesson_name': 'Lesson 1      '}
    c_res = format_step_name.parseString("##\t\t\t dq21eoi1 231o231238")
    assert c_res.asList() == ['##', 'dq21eoi1 231o231238']
    assert c_res.asDict() == {'step_name': 'dq21eoi1 231o231238'}

    a = format_lesson_id.runTests("lesson = 123", printResults=False)
    assert a[0]
    assert a[1][0][1].asList() == ['lesson', '=', '123']
    assert a[1][0][1].asDict() == {'lesson_id': '123'}

    b = format_lesson_name.runTests("  #    Lesson 1      ", comment=None, printResults=False)
    assert b[0]
    assert b[1][0][1].asList() == ['#', 'Lesson 1']
    assert b[1][0][1].asDict() == {"lesson_name": 'Lesson 1'}

    match_b = find_format("# lesson 1 \n # 123123123", format_lesson_name)
    assert match_b[0][0].asList() == ['#', 'lesson 1 ']
    assert match_b[1][0].asList() == ['#', '123123123']


def test_Lesson_parse():
    # TODO: think of tests
    pass
