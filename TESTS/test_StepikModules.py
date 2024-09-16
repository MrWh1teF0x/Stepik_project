from Parse_Classes.OnlineTokens import OnlineLesson
import pytest

def test_Lesson_init():
    a1 = OnlineLesson()

    assert a1.file is None
    with pytest.warns(ImportWarning):
        a1.open_file(r"D:\PyCharm Projects\Stepic_project\files\sadmple.md")

