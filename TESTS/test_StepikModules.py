from src.Parse_Classes.OnlineTokens import OnlineLesson
from src.RegExpFormats import *
import pytest


def test_Lesson_init():
    a1 = OnlineLesson()

    # wrong calls ----------------------------------------------------------------
    assert a1.file is None
    with pytest.warns(UserWarning):
        a1.read_file(r"D:\PyCharm Projects\Stepic_project\files\sadmple_1.md")
    assert a1.file is None
    with pytest.warns(UserWarning):
        a1.read_file(r"D:\.md")
    with pytest.warns(UserWarning):
        a1.read_file(r"")
    assert a1.file is None
    # correct call ---------------------------------------------------------------
    a1.read_file(r"D:\PyCharm Projects\Stepic_project\files\test.md")
    assert a1.file == ["# This is a test file", "it is only used for testing purposes", "",
                       "* 1", "* 2", "* 3", "", "\\n", "", "### Header 3"]
    # wrong call, file not changed -----------------------------------------------
    with pytest.warns(UserWarning):
        a1.read_file(r"")
    assert a1.file is not None
    # clear ----------------------------------------------------------------------
    a1 = OnlineLesson()
    assert a1.file is None


def test_RegExp_check_format():
    f1 = re.compile("c")
    f2 = re.compile("wadwadwad")
    f3 = format_lesson_id

    # TODO: add tests for f1, f2, f3


def test_Lesson_parse():
    # TODO: think of tests
    pass
