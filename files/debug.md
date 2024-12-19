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

## TASKINLINE Задача найти расстояние между 2 точками на плоскости XY

Даны координаты 2 точек (x1, y1) и (x2, y2). 

**Написать функцию** `dist(x1, y1, x2, y2)`, которая вычисляет расстояние между ними по формуле $$c^2 = (x_1 - x_2)^2 + (y_1 - y_2)^2$$

<img src="https://stepik.org/media/attachments/lesson/408292/length2D.png" width=300 />

```python
from math import sqrt  # функция вычисляет квадратный корень

def dist(x1, y1, x2, y2):
    # тут нужно написать код

x1, y1, x2, y2 = map(float, input().split())    # читаем числа
d = dist(x1, y1, x2, y2)                        # вызываем функцию
print(d)                                        # печатаем результат
```
TEST
3 0 0 4
----
5.0
====
0 4 3 0
----
5.0
====
0 1 0 5
----
4.0
====
1 2 3 4
----
2.8284271247461903
====
-1.3 5.1 1.7 1.1
----
5.0
====
CONFIG
checker = std_float_seq
code_lang = python3
CODE
from math import sqrt  # функция вычисляет квадратный корень

def dist(x1, y1, x2, y2):
    # тут нужно написать код

x1, y1, x2, y2 = map(float, input().split())    # читаем числа
d = dist(x1, y1, x2, y2)                        # вызываем функцию
print(d)                                        # печатаем результат

## TASKINLINE Сумма
Даны два нецелых числа через пробел. Напечатайте их сумму.
HEADER
#include <stdio.h>
int main() {
FOOTER
	return 0;
}
CODE
// объявите 2 переменные x и y

// прочитайте в них числа

// вычислите и напечатайте результат

CONFIG
cost = 3
samples_count = 2
code_lang = c++20
checker = std_float_seq
TEST
0.1 0.2
----
0.3
====
-3.12
7.28
----
4.16
====
-1
-2
----
-3.0
====
0
0
----
0.0
====
21
-21.0
----
0.0
====
