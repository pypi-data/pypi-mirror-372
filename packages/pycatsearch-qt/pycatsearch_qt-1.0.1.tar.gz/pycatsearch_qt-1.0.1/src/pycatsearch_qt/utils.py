import html
import html.entities
import itertools
import os
import sys
from typing import Any, Iterable

from pycatsearch.utils import NAME, STOICHIOMETRIC_FORMULA, STRUCTURAL_FORMULA, CatalogEntryType

__all__ = [
    "chem_html",
    "best_name",
    "remove_html",
    "wrap_in_html",
    "ReleaseInfo",
    "latest_release",
    "update_with_pip",
    "tag",
    "p_tag",
    "a_tag",
]


def tex_to_html_entity(s: str) -> str:
    r"""
    Change LaTeX entities syntax to HTML one.
    Get ‘\alpha’ to be ‘&alpha;’ and so on.
    Unknown LaTeX entities do not get replaced.

    :param s: A line to convert
    :return: a line with all LaTeX entities renamed
    """
    word_start: int = -1
    word_started: bool = False
    backslash_found: bool = False
    _i: int = 0
    fixes: dict[str, str] = {
        "neq": "#8800",
    }
    while _i < len(s):
        _c: str = s[_i]
        if word_started and not _c.isalpha():
            word_started = False
            if s[word_start:_i] + ";" in html.entities.entitydefs:
                s = s[: word_start - 1] + "&" + s[word_start:_i] + ";" + s[_i:]
                _i += 2
            elif s[word_start:_i] in fixes:
                s = s[: word_start - 1] + "&" + fixes[s[word_start:_i]] + ";" + s[_i:]
                _i += 2
        if backslash_found and _c.isalpha() and not word_started:
            word_start = _i
            word_started = True
        backslash_found = _c == "\\"
        _i += 1
    if word_started:
        if s[word_start:_i] + ";" in html.entities.entitydefs:
            s = s[: word_start - 1] + "&" + s[word_start:_i] + ";" + s[_i:]
            _i += 2
        elif s[word_start:_i] in fixes:
            s = s[: word_start - 1] + "&" + fixes[s[word_start:_i]] + ";" + s[_i:]
            _i += 2
    return s


def chem_html(formula: str) -> str:
    """converts plain text chemical formula into html markup"""
    if "<" in formula or ">" in formula:
        # we can not tell whether it's a tag or a mathematical sign
        return formula

    def sub_tag(s: str) -> str:
        return "<sub>" + s + "</sub>"

    def sup_tag(s: str) -> str:
        return "<sup>" + s + "</sup>"

    def i_tag(s: str) -> str:
        return "<i>" + s + "</i>"

    def subscript(s: str) -> str:
        number_start: int = -1
        number_started: bool = False
        cap_alpha_started: bool = False
        low_alpha_started: bool = False
        _i: int = 0
        while _i < len(s):
            _c: str = s[_i]
            if number_started and not _c.isdigit():
                number_started = False
                s = s[:number_start] + sub_tag(s[number_start:_i]) + s[_i:]
                _i += 1
            if (cap_alpha_started or low_alpha_started) and _c.isdigit() and not number_started:
                number_start = _i
                number_started = True
            if low_alpha_started:
                cap_alpha_started = False
                low_alpha_started = False
            if cap_alpha_started and _c.islower() or _c == ")":
                low_alpha_started = True
            cap_alpha_started = _c.isupper()
            _i += 1
        if number_started:
            s = s[:number_start] + sub_tag(s[number_start:])
        return s

    def prefix(s: str) -> str:
        no_digits: bool = False
        _i: int = len(s)
        while not no_digits:
            _i = s.rfind("-", 0, _i)
            if _i == -1:
                break
            if s[:_i].isalpha() and s[:_i].isupper():
                break
            no_digits = True
            _c: str
            unescaped_prefix: str = html.unescape(s[:_i])
            for _c in unescaped_prefix:
                if _c.isdigit() or _c == "<":
                    no_digits = False
                    break
            if no_digits and (unescaped_prefix[0].islower() or unescaped_prefix[0] == "("):
                return i_tag(s[:_i]) + s[_i:]
        return s

    def charge(s: str) -> str:
        if s[-1] in "+-":
            return s[:-1] + sup_tag(s[-1])
        return s

    def v(s: str) -> str:
        if "=" not in s:
            return s[0] + " = " + s[1:]
        ss: list[str] = list(map(str.strip, s.split("=")))
        for _i in range(len(ss)):
            if ss[_i].startswith("v"):
                ss[_i] = ss[_i][0] + sub_tag(ss[_i][1:])
        return " = ".join(ss)

    html_formula: str = html.escape(formula)
    html_formula_pieces: list[str] = list(map(str.strip, html_formula.split(",")))
    for i in range(len(html_formula_pieces)):
        if html_formula_pieces[i].startswith("v"):
            html_formula_pieces = html_formula_pieces[:i] + [", ".join(html_formula_pieces[i:])]
            break
    for i in range(len(html_formula_pieces)):
        if html_formula_pieces[i].startswith("v"):
            html_formula_pieces[i] = v(html_formula_pieces[i])
            break
        for function in (subscript, prefix, charge):
            html_formula_pieces[i] = function(html_formula_pieces[i])
    html_formula = ", ".join(html_formula_pieces)
    return html_formula


