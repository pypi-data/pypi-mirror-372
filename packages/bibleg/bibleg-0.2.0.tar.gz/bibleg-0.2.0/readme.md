# bibleg

[![Test](https://github.com/jncraton/bibleg/actions/workflows/test.yml/badge.svg)](https://github.com/jncraton/bibleg/actions/workflows/test.yml)

Unofficial Bible API in Python

## Installation

```sh
pip install bibleg
```

## Usage

```python
>>> from bibleg import get_text

>>> get_text("John 11:35")
'Jesus wept.'

>>> get_text("Gen 1:1")
'In the beginning, God created the heavens and the earth.'
```
