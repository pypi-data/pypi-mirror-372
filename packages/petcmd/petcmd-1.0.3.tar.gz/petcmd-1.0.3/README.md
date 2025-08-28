# petcmd

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/petcmd)
![PyPI - Version](https://img.shields.io/pypi/v/petcmd)
![Documentation Status](https://readthedocs.org/projects/petcmd/badge/?version=latest)
![PyPI - License](https://img.shields.io/pypi/l/petcmd)
![Downloads](https://static.pepy.tech/badge/petcmd)

## Installation

**petcmd** can be installed with [pip](http://pypi.python.org/pypi/pip):

```bash
python -m pip install petcmd
```

You can also download the project source and do:

```bash
pip install .
```

## Dependencies

**petcmd** was created as a lightweight package, so there are no dependencies.

## Examples

```python
from petcmd import Commander

commander = Commander()

@commander.command("calc")
def calculate(a: int, b: int, operator: str = "+"):
	print(eval(f"{a} {operator} {b}"))

if __name__ == "__main__":
	commander.process()
```

```bash
$ python app.py calc 1 2
3
$ python app.py calc 10 2 /
5.0
$ python app.py calc 10 2 -o /
5.0
$ python app.py calc 10 2 --operator /
5.0
$ python app.py calc -a 10 -b 2 --operator /
5.0
```

### Documentation

Documentation is available at https://petcmd.readthedocs.io/en/latest/

## Testing

```bash
python -m tests
```
