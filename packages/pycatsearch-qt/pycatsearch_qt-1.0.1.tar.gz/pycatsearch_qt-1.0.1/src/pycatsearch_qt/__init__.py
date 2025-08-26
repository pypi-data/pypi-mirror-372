import sys
from abc import ABCMeta
from contextlib import suppress
from datetime import datetime, timedelta, timezone
from functools import partialmethod
from pathlib import Path
from typing import Any

from packaging.version import Version
from pycatsearch.catalog import Catalog
from qtpy import PYSIDE2, QT6
from qtpy.QtCore import QLibraryInfo, QLocale, QTranslator, Qt, qVersion
from qtpy.QtGui import QIcon
from qtpy.QtWidgets import QAbstractSpinBox, QApplication, QDialog, QMenu, QWidget

__all__ = ["qta_icon", "main"]

__author__ = "StSav012"
__original_name__ = "pycatsearch_qt"

try:
    from ._version import __version__
except ImportError:
    __version__ = ""


class _QWidgetMetaMixin(type(QWidget), ABCMeta):
    pass


if sys.version_info < (3, 10, 0) and __file__ != "<string>":
    from importlib import import_module
    from importlib.abc import Loader, MetaPathFinder
    from importlib.machinery import ModuleSpec
    from importlib.util import spec_from_file_location
    from types import CodeType, ModuleType

    class StringImporter(MetaPathFinder):
        class Loader(Loader):
            def __init__(self, modules: "dict[str, str | dict]") -> None:
                self._modules: "dict[str, str | dict]" = modules

            def is_package(self, module_name: str) -> bool:
                return isinstance(self._modules[module_name], dict)

            def get_code(self, module_name: str) -> CodeType:
                return compile(self._modules[module_name], filename="<string>", mode="exec")

            def create_module(self, spec: ModuleSpec) -> "ModuleType | None":
                return ModuleType(spec.name)

            def exec_module(self, module: ModuleType) -> None:
                if module.__name__ not in self._modules:
                    raise ImportError(module.__name__)

                sys.modules[module.__name__] = module
                if not self.is_package(module.__name__):
                    exec(self._modules[module.__name__], module.__dict__)
                else:
                    for sub_module in self._modules[module.__name__]:
                        self._modules[".".join((module.__name__, sub_module))] = self._modules[module.__name__][
                            sub_module
                        ]
                    exec(self._modules[module.__name__].get("__init__", ""), module.__dict__)

        def __init__(self, **modules: "str | dict") -> None:
            self._modules: "dict[str, str | dict]" = modules
            self._loader = StringImporter.Loader(modules)

        def find_spec(
            self,
            fullname: str,
            path: "str | None",
            target: "ModuleType | None" = None,
        ) -> "ModuleSpec | None":
            if fullname in self._modules:
                spec: ModuleSpec = spec_from_file_location(fullname, loader=self._loader)
                spec.origin = "<string>"
                return spec
            return None

    def list_files(path: Path, *, suffix: "str | None" = None) -> "list[Path]":
        files: "list[Path]" = []
        if path.is_dir():
            for file in path.iterdir():
                files.extend(list_files(file, suffix=suffix))
        elif path.is_file() and (suffix in (None, path.suffix)):
            files.append(path.absolute())
        return files

    me: Path = Path(__file__).resolve()
    my_parent: Path = me.parent

    py38_modules: "dict[str, str | dict]" = {}

    for f in list_files(my_parent, suffix=me.suffix):
        lines: "list[str]" = f.read_text(encoding="utf-8").splitlines()
        if not any(line.startswith("from __future__ import annotations") for line in lines):
            lines.insert(0, "from __future__ import annotations")
            new_text: str = "\n".join(lines)
            new_text = new_text.replace("ParamSpec", "TypeVar")
            if f.resolve() != me:
                new_text = new_text.replace("__file__", repr(str(f.resolve())))
            parts: "tuple[str, ...]" = f.relative_to(my_parent).parts
            p: "dict[str, str | dict]" = py38_modules
            for part in parts[:-1]:
                if part not in p:
                    p[part] = {}
                p = p[part]
            p[parts[-1][: -len(me.suffix)]] = new_text

    if py38_modules:
        for m in list(sys.modules):
            if m.startswith(__original_name__):
                if m in sys.modules:  # check again in case the module's gone midway
                    sys.modules.pop(m)

        sys.meta_path.insert(0, StringImporter(**{__original_name__: py38_modules}))
        if __original_name__ not in sys.modules:
            sys.modules[__original_name__] = import_module(__original_name__)


