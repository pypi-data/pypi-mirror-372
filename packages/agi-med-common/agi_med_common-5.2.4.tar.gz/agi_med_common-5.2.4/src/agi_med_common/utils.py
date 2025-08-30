import codecs
import json
import os
from collections.abc import Iterable
from datetime import datetime
from pathlib import Path


def make_session_id() -> str:
    return f"{datetime.now():%Y-%m-%d--%H-%M-%S}"


def read_json(path: Path | os.PathLike[str] | str) -> list | dict:
    with codecs.open(path, "r", encoding="utf8") as file:
        return json.load(file)


def try_parse_json(text: str | None) -> str | None:
    # taken from agi_med_common
    if not isinstance(text, str):
        return None
    if not text:
        return None
    if text[0] not in "{[":
        return None
    if text[-1] not in "}]":
        return None
    try:
        return json.loads(text)
    except Exception:
        return None


def try_parse_int(text: str) -> int | None:
    try:
        return int(text)
    except (ValueError, TypeError):
        return None


def try_parse_float(text: str) -> float | None:
    try:
        return float(text)
    except (ValueError, TypeError):
        return None


def try_parse_bool(v: str | bool | int) -> bool:
    if isinstance(v, bool):
        return v
    if isinstance(v, int):
        return bool(v)
    return v.lower() in ("yes", "true", "t", "1")


def pretty_line(text: str, cut_count: int = 100) -> str:
    if len(text) > 100:
        text_cut = text[:cut_count]
        size = len(text)
        text_pretty = f"{text_cut}..(total {size} characters)"
    else:
        text_pretty = text
    text_pretty = text_pretty.replace("\n", "\\n")
    return text_pretty


def first_nonnull(obj: Iterable):
    for elem in obj:
        if elem:
            return elem
    return None
