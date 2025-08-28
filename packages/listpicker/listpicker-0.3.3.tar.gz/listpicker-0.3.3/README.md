python-listpicker
=================

Interactive list selection for POSIX terminals.

```python
pip install listpicker
```

Python 3.10+

Features
--------

- Single and multiple selection from a sequence of strings
- Interactive substring filtering
- Paging for long lists
- Common navigation keybindings (vi, emacs, arrow keys, Home/End, etc)
- Direct terminal manipulation with CSI commands (i.e. no curses)
- Draw to main screen buffer without clearing the screen
- Proper truncation of long lines with SGR color sequences
- Redraw on terminal resize (SIGWINCH)
- Help menu and multiselect confirmation prompt
- Preselected options in multiselect prompts

Screenshots
-----------

![timezones](https://github.com/guns/python-listpicker/assets/55776/f7e6629b-77ba-4f99-a9f6-0de15485c2dd)
![helpmenu](https://github.com/guns/python-listpicker/assets/55776/78a966e7-4023-4d52-bfa9-87acac89b73e)
![filtering](https://github.com/guns/python-listpicker/assets/55776/ae01150c-cead-42f3-898e-2d631d3ba83a)
![multiselect](https://github.com/guns/python-listpicker/assets/55776/4888a62c-a94b-41c8-8113-07fee8649648)
![multiselect-confirmation](https://github.com/guns/python-listpicker/assets/55776/81cb6432-7791-4439-b2cf-0f90d7e67cfe)

Examples
--------

### Basic usage

```python
import listpicker

pizza_styles = ("Thin crust", "Stuffed crust", "Deep dish")
style = listpicker.pick("Choose pizza style:", pizza_styles)

# User can abort input, so handle the case where "pick()" returns "None"
if style is None:
    style = pizza_styles[0]

pizza_toppings = ("Pepperoni", "Sausage", "Mushroom", "Pineapple")
toppings = listpicker.pick_multiple("Choose toppings:", pizza_toppings)
```

### Typical usage with dictionary

```python
import dataclasses

import listpicker


@dataclasses.dataclass
class Book:
    isbn: str
    title: str
    authors: list[str]
    publication_year: int


books = [
    Book(
        "0201038013",
        "The Art of Computer Programming, Volume 1: Fundamental Algorithms",
        ["Knuth, Donald"],
        1968,
    ),
    Book(
        "0262010771",
        "Structure and Interpretation of Computer Programs",
        ["Harold Abelson", "Gerald Jay Sussman", "Julie Sussman"],
        1984,
    ),
    Book(
        "032163537X",
        "Elements of Programming",
        ["Stepanov, Alexander A.", "McJones, Paul"],
        2009,
    ),
]

options = {f"{b.title} ({b.publication_year})": b for b in books}
choice = listpicker.pick("Pick a book:", list(options.keys()))

# Pick a book:
#   (filter with f, submit with Enter, F1 for keybindings)
# > 1. The Art of Computer Programming, Volume 1: Fundamental Algorithms (1968)
#   2. Structure and Interpretation of Computer Programs (1984)
#   3. Elements of Programming (2009)

if choice:
    book = options[choice]
```
