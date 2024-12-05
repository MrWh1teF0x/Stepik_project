# Установка python

lesson = 483387

## Где программировать?

Выберите один вариант.

* Хороший компьютер? Установите PyCharm. Очень удобно.
* Медленный компьютер? Установите python.
* iOS? Установите Pythonista
* Нет компьютера? Программируйте online на repl.it

TODO: Тут должны быть переходы на разные инструкции

## Установите PyCharm

* https://www.jetbrains.com/pycharm/download/#section=windows
    * Выберите Windows, Mac или Linux
    * Для Community выберите кнопку Download
    
## STRING string text

Напишите слово "Деревяшка123" в ответе (в таком-же регистре)
123 ANSWER: "Деревяшка321"

ANSWER: Деревяшка123

## STRING Да, да, нет

Что напечатает код?

```python
res = 'yes'
res = res + 'yes'
res = res + 'no'
print(res)
```

ANSWER: yesyesno

## QUIZ Длина строки

Как вычислить длину строки `s`?

A. `len(s)`
B. `length(s)`
C. `size(s)`
D. `s.len()`
E. `s.length()`
F. `s.size()`

ANSWER: A

## QUIZ Прочитать размер стороны

TEXTBEGIN
Нужно прочитать длину стороны квадрата и передать ее в функцию sq. Какой код написан правильно?
```python
def sq(size):
    for i in range(4):
        t.fd(size)
        t.lt(90)
```
TEXTEND

A.
```python
a = int(input())
sq(a)
```

B.
```python
a = input()
sq(a)
```

C.
```python
a = len(input())
sq(a)
```

D.
```python
a = input()
a = int(a)
sq(a)
```

ANSWER: A, D

## NUMBER Число ПИ

Введите число пи с точностью 0.01

ANSWER: 3.14 ± 0.01