def _warn_about_outdated_package(package_name: str, package_version: str, release_time: datetime) -> None:
    """Display a warning about an outdated package a year after the package released"""
    if datetime.now(tz=timezone.utc) - release_time > timedelta(days=366):
        import tkinter.messagebox

        tkinter.messagebox.showwarning(
            title="Package Outdated", message=f"Please update {package_name} package to {package_version} or newer"
        )


def _make_old_qt_compatible_again() -> None:
    def to_iso_format(s: str) -> str:
        if sys.version_info < (3, 11, 0):
            import re
            from typing import Callable

            if s.endswith("Z"):
                # '2011-11-04T00:05:23Z'
                s = s[:-1] + "+00:00"

            def from_iso_datetime(_m: re.Match[str]) -> str:
                groups: dict[str, str] = _m.groupdict("")
                date: str = f"{_m['year']}-{_m['month']}-{_m['day']}"
                time: str = (
                    f"{groups['hour']:0>2}:{groups['minute']:0>2}:{groups['second']:0>2}.{groups['fraction']:0<6}"
                )
                return date + "T" + time + groups["offset"]

            def from_iso_calendar(_m: re.Match[str]) -> str:
                from datetime import date

                groups: dict[str, str] = _m.groupdict("")
                date: str = date.fromisocalendar(
                    year=int(_m["year"]), week=int(_m["week"]), day=int(_m["dof"])
                ).isoformat()
                time: str = (
                    f"{groups['hour']:0>2}:{groups['minute']:0>2}:{groups['second']:0>2}.{groups['fraction']:0<6}"
                )
                return date + "T" + time + groups["offset"]

            patterns: dict[str, Callable[[re.Match[str]], str]] = {
                # '20111104', '20111104T000523283'
                r"(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2})"
                r"(.(?P<hour>\d{2})(?P<minute>\d{2})(?P<second>\d{2})(?P<fraction>\d+)?)?"
                r"(?P<offset>[+\-].+)?": from_iso_datetime,
                # '2011-11-04', '2011-11-04T00:05:23.283', '2011-11-04T00:05:23.283+00:00'
                r"(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})"
                r"(.(?P<hour>\d{1,2}):(?P<minute>\d{1,2}):(?P<second>\d{1,2})(\.(?P<fraction>\d+))?)?"
                r"(?P<offset>[+\-].+)?": from_iso_datetime,
                # '2011-W01-2T00:05:23.283'
                r"(?P<year>\d{4})-W(?P<week>\d{1,2})-(?P<dof>\d{1,2})"
                r"(.(?P<hour>\d{1,2}):(?P<minute>\d{1,2}):(?P<second>\d{1,2})(\.(?P<fraction>\d+))?)?"
                r"(?P<offset>[+\-].+)?": from_iso_calendar,
                # '2011W0102T000523283'
                r"(?P<year>\d{4})-W(?P<week>\d{2})-(?P<dof>\d{2})"
                r"(.(?P<hour>\d{1,2})(?P<minute>\d{1,2})(?P<second>\d{1,2})(?P<fraction>\d+)?)?"
                r"(?P<offset>[+\-].+)?": from_iso_calendar,
            }
            match: re.Match[str] | None
            for _p in patterns:
                match = re.fullmatch(_p, s)
                if match is not None:
                    s = patterns[_p](match)
                    break

        return s

    if not QT6:
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)

    from qtpy import __version__

    if Version(__version__) < Version("2.3.1"):
        _warn_about_outdated_package(
            package_name="QtPy",
            package_version="2.3.1",
            release_time=datetime.fromisoformat(to_iso_format("2023-03-28T23:06:05Z")),
        )
        if QT6:
            QLibraryInfo.LibraryLocation = QLibraryInfo.LibraryPath
    if Version(__version__) < Version("2.4.0"):
        _warn_about_outdated_package(
            package_name="QtPy",
            package_version="2.4.0",
            release_time=datetime.fromisoformat(to_iso_format("2023-08-29T16:24:56Z")),
        )
        if PYSIDE2:
            QApplication.exec = QApplication.exec_
            QDialog.exec = QDialog.exec_

        if not QT6:
            QLibraryInfo.path = lambda *args, **kwargs: QLibraryInfo.location(*args, **kwargs)
            QLibraryInfo.LibraryPath = QLibraryInfo.LibraryLocation

        if Version(qVersion()) < Version("6.3"):
            from qtpy.QtCore import QObject
            from qtpy.QtGui import QKeySequence
            from qtpy.QtWidgets import QAction, QToolBar, QWidget

            def add_action(self: QWidget, *args, old_add_action) -> QAction:
                action: QAction
                icon: QIcon
                text: str
                shortcut: QKeySequence | QKeySequence.StandardKey | str | int
                receiver: QObject
                member: bytes
                if all(
                    isinstance(arg, t)
                    for arg, t in zip(args, [str, (QKeySequence, QKeySequence.StandardKey, str, int), QObject, bytes])
                ):
                    if len(args) == 2:
                        text, shortcut = args
                        action = old_add_action(self, text)
                        action.setShortcut(shortcut)
                    elif len(args) == 3:
                        text, shortcut, receiver = args
                        action = old_add_action(self, text, receiver)
                        action.setShortcut(shortcut)
                    elif len(args) == 4:
                        text, shortcut, receiver, member = args
                        action = old_add_action(self, text, receiver, member, shortcut)
                    else:
                        return old_add_action(self, *args)
                    return action
                elif all(
                    isinstance(arg, t)
                    for arg, t in zip(
                        args, [QIcon, str, (QKeySequence, QKeySequence.StandardKey, str, int), QObject, bytes]
                    )
                ):
                    if len(args) == 3:
                        icon, text, shortcut = args
                        action = old_add_action(self, icon, text)
                        action.setShortcut(QKeySequence(shortcut))
                    elif len(args) == 4:
                        icon, text, shortcut, receiver = args
                        action = old_add_action(self, icon, text, receiver)
                        action.setShortcut(QKeySequence(shortcut))
                    elif len(args) == 5:
                        icon, text, shortcut, receiver, member = args
                        action = old_add_action(self, icon, text, receiver, member, QKeySequence(shortcut))
                    else:
                        return old_add_action(self, *args)
                    return action
                return old_add_action(self, *args)

            QMenu.addAction = partialmethod(add_action, old_add_action=QMenu.addAction)
            QToolBar.addAction = partialmethod(add_action, old_add_action=QToolBar.addAction)
    if Version(__version__) < Version("2.4.1"):
        _warn_about_outdated_package(
            package_name="QtPy",
            package_version="2.4.1",
            release_time=datetime.fromisoformat(to_iso_format("2023-10-23T23:57:23Z")),
        )

    # not a part of any QtPy (yet)
    if PYSIDE2:
        # noinspection PyUnresolvedReferences
        QAbstractSpinBox.setAlignment = partialmethod(
            lambda self, flag, _old: _old(self, Qt.Alignment(flag)),
            _old=QAbstractSpinBox.setAlignment,
        )
        Qt.AlignmentFlag.__or__ = lambda self, other: int(self) | int(other)
        Qt.AlignmentFlag.__ror__ = lambda self, other: int(other) | int(self)

        if not hasattr(QMenu, "exec"):
            QMenu.exec = lambda self, pos: self.exec_(pos)