def is_good_html(text: str) -> bool:
    """Basic check that all tags are sound"""
    _1, _2, _3 = text.count("<"), text.count(">"), 2 * text.count("</")
    return _1 == _2 and _1 == _3


def best_name(entry: CatalogEntryType, allow_html: bool = True) -> str:
    species_tag: int = entry.speciestag
    last: str = best_name.__dict__.get("last", dict()).get(species_tag, dict()).get(allow_html, "")
    if last:
        return last

    def _best_name() -> str:
        if isotopolog := entry.isotopolog:
            if allow_html:
                if is_good_html(str(molecule_symbol := entry.moleculesymbol)) and (
                    entry.structuralformula == isotopolog or entry.stoichiometricformula == isotopolog
                ):
                    if state_html := entry.state_html:
                        # span tags are needed when the molecule symbol is malformed
                        return f"<span>{molecule_symbol}</span>, {chem_html(tex_to_html_entity(str(state_html)))}"
                    return str(molecule_symbol)
                else:
                    if state_html := entry.state_html:
                        return f"{chem_html(str(isotopolog))}, {chem_html(tex_to_html_entity(str(state_html)))}"
                    return chem_html(str(isotopolog))
            else:
                if state_html := entry.state_html:
                    return f"{isotopolog}, {remove_html(tex_to_html_entity(state_html))}"
                if state := entry.state:
                    return f"{isotopolog}, {remove_html(tex_to_html_entity(state.strip('$')))}"
                return isotopolog

        for key in (NAME, STRUCTURAL_FORMULA, STOICHIOMETRIC_FORMULA):
            if candidate := getattr(entry, key, ""):
                return chem_html(str(candidate)) if allow_html else str(candidate)
        if trivial_name := entry.trivialname:
            return str(trivial_name)
        if species_tag:
            return str(species_tag)
        return "no name"

    res: str = _best_name()
    if not species_tag:
        return res
    if "last" not in best_name.__dict__:
        best_name.__dict__["last"] = dict()
    if species_tag not in best_name.__dict__["last"]:
        best_name.__dict__["last"][species_tag] = dict()
    best_name.__dict__["last"][species_tag][allow_html] = res
    return res


def remove_html(line: str) -> str:
    """removes HTML tags and decodes HTML entities"""
    if not is_good_html(line):
        return html.unescape(line)

    new_line: str = line
    tag_start: int = new_line.find("<")
    tag_end: int = new_line.find(">", tag_start)
    while tag_start != -1 and tag_end != -1:
        new_line = new_line[:tag_start] + new_line[tag_end + 1 :]
        tag_start = new_line.find("<")
        tag_end = new_line.find(">", tag_start)
    return html.unescape(new_line).lstrip()


def wrap_in_html(text: str, line_end: str = os.linesep) -> str:
    """Make a full HTML document out of a piece of the markup"""
    new_text: list[str] = [
        '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">',
        '<html lang="en" xml:lang="en">',
        "<head>",
        '<meta http-equiv="content-type" content="text/html; charset=utf-8">',
        "</head>",
        "<body>",
        text,
        "</body>",
        "</html>",
    ]

    return line_end.join(new_text)


