"""Generalized POSET property checks with mathematical explanations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from parser import (
    InputError,
    format_pair,
    format_value,
    validate_relation,
)


@dataclass
class PropertyResult:
    """Result, working details, and violations for one property."""

    name: str
    passed: bool
    details: list[str]
    failure_reason: str | None = None
    violations: list[str] = field(default_factory=list)


@dataclass
class AnalysisResult:
    """Complete analysis of a finite set and user-defined relation."""

    elements: list[Any]
    relation: set[tuple[Any, Any]]
    properties: list[PropertyResult]

    @property
    def is_poset(self) -> bool:
        """Return true exactly when all three POSET properties pass."""

        return all(
            property_result.passed
            for property_result in self.properties
        )


def _summarize(
    items: list[str],
    limit: int = 8,
) -> str:
    """Keep failure messages readable for large relations."""

    if len(items) <= limit:
        return "; ".join(items)

    remaining = len(items) - limit

    return (
        f"{'; '.join(items[:limit])}; "
        f"and {remaining} more"
    )


def check_reflexive(
    elements: list[Any],
    relation: set[tuple[Any, Any]],
) -> PropertyResult:
    """Check whether every element a has the pair (a,a)."""

    details: list[str] = []
    missing_pairs: list[str] = []

    for element in elements:
        pair_text = format_pair(element, element)

        if (element, element) in relation:
            details.append(
                f"{pair_text} is present in R."
            )
        else:
            details.append(
                f"{pair_text} is missing from R."
            )
            missing_pairs.append(pair_text)

    if missing_pairs:
        return PropertyResult(
            name="Reflexive",
            passed=False,
            details=details,
            failure_reason=(
                "Missing required self-pair(s): "
                f"{_summarize(missing_pairs)}."
            ),
            violations=missing_pairs,
        )

    return PropertyResult(
        name="Reflexive",
        passed=True,
        details=details,
    )


def check_antisymmetric(
    elements: list[Any],
    relation: set[tuple[Any, Any]],
) -> PropertyResult:
    """Check that opposite pairs imply equal elements."""

    del elements

    details: list[str] = []
    violations: list[str] = []
    checked_unordered_pairs: set[frozenset[Any]] = set()

    ordered_pairs = sorted(
        relation,
        key=lambda pair: (
            format_value(pair[0]),
            format_value(pair[1]),
        ),
    )

    for left, right in ordered_pairs:
        if left == right:
            continue

        unordered_pair = frozenset({left, right})

        if unordered_pair in checked_unordered_pairs:
            continue

        checked_unordered_pairs.add(unordered_pair)

        forward = format_pair(left, right)
        reverse = format_pair(right, left)

        if (right, left) in relation:
            details.append(
                f"Checked {forward} and {reverse}: "
                "both are present."
            )

            violations.append(
                f"{forward} and {reverse}"
            )
        else:
            details.append(
                f"Checked {forward}: the reverse pair "
                f"{reverse} is not present."
            )

    if violations:
        return PropertyResult(
            name="Antisymmetric",
            passed=False,
            details=details,
            failure_reason=(
                "Opposite pairs with different elements were found: "
                f"{_summarize(violations)}."
            ),
            violations=violations,
        )

    return PropertyResult(
        name="Antisymmetric",
        passed=True,
        details=details or [
            "There are no distinct off-diagonal pairs to compare."
        ],
    )


def check_transitive(
    elements: list[Any],
    relation: set[tuple[Any, Any]],
) -> PropertyResult:
    """Check every (a,b),(b,c) chain for the required (a,c)."""

    del elements

    details: list[str] = []
    violations: list[str] = []

    ordered_pairs = sorted(
        relation,
        key=lambda pair: (
            format_value(pair[0]),
            format_value(pair[1]),
        ),
    )

    for first, middle in ordered_pairs:
        for second_middle, last in ordered_pairs:
            if middle != second_middle:
                continue

            first_pair = format_pair(first, middle)
            second_pair = format_pair(middle, last)
            required_pair = format_pair(first, last)

            if (first, last) in relation:
                details.append(
                    f"{first_pair} and {second_pair} → "
                    f"{required_pair} is present."
                )
            else:
                details.append(
                    f"{first_pair} and {second_pair} → "
                    f"{required_pair} is missing."
                )

                violations.append(
                    f"{first_pair}, {second_pair} "
                    f"require {required_pair}"
                )

    if violations:
        return PropertyResult(
            name="Transitive",
            passed=False,
            details=details,
            failure_reason=(
                "Missing shortcut pair(s): "
                f"{_summarize(violations)}."
            ),
            violations=violations,
        )

    return PropertyResult(
        name="Transitive",
        passed=True,
        details=details or [
            "There are no composable relation pairs to check."
        ],
    )


def check_poset(
    elements: list[Any],
    relation: set[tuple[Any, Any]],
) -> AnalysisResult:
    """Validate and check reflexivity, antisymmetry, and transitivity."""

    validate_relation(elements, relation)

    properties = [
        check_reflexive(elements, relation),
        check_antisymmetric(elements, relation),
        check_transitive(elements, relation),
    ]

    return AnalysisResult(
        elements=elements,
        relation=relation,
        properties=properties,
    )


def analyze_relation(
    elements: list[Any],
    relation: set[tuple[Any, Any]],
) -> AnalysisResult:
    """Backward-compatible alias for check_poset."""

    return check_poset(elements, relation)


__all__ = [
    "AnalysisResult",
    "InputError",
    "PropertyResult",
    "analyze_relation",
    "check_antisymmetric",
    "check_poset",
    "check_reflexive",
    "check_transitive",
    "format_pair",
    "format_value",
]