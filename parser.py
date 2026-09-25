import ast
import re


class InputError(ValueError):
    pass


def format_value(value):
    return value if isinstance(value, str) else repr(value)


def format_pair(a, b):
    return f"({format_value(a)}, {format_value(b)})"


def _split(text):
    parts = []
    current = ""
    depth = 0
    quote = None

    for ch in text:
        if quote:
            current += ch
            if ch == quote:
                quote = None
        elif ch in "'\"":
            quote = ch
            current += ch
        elif ch in "([{":
            depth += 1
            current += ch
        elif ch in ")]}":
            depth -= 1
            current += ch
        elif ch == "," and depth == 0:
            parts.append(current.strip())
            current = ""
        else:
            current += ch

    if current.strip():
        parts.append(current.strip())

    return parts


def _parse(text):
    text = text.strip()

    if not text:
        raise InputError("Empty value is not allowed.")

    try:
        value = ast.literal_eval(text)
    except (ValueError, SyntaxError):
        value = text

    try:
        hash(value)
    except TypeError:
        raise InputError("Only simple values are allowed.")

    return value


def parse_set_input(text):
    text = text.strip()

    if not text:
        raise InputError("Please enter at least one set element.")

    try:
        values = list(ast.literal_eval(text))
    except (ValueError, SyntaxError, TypeError):
        if text[0] in "{[(" and text[-1] in "}])":
            text = text[1:-1]
        values = [_parse(x) for x in _split(text)]

    if not values:
        raise InputError("Please enter at least one set element.")

    if len(values) != len(set(values)):
        raise InputError("Set elements must be unique.")

    return values


def parse_relation_input(text):
    text = text.strip()

    if not text:
        return set()

    pairs = re.findall(r"\(([^()]*)\)", text)

    if not pairs:
        raise InputError(
            "Use pairs like (1,1),(1,2),(2,2)."
        )

    relation = set()

    for pair in pairs:
        values = _split(pair)

        if len(values) != 2:
            raise InputError("Each pair must contain two values.")

        relation.add(
            (_parse(values[0]), _parse(values[1]))
        )

    if len(relation) != len(pairs):
        raise InputError("Duplicate relation pair found.")

    return relation


def validate_relation(elements, relation):
    elements = set(elements)

    for a, b in relation:
        if a not in elements or b not in elements:
            raise InputError(
                f"{format_pair(a, b)} is not in the entered set."
            )