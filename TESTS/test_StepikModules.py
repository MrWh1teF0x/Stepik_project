from src.Parse_Classes.OnlineTokens import OnlineLesson
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
    assert a1.file == ["# This is a test file\n", "it is only used for testing purposes\n", "\n",
                       "* 1\n", "* 2\n", "* 3\n", "\n", "### Header 3\n"]
    # wrong call, file not changed -----------------------------------------------
    with pytest.warns(UserWarning):
        a1.read_file(r"")
    assert a1.file is not None
    # clear ----------------------------------------------------------------------
    a1 = OnlineLesson()
    assert a1.file is None
