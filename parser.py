"""Input parsing and validation for finite sets and relations."""

from __future__ import annotations

import ast
import re
from typing import Any, Iterable


class InputError(ValueError):
    """Raised when a set or relation input is invalid."""


def format_value(value: Any) -> str:
    """Return a readable value for messages and diagram labels."""

    if isinstance(value, str):
        return value

    return repr(value)


def format_pair(left: Any, right: Any) -> str:
    """Return an ordered pair in the notation used by the application."""

    return f"({format_value(left)}, {format_value(right)})"


def _split_top_level(text: str) -> list[str]:
    """Split comma-separated text without splitting nested values or quotes."""

    parts: list[str] = []
    current: list[str] = []
    depth = 0
    quote: str | None = None
    escaped = False

    for character in text:
        if quote is not None:
            current.append(character)

            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == quote:
                quote = None

            continue

        if character in {"'", '"'}:
            quote = character
            current.append(character)

        elif character in "([{":
            depth += 1
            current.append(character)

        elif character in ")]}":
            depth -= 1

            if depth < 0:
                raise InputError(
                    "An input value has unbalanced brackets."
                )

            current.append(character)

        elif character == "," and depth == 0:
            parts.append("".join(current).strip())
            current = []

        else:
            current.append(character)

    if quote is not None:
        raise InputError(
            "An input value has an unfinished quote."
        )

    if depth != 0:
        raise InputError(
            "An input value has unbalanced brackets."
        )

    final_part = "".join(current).strip()

    if final_part:
        parts.append(final_part)

    return parts


def _parse_atom(text: str) -> Any:
    """Parse a number, boolean, quoted string, or simple unquoted name."""

    token = text.strip()

    if not token:
        raise InputError(
            "A set or relation contains an empty value."
        )

    try:
        value = ast.literal_eval(token)
    except (ValueError, SyntaxError):
        # Supports inputs such as a,b,c.
        value = token

    try:
        hash(value)
    except TypeError as error:
        raise InputError(
            f"{token!r} is not a simple hashable value."
        ) from error

    return value


def _try_parse_collection(text: str) -> list[Any] | None:
    """Parse a Python-like collection when the entire input is one."""

    try:
        value = ast.literal_eval(text)
    except (ValueError, SyntaxError):
        return None

    if not isinstance(value, (set, list, tuple)):
        return None

    values = list(value)

    for item in values:
        try:
            hash(item)
        except TypeError as error:
            raise InputError(
                "Every set element must be a simple value."
            ) from error

    return values


def parse_set_input(text: str) -> list[Any]:
    """Parse 1,2,3 or {1,2,3} into unique values."""

    cleaned = text.strip()

    if not cleaned:
        raise InputError(
            "Please enter at least one set element."
        )

    values = _try_parse_collection(cleaned)

    if values is None:
        without_outer_brackets = cleaned

        if (
            len(without_outer_brackets) >= 2
            and without_outer_brackets[0] in "{[("
            and without_outer_brackets[-1] in "}])"
        ):
            without_outer_brackets = without_outer_brackets[1:-1].strip()

        values = [
            _parse_atom(part)
            for part in _split_top_level(without_outer_brackets)
        ]

    if not values:
        raise InputError(
            "Please enter at least one set element."
        )

    unique_values: list[Any] = []

    for value in values:
        if value not in unique_values:
            unique_values.append(value)

    if len(unique_values) != len(values):
        raise InputError(
            "The set contains a duplicate element. "
            "A set must have unique elements."
        )

    return unique_values


def _parse_pair(pair_text: str) -> tuple[Any, Any]:
    """Parse the two values inside one relation pair."""

    parts = _split_top_level(pair_text)

    if len(parts) != 2:
        raise InputError(
            "Each relation pair needs exactly two values, "
            f"but {pair_text!r} was found."
        )

    return _parse_atom(parts[0]), _parse_atom(parts[1])


def parse_relation_input(text: str) -> set[tuple[Any, Any]]:
    """Parse (1,1),(1,2) into a set of ordered pairs."""

    cleaned = text.strip()

    if not cleaned:
        return set()

    pair_matches = re.findall(
        r"\(([^()]*)\)",
        cleaned,
    )

    if not pair_matches:
        raise InputError(
            "Use relation pairs like (1,1),(1,2),(2,2). "
            "Quoted strings are also supported, for example ('a','b')."
        )

    leftover = re.sub(
        r"\([^()]*\)",
        "",
        cleaned,
    )

    leftover = (
        leftover
        .replace("[", "")
        .replace("]", "")
        .replace(",", "")
        .strip()
    )

    if leftover:
        raise InputError(
            f"Could not understand this relation text: {leftover!r}."
        )

    parsed_pairs = [
        _parse_pair(pair_match)
        for pair_match in pair_matches
    ]

    relation = set(parsed_pairs)

    if len(relation) != len(parsed_pairs):
        raise InputError(
            "The relation contains a duplicate pair. "
            "Each ordered pair should be entered only once."
        )

    return relation


def validate_relation(
    elements: Iterable[Any],
    relation: set[tuple[Any, Any]],
) -> None:
    """Ensure every relation pair uses values from the entered set."""

    element_set = set(elements)

    outside_pairs = [
        pair
        for pair in relation
        if pair[0] not in element_set
        or pair[1] not in element_set
    ]

    if outside_pairs:
        examples = ", ".join(
            format_pair(*pair)
            for pair in outside_pairs[:3]
        )

        raise InputError(
            f"Relation pair(s) {examples} use values "
            "that are not in the set."
        )