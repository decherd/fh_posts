---
title: MD Test
summary: A test of a .md file
date: February 25, 2025
tags:
  - python
  - fasthtml
  - monsterui
---

# MD Test

This is a test of a .md file.
<https://www.example.com>

```python:run:hide
a = 5
```

# Show code block and the output
```python:run
# Show code block and the output
def add_number(x, y):
    return x + y
print(f"a is {a}")
add_number(a, 1)
```

# Show the code and don't run it
```python
# Show the code and don't run it.
print(f"The result of adding two to {a} is {add_number(a, 2)}")
add_number(a, 2)
```

# Don't show code block but show the output
```python:run:hide-in
# Don't show code block but show the output
print(f"The result of adding three to {a} is {add_number(a, 3)}")
add_number(a, 3)
```

# Show code block but don't show the output
```python:run:hide-out
# Show code block but don't show the output
print(f"The result of adding four to {a} is {add_number(a, 4)}")
add_number(a, 4)
```

# Show code block with the last line (function call shown) and the output
```python:run:hide-call
# Show code block but hide the last line (function call) and show the output
print(f"The result of adding five to {a} is {add_number(a, 5)}")
add_number(a, 6)
```