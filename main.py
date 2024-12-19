from src.Parse_Classes.LessonParsers import Lesson
import src.PyParseFormats as PPF

class ALPHA:
    numb: int = 0

def test_Lesson_parse_id_and_name():
    a1 = Lesson(r".\files\test.md")
    a2 = Lesson()
    a3 = Lesson(r".\files\sample_1.md")
    a4 = Lesson()

    a1.parse()
    assert a1.name == ""
    assert a1.id == -1

    a2.parse(r".\files\sample_1.md")
    assert a2.name == "Установка python"
    assert a2.id == 483387

    a3.parse(r".\files\sample_2.md")
    assert a3.name == "read, readline, readlines"
    assert a3.id == 496523

    a4.parse()
    assert a4.name == ""
    assert a4.id == -1

if __name__ == "__main__":
    a = PPF.format_lesson_id.runTests("lesson = 123", printResults=False)
    b = PPF.format_lesson_id.runTests("lesson -= 123", printResults=False)
    c = PPF.pp.ParseResults(a[1][0])
    print()
    print(a[1][0][1])
    print(b[1])
    print(c)
    print(-0 == 0)
    print("-")
    a = PPF.format_quiz_option.runTests(" A) 123", comment=None, printResults=False)
    print(a)
    a = PPF.format_quiz_option.parseString(" A) 123")
    print(a)
    print("-")
    a = ["12345"]
    print("\n".join(a))
    a = "123456"
    i = 2
    print(f"""In {a}: expected "{chr(ord(a[i - 1]) + 1)}" after "{a[i - 1]}", \
got "{a[i]}" instead""")
    print("-")
    a = lambda x: int(x)
    print([a("123")])

    print("-")
    text = r"123\ne"
    print(text)
    print([text])

    print("-")
    print("##  \t a \n b \f c \r TEXT \n QUIZ")
    print(["##  \t a \n b \f  c \r TEXT \n QUIZ"])

    print("-")
    print(""" 
return template code in IDE
"::python3\n::code\n# This is code in lang and templates\n::header\n# This is header\n::footer\n# This is footer\n"
""")
    print("End")
    # test_Lesson_parse_id_and_name()
