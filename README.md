# fh_posts


<!-- WARNING: THIS FILE WAS AUTOGENERATED! DO NOT EDIT! -->

fh_posts is a Python package that transforms your Markdown and Jupyter
Notebook blog posts into dynamic FastHTML content. It extracts YAML
front matter using fastcore’s AttrDict for seamless metadata access and
executes custom-tagged Python code blocks to render interactive posts.

# Features

- YAML Front Matter Parsing: Automatically extracts front matter (e.g.,
  title, summary, date, tags) and makes it accessible via both
  dictionary and attribute notation.
- Multi-Format Support: Process both Markdown (.md) and Jupyter Notebook
  (.ipynb) files.
- Dynamic Code Execution: Custom code block tags let you decide whether
  to run code, hide code, or show output live.
- FastHTML Integration: Render posts to FastHTML’s NotStr objects for
  lightning-fast blog content.
- Link Handling: Optionally set all links to open in a new window when
  rendering.

# Installation

Install the package via pip:

``` python
pip install fh-posts
```

# Usage

You can import the package in two ways:

``` python
# Option 1: Import everything
from fh_posts.all import *

# Option 2: Import only the core functionality
from fh_posts.core import Post, load_posts
```

## Tags

In a markdown file when you add a code block with triple backticks and
python, append additional colon seperated tags to control how the code
is run and rendered. All run code blocks will be executed in order and
be in the namespace for the rest of the post. This should feel familiar
to those who have used jupyter notebooks.

- `python` (default) - output the code but don’t run it
- `python:run` - run and show the code and the output
- `python:run:hide` - run the code but don’t the code or output
- `python:run:hide-in` - run the code but don’t show the code block,
  only the output
- `python:run:hide-out` - run the code and show the output but don’t
  show the code block
- `python:run:hide-call` - run the code and show the output and the code
  block but don’t show the call to the function (last line of code)

In a notebook file all code cells are run by default. Add a `#|python`
tag to the first line of any code cell to also have it appear as a code
block in the post. All of the other tags for markdown posts apply to
notebook posts as well. Having to add `run` each time is redundant since
all cells are run but it keeps things consistent between markdown and
notebook posts.

## Example: Markdown Posts

Markdown File (hello.md):

```` markdown
---
title: Hello FastHTML and MonsterUI
summary: An introduction to FastHTML and MonsterUI.
date: February 25, 2025
tags:
  - python
  - fasthtml
  - monsterui
---

Welcome to our blog post!

```python:run
print("Hello, world!")
```
````

### Loading & Rendering:

``` python
from pathlib import Path
from fh_posts.core import load_posts

# Load posts from the 'posts' directory
posts = load_posts(Path('posts'))

# Access metadata
for post in posts:
    print(post.title, post.date)

# Render a post by its slug
post = next(p for p in posts if p.slug == 'hello')
html_output = post.render(open_links_new_window=True)
print(html_output)
```

![Screenshot of rendered markdown post](./images/md_render.png)

## Example: Jupyter Notebook Posts

Notebook File (notebook_post.ipynb):

- Cell 1 (Raw Cell with YAML Front Matter):

``` yaml
---
title: Notebook Post Example
summary: A demonstration of a notebook-based blog post.
date: March 1, 2025
tags:
  - jupyter
  - python
---
```

## Code Cell Example:

``` python
#|python:run:hide-in
print("Notebook live output")
```

# Contributing

Contributions are welcome! Please open an issue or submit a pull request
to help improve fh_posts.
