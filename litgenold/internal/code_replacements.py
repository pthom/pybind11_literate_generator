from dataclasses import dataclass
from typing import List
import re


@dataclass
class StringReplacement:
    replace_what: str = ""
    by_what: str = ""


def _parse_string_replacement(line: str) -> StringReplacement:
    """
    Parses a string of the form
    cv::Matx33d::eye() -> np.eye(3)
    """
    items = line.split(" -> ")
    r = StringReplacement()
    r.replace_what = items[0].strip()
    r.by_what = items[1].strip()
    if r.by_what == "REMOVE":
        r.by_what = ""
    return r


def _parse_string_replacements(lines: str) -> List[StringReplacement]:
    lines_vec = lines.split("\n")
    lines_vec = list(lines_vec)
    lines_vec = map(lambda s: s.strip(), lines_vec)
    lines_vec = list(lines_vec)
    lines_vec = filter(lambda s: len(s) > 0, lines_vec)
    lines_vec = list(lines_vec)
    r = list(map(_parse_string_replacement, lines_vec))
    return r


def opencv_replacements() -> List[StringReplacement]:
    replacements = r"""
    \bcv::Size\(\) -> (0, 0)
    \bcv::Point\(-1, -1\) -> (-1, -1)
    \bcv::Point2d\(-1., -1.\) -> (-1., -1.)
    \bcv::Size\b -> Size
    \bcv::Matx33d::eye\(\) -> np.eye(3)
    \bcv::Matx33d\b -> Matx33d
    \bcv::Mat\b -> np.ndarray
    \bcv::Point\b -> Point
    \bcv::Point2d\b -> Point2d
    """
    return _parse_string_replacements(replacements)


def standard_replacements() -> List[StringReplacement]:
    replacements = r"""
    \buint8_t\b -> int
    \bint8_t\b -> int
    \buint16_t\b -> int
    \bint16_t\b -> int
    \buint32_t\b -> int
    \bint32_t\b -> int
    \buint64_t\b -> int
    \bint64_t\b -> int
    \blong double\b -> float
    \bdouble\b -> float
    \blong\b -> int
    
    \bconst char*\b -> str
    \bconst char *\b -> str
    
    \bsize_t\b -> int
    \bstd::string\(\) -> ""
    \bstd::string\b -> str
    \btrue\b -> True
    \bfalse\b -> False
    \bstd::vector<([\w:]*)> -> list[\1]
    \bvoid\b -> None
    
    \bpy::array\b -> numpy.ndarray
    
    \bconst\b -> REMOVE
    & -> REMOVE
    \* -> REMOVE
    """
    return _parse_string_replacements(replacements)


def apply_one_replacement(s: str, replacement: StringReplacement):
    regex = replacement.replace_what
    subst = replacement.by_what
    r, nb = re.subn(regex, subst , s)
    return r


def apply_code_replacements(s: str, replacements: List[StringReplacement]) -> str:
    r = s
    for replacement in replacements:
        r = apply_one_replacement(r, replacement)
    return r