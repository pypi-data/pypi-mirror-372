# dotdotdot

A minimalist python library to access application configuration using dot notation.

----
## Usage
```bash
   (dot3.6) narora@nararombp ~/s/d/tests 𝓝𝓮𝓱𝓪𝓻 > cat test_config.yml
    test:
      nest:
        inty: 1
        stringy: 'string'
        listy: [1]
    (dot3.6) narora@nararombp ~/s/d/tests 𝓝𝓮𝓱𝓪𝓻 > python
    Python 3.6.4 (default, Dec 21 2017, 20:32:22)
    [GCC 4.2.1 Compatible Apple LLVM 7.3.0 (clang-703.0.31)] on darwin
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import dotdotdot as dot
    >>> c = dot.load('test_config.yml')
    >>> type(c)
    <class 'dotdotdot.config.Config'>
    >>> type(c.test)
    <class 'dotdotdot.config.test'>
    >>> type(c.test.nest)
    <class 'dotdotdot.config.nest'>
    >>> type(c.test.nest.inty)
    <class 'int'>
    >>> type(c.test.nest.stringy)
    <class 'str'>
    >>> type(c.test.nest.listy)
    <class 'list'>
    >>> c.test.nest.inty
    1
    >>> c.test.nest.stringy
    'string'
    >>> c.test.nest.listy
    [1]
    >>>
```

----
## Run tests
* Python 2.7
```
(dot2.7) nehar@nehar-macbook ~/D/s/dotdotdot 𝓝𝓮𝓱𝓪𝓻 > pytest
=============== test session starts ===============
platform darwin -- Python 2.7.15, pytest-4.2.0, py-1.7.0, pluggy-0.8.1
rootdir: /Users/nehar/Documents/src/dotdotdot, inifile: pytest.ini
plugins: pep8-1.0.6, flake8-1.0.4
collected 3 items

tests/test_config.py ...                                                                                                                                                                                                                                [100%]

=============== deprecated python version ===============
You are using Python 2.7.15, which will no longer be supported in pytest 5.0
For more information, please read:
  https://docs.pytest.org/en/latest/py27-py34-deprecation.html
=============== 3 passed in 0.10 seconds ===============
(dot2.7) nehar@nehar-macbook ~/D/s/dotdotdot 𝓝𝓮𝓱𝓪𝓻 >
```
* Python 3.7
```
(dot2.7) nehar@nehar-macbook ~/D/s/dotdotdot 𝓝𝓮𝓱𝓪𝓻 > vf activate dot3.7
(dot3.7) nehar@nehar-macbook ~/D/s/dotdotdot 𝓝𝓮𝓱𝓪𝓻 > pytest
/Users/nehar/venvs/dot3.7/lib/python3.7/site-packages/pep8.py:110: FutureWarning: Possible nested set at position 1
  EXTRANEOUS_WHITESPACE_REGEX = re.compile(r'[[({] | []}),;:]')
=============== test session starts ===============
platform darwin -- Python 3.7.1, pytest-4.2.0, py-1.7.0, pluggy-0.8.1
rootdir: /Users/nehar/Documents/src/dotdotdot, inifile: pytest.ini
plugins: pep8-1.0.6, flake8-1.0.4
collected 3 items

tests/test_config.py ...                                                                                                                                                                                                                                [100%]

=============== 3 passed in 0.09 seconds ===============
(dot3.7) nehar@nehar-macbook ~/D/s/dotdotdot 𝓝𝓮𝓱𝓪𝓻 >
```
-----
## Building the wheel
```bash
    (3.6) nehar@mac ~/s/dotdotdot 𝓝𝓮𝓱𝓪𝓻 > python setup.py bdist_wheel
```

----
## Installation
```bash
    (3.6) nehar@mac ~/s/dotdotdot 𝓝𝓮𝓱𝓪𝓻 > pip install dist/dotdotdot-1.0.0-py3-none-any.whl
    Processing ./dist/dist/dotdotdot-1.0.0-py3-none-any.whl 
    Installing collected packages: dotdotdot
    Successfully installed dotdotdot-1.0.0
```
