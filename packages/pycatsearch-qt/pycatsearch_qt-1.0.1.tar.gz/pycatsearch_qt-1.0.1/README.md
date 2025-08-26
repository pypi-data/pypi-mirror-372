# PyCatSearch-Qt

A Qt-based GUI for [PyCatSearch](https://github.com/stsav012/pycatsearch).

## Requirements

The code is developed under `Python 3.13`.

It should work under `Python 3.8` but is uninstallable there bue to changes in `setuptools`.
Still, you can get the source files and try them under `Python 3.8`.

The GUI requires Python bindings for Qt (`PyQt5`, `PySide6`, `PyQt6`, or `PySide2`), picked by `QtPy`.

## Installation

The package is available from the PyPI repo:

```commandline
python3 -m pip install pycatsearch-qt
```

One may provide a Qt binding beforehand manually installing
- `PySide6-Essentials`,
- `PyQt6`,
- `PyQt5`, or
- `PySide2`.

Otherwise, one of them will be installed automatically.
Currently, it is unavoidable.