def qta_icon(*qta_name: str, **qta_specs: Any) -> QIcon:
    if qta_name:
        with suppress(ImportError, Exception):
            from qtawesome import icon

            return icon(*qta_name, **qta_specs)  # might raise an `Exception` if the icon is not in the font

    return QIcon()


def main() -> int:
    import re

    # fix `re.RegexFlag.NOFLAG` missing on some systems
    if not hasattr(re.RegexFlag, "NOFLAG"):
        re.RegexFlag.NOFLAG = 0

    _make_old_qt_compatible_again()

    from .ui import UI

    app: QApplication = QApplication(sys.argv)

    languages: set[str] = set(QLocale().uiLanguages() + [QLocale().bcp47Name(), QLocale().name()])
    language: str
    translations_path: str = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
    qt_translator: QTranslator = QTranslator()
    for language in languages:
        if qt_translator.load("qt_" + language, translations_path):
            QApplication.installTranslator(qt_translator)
            break
    qtbase_translator: QTranslator = QTranslator()
    for language in languages:
        if qtbase_translator.load("qtbase_" + language, translations_path):
            QApplication.installTranslator(qtbase_translator)
            break
    my_translator: QTranslator = QTranslator()
    for language in languages:
        if my_translator.load(language, str(Path(__file__).parent / "i18n")):
            QApplication.installTranslator(my_translator)
            break

    from argparse import ZERO_OR_MORE, ArgumentParser, Namespace

    ap: ArgumentParser = ArgumentParser(
        allow_abbrev=True,
        description=f"GUI for PyCatSearch.\nFind more at https://github.com/{__author__}/{__original_name__}.",
    )
    ap.add_argument("catalog", type=Path, help="the catalog location to load", nargs=ZERO_OR_MORE)
    args: Namespace = ap.parse_intermixed_args()

    window: UI = UI(Catalog(*args.catalog))
    window.show()
    return app.exec()
