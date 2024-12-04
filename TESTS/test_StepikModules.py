from src.Parse_Classes.LessonParsers import Lesson
from src.PyParseFormats import *
import pytest


def test_Lesson_init():
    a1 = Lesson()
    # wrong calls ----------------------------------------------------------------
    with pytest.warns(UserWarning):
        a1_file = a1.read_file(r"..\files\sadmple_1.md")
    assert a1_file == []
    with pytest.warns(UserWarning):
        a1_file = a1.read_file(r"D:\.md")
    with pytest.warns(UserWarning):
        a1_file = a1.read_file(r"")
    assert a1_file == []
    assert a1.f_path is ""
    # correct call ---------------------------------------------------------------
    a1_file = a1.read_file(r"..\files\test.md")
    assert a1_file == [
        "# This is a test file",
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


def test_PyParse_check_format():
    a1_res = format_lesson_id.parseString("lesson = 123")
    assert a1_res.asList() == ["lesson", "=", "123"]
    assert a1_res.asDict() == {"lesson_id": "123"}
    a2_res = format_lesson_id.parseString("lesson=123")
    assert a2_res.asList() == ["lesson", "=", "123"]
    assert a2_res.asDict() == {"lesson_id": "123"}
    b_res = format_lesson_name.parseString("#    Lesson 1      ")
    assert b_res.asList() == ["#", "Lesson 1      "]
    assert b_res.asDict() == {"lesson_name": "Lesson 1      "}
    c_res = format_step_name.parseString("##\t\t\t dq21eoi1 231o231238")
    assert c_res.asList() == ["##", "dq21eoi1 231o231238"]
    assert c_res.asDict() == {"step_name": "dq21eoi1 231o231238"}
    d_res = format_step_name.parseString("## 123")
    assert d_res.asList() == ["##", "123"]
    assert d_res.asDict() == {"step_name": "123"}

    a = format_lesson_id.runTests("lesson = 123", printResults=False)
    assert a[0]
    assert a[1][0][1].asList() == ["lesson", "=", "123"]
    assert a[1][0][1].asDict() == {"lesson_id": "123"}
    a_1 = format_lesson_name.runTests(
        "  #   123123123", comment=None, printResults=False
    )
    assert a_1[0]

    b = format_lesson_name.runTests(
        "  #    Lesson 1      ", comment=None, printResults=False
    )
    assert b[0]
    assert b[1][0][1].asList() == ["#", "Lesson 1"]
    assert b[1][0][1].asDict() == {"lesson_name": "Lesson 1"}

    match_b = find_format("# lesson 1 \n # 123123123", format_lesson_name)
    assert match_b[0][0].asList() == ["#", "lesson 1 "]
    assert match_b[1][0].asList() == ["#", "123123123"]

    match_a = find_format("gibberish", format_lesson_name)
    assert match_a == ()

    text_a = [
        "# HEADER",
        "some text",
        "lesson = 123123123",
        "awaawdawd",
        "## Lesson1",
        "fussaweawefo",
    ]
    res_a = search_format_in_text(text_a, format_lesson_id)
    assert 123123123 == int(res_a[0][0]["lesson_id"])


# search_format_in_text (max_amount = 0)


def test_Lesson_parse_id_and_name():
    a1 = Lesson(r"..\files\test.md")
    a2 = Lesson()
    a3 = Lesson(r"..\files\sample_1.md")
    a4 = Lesson()

    with pytest.warns(UserWarning):
        a1.parse()
    assert a1.name == ""
    assert a1.id == -1

    a2.parse(r"..\files\sample_1.md")
    assert a2.name == "Установка python"
    assert a2.id == 483387

    a3.parse(r"..\files\sample_2.md")
    assert a3.name == "read, readline, readlines"
    assert a3.id == 496523

    with pytest.warns(UserWarning):
        a4.parse()
    assert a4.name == ""
    assert a4.id == -1


def test_Steps():
    lesson = Lesson(r"..\files\debug.md")
    lesson.parse()

    steps = lesson.steps
    print()
    for s in steps:
        print(s.json_data)
