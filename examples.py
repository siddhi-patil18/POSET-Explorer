"""Optional beginner-friendly examples for the Streamlit interface."""

from __future__ import annotations


EXAMPLES: dict[str, tuple[str, str]] = {
    "Divisibility on {1, 2, 3, 6} (POSET)": (
        "1,2,3,6",
        "(1,1),(1,2),(1,3),(1,6),"
        "(2,2),(2,6),(3,3),(3,6),(6,6)",
    ),
    "Natural order on {1, 2, 3} (POSET)": (
        "1,2,3",
        "(1,1),(1,2),(1,3),(2,2),(2,3),(3,3)",
    ),
    "Missing self-pair (not reflexive)": (
        "1,2,3",
        "(1,1),(1,2),(1,3),(2,2),(2,3)",
    ),
    "Opposite pairs (not antisymmetric)": (
        "1,2,3",
        "(1,1),(2,2),(3,3),(1,2),(2,1)",
    ),
    "Missing shortcut (not transitive)": (
        "1,2,3",
        "(1,1),(2,2),(3,3),(1,2),(2,3)",
    ),
}


DEFAULT_EXAMPLE = "Divisibility on {1, 2, 3, 6} (POSET)"