class ReleaseInfo:
    def __init__(self, version: str = "", pub_date: str = "") -> None:
        self.version: str = version
        self.pub_date: str = pub_date

    def __bool__(self) -> bool:
        return bool(self.version) and bool(self.pub_date)

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, (str, ReleaseInfo)):
            raise TypeError("The argument must be a string or ReleaseInfo")
        if isinstance(other, str):
            other = ReleaseInfo(version=other)
        i: str
        j: str
        for i, j in itertools.zip_longest(
            self.version.replace("-", ".").split("."), other.version.replace("-", ".").split("."), fillvalue=""
        ):
            if i == j:
                continue
            if i.isdigit() and j.isdigit():
                return int(i) < int(j)
            else:
                i_digits: str = "".join(itertools.takewhile(str.isdigit, i))
                j_digits: str = "".join(itertools.takewhile(str.isdigit, j))
                if i_digits != j_digits:
                    if i_digits and j_digits:
                        return int(i_digits) < int(j_digits)
                    else:
                        return i_digits < j_digits
                return i < j
        return False

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, (str, ReleaseInfo)):
            raise TypeError("The argument must be a string or ReleaseInfo")
        if isinstance(other, str):
            other = ReleaseInfo(version=other)
        return self.version == other.version


def latest_release() -> ReleaseInfo:
    import urllib.request
    import xml.dom.minidom as dom
    from http.client import HTTPResponse
    from urllib.error import URLError
    from xml.dom.minicompat import NodeList

    from . import __original_name__

    try:
        r: HTTPResponse = urllib.request.urlopen(
            f"https://pypi.org/rss/project/{__original_name__}/releases.xml", timeout=1
        )
    except URLError:
        return ReleaseInfo()
    if r.getcode() != 200 or not r.readable():
        return ReleaseInfo()
    rss: dom.Node | None = dom.parseString(r.read().decode(encoding="ascii")).documentElement
    if not isinstance(rss, dom.Element) or rss.tagName != "rss":
        return ReleaseInfo()
    channels: NodeList = rss.getElementsByTagName("channel")
    if not channels or channels[0].nodeType != dom.Node.ELEMENT_NODE:
        return ReleaseInfo()
    channel: dom.Element = channels[0]
    items: NodeList = channel.getElementsByTagName("item")
    if not items or items[0].nodeType != dom.Node.ELEMENT_NODE:
        return ReleaseInfo()
    item: dom.Element = items[0]
    titles: NodeList = item.getElementsByTagName("title")
    if not titles or titles[0].nodeType != dom.Node.ELEMENT_NODE:
        return ReleaseInfo()
    title: dom.Element = titles[0]
    pub_dates: NodeList = item.getElementsByTagName("pubDate")
    if not pub_dates or pub_dates[0].nodeType != dom.Node.ELEMENT_NODE:
        return ReleaseInfo()
    pub_date: dom.Element = pub_dates[0]
    title_value: dom.Node = title.firstChild
    pub_date_value: dom.Node = pub_date.firstChild
    if not isinstance(title_value, dom.Text) or not isinstance(pub_date_value, dom.Text):
        return ReleaseInfo()

    return ReleaseInfo(title_value.data, pub_date_value.data)


def update_with_pip() -> None:
    import subprocess
    import sys

    from . import __original_name__

    subprocess.Popen(
        args=[
            sys.executable,
            "-c",
            f"""import sys, subprocess, time; time.sleep(2);\
        subprocess.run(args=[sys.executable, '-m', 'pip', 'install', '-U', {__original_name__!r}]);\
        subprocess.Popen(args=[sys.executable, '-m', {__original_name__!r}])""",
        ]
    )
    sys.exit(0)


def tag(name: str, text: str = "", **attrs: str) -> str:
    parts: list[str] = ["<", " ".join((name, *itertools.starmap(lambda a, v: f"{a}={str(v)!r}", attrs.items())))]
    if text:
        parts.extend([">", text, "</", name, ">"])
    else:
        parts.append("/>")
    return "".join(parts)


def p_tag(text: str) -> str:
    return tag("p", text)


def a_tag(text: str, url: str) -> str:
    return tag("a", text, href=url)


if sys.version_info < (3, 10, 0):
    import builtins

    # noinspection PyShadowingBuiltins,PyUnusedLocal
    def zip(*iterables: Iterable[Any], strict: bool = False) -> builtins.zip:
        """Intentionally override `builtins.zip` to ignore `strict` parameter in Python < 3.10"""
        return builtins.zip(*iterables)

    __all__.append("zip")
