from dataclasses import dataclass, field

from parser import (
    format_pair,
    format_value,
    validate_relation,
)


@dataclass
class PropertyResult:
    name: str
    passed: bool
    details: list[str]
    failure_reason: str | None = None
    violations: list[str] = field(default_factory=list)


@dataclass
class AnalysisResult:
    elements: list
    relation: set
    properties: list

    @property
    def is_poset(self):
        return all(p.passed for p in self.properties)


def check_reflexive(elements, relation):
    details = []
    missing = []

    for a in elements:
        pair = format_pair(a, a)

        if (a, a) in relation:
            details.append(f"{pair} is present.")
        else:
            details.append(f"{pair} is missing.")
            missing.append(pair)

    return PropertyResult(
        "Reflexive",
        not missing,
        details,
        f"Missing self-pair(s): {', '.join(missing)}." if missing else None,
        missing,
    )


def check_antisymmetric(elements, relation):
    details = []
    violations = []
    checked = set()

    for a, b in relation:
        if a == b:
            continue

        pair = frozenset((a, b))

        if pair in checked:
            continue

        checked.add(pair)

        if (b, a) in relation:
            details.append(
                f"{format_pair(a,b)} and {format_pair(b,a)} are present."
            )
            violations.append(
                f"{format_pair(a,b)} and {format_pair(b,a)}"
            )
        else:
            details.append(
                f"{format_pair(a,b)} has no reverse pair."
            )

    return PropertyResult(
        "Antisymmetric",
        not violations,
        details,
        "Opposite pairs found: " + ", ".join(violations)
        if violations else None,
        violations,
    )


def check_transitive(elements, relation):
    details = []
    violations = []

    for a, b in relation:
        for x, c in relation:

            if b != x:
                continue

            required = format_pair(a, c)

            if (a, c) in relation:
                details.append(
                    f"{format_pair(a,b)} and {format_pair(b,c)} -> "
                    f"{required} present."
                )
            else:
                details.append(
                    f"{format_pair(a,b)} and {format_pair(b,c)} -> "
                    f"{required} missing."
                )
                violations.append(required)

    return PropertyResult(
        "Transitive",
        not violations,
        details,
        "Missing pair(s): " + ", ".join(violations)
        if violations else None,
        violations,
    )


def check_poset(elements, relation):

    validate_relation(elements, relation)

    properties = [
        check_reflexive(elements, relation),
        check_antisymmetric(elements, relation),
        check_transitive(elements, relation),
    ]

    return AnalysisResult(
        elements,
        relation,
        properties,
    )


def analyze_relation(elements, relation):
    return check_poset(elements, relation)