## Basic "ParserElement" tokens




## Basic ways to join various "ParserElement"
| Command                 | Operator analog   | Explanation              |
|-------------------------|-------------------|--------------------------|
| pp.And([p1, p2])        | == p1 + p2        | Ordered join             |
| pp.Each([p1, p2])       | == p1 & p2        | Unordered join           |
| pp.MatchFirst([p1, p2]) | == p1 \| p2       | Priority match           |
| pp.Or([p1, p2])         | == p1 ^ p2        | Longest match            |
| pp.NotAny(p)            | == ~ p            | denial                   |
| p + p + p               | == p * 3 or 3 * p | Abbreviation for binding |


## Whays to parse text
**parseString** – parses input text from the beginning; ignores extra trailing text.\
**scanString** – looks through input text and generates matches; similar to re.finditer() \
**searchString** – like scanString, but returns a list of tokens \
**transformString** – like scanString, but specifies replacements for tokens
