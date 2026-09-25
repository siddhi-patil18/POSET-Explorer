"""Interactive Streamlit application for checking finite POSET relations."""

from __future__ import annotations

import streamlit as st

from examples import DEFAULT_EXAMPLE, EXAMPLES
from hasse_diagram import (
    build_hasse_graph,
    draw_hasse_diagram,
    find_cover_relations,
)
from parser import InputError, format_pair, parse_relation_input, parse_set_input
from poset_checker import AnalysisResult, check_poset


def reset_application() -> None:
    """Clear all user-entered state and start with the default example."""

    st.session_state.clear()
    st.rerun()


def render_property_result(property_result) -> None:
    """Show a compact result message for one mathematical property."""

    if property_result.passed:
        st.success(f"✓ {property_result.name}: TRUE")
    else:
        st.error(f"✗ {property_result.name}: FALSE")
        st.caption(property_result.failure_reason)


def render_property_steps(property_result) -> None:
    """Show the detailed checking process for one property."""

    with st.expander(
        f"{property_result.name} checking steps",
        expanded=True,
    ):
        for detail in property_result.details:
            st.markdown(f"- {detail}")

        if property_result.violations:
            st.markdown("**Violating case(s):**")

            for violation in property_result.violations:
                st.markdown(f"- `{violation}`")

        if property_result.failure_reason:
            st.warning(property_result.failure_reason)


def render_analysis(analysis: AnalysisResult) -> None:
    """Render property results, explanations, and the diagram when valid."""

    st.subheader("Relation Properties")

    result_columns = st.columns(3)

    for column, property_result in zip(
        result_columns,
        analysis.properties,
    ):
        with column:
            render_property_result(property_result)

    st.subheader("Step-by-Step Analysis")

    for step_number, property_result in enumerate(
        analysis.properties,
        start=1,
    ):
        st.markdown(
            f"**Step {step_number}: Check {property_result.name}**"
        )
        render_property_steps(property_result)

    st.divider()

    if analysis.is_poset:
        st.subheader("POSET Result")

        st.success("✓ Relation is a POSET")

        st.caption(
            "A POSET is a relation that is reflexive, antisymmetric, "
            "and transitive on the given set."
        )

        st.markdown(
            "**Step 4: Determine whether it is a POSET** — "
            "all three relation properties passed."
        )

        covers = find_cover_relations(
            analysis.elements,
            analysis.relation,
        )

        st.subheader("Hasse Diagram")

        st.write(
            "Self-relations and transitive/redundant edges have been removed. "
            "The remaining edges are the cover relations."
        )

        st.markdown(
            "**Step 5: Identify cover relations** — "
            f"{len(covers)} cover relation(s) remain."
        )

        diagram_columns = st.columns([2, 1])

        with diagram_columns[0]:
            graph = build_hasse_graph(
                analysis.elements,
                covers,
            )

            figure = draw_hasse_diagram(graph)
            st.pyplot(figure, width="stretch")

            st.markdown(
                "**Step 6: Generate the Hasse diagram** — "
                "the graph is drawn from the computed cover relations."
            )

        with diagram_columns[1]:
            st.markdown("**Cover relations kept**")

            if covers:
                for lower, upper in covers:
                    st.write(format_pair(lower, upper))
            else:
                st.info(
                    "This POSET has no edges between different elements."
                )

    else:
        st.subheader("POSET Result")

        st.error("✗ Relation is NOT a POSET")

        failed_properties = [
            item
            for item in analysis.properties
            if not item.passed
        ]

        st.write("The relation fails because:")

        for property_result in failed_properties:
            st.markdown(
                f"- **{property_result.name}:** "
                f"{property_result.failure_reason}"
            )

        st.info(
            "The Hasse diagram is shown only when all three POSET "
            "properties are true."
        )


st.set_page_config(
    page_title="Interactive Hasse Diagram Builder & POSET Property Checker",
    page_icon="∣",
    layout="wide",
)

st.title("Interactive Hasse Diagram Builder & POSET Property Checker")

st.write(
    "Enter any finite set and binary relation to check the three "
    "POSET properties. When the relation is a POSET, the app removes "
    "redundant edges and draws its Hasse diagram."
)

with st.sidebar:
    st.header("Project at a glance")

    st.write(
        "This tool demonstrates reflexivity, antisymmetry, transitivity, "
        "POSET verification, and cover-relation extraction."
    )

    st.divider()

    st.markdown("**Input tips**")
    st.write("Set: `1,2,3,6`")
    st.write("Relation: `(1,1),(1,2),(2,2)`")
    st.write("Unquoted names such as `a,b,c` are supported.")

st.header("Input")

example_name = st.selectbox(
    "Optional example",
    ["Custom input", *EXAMPLES.keys()],
)

load_column, reset_column = st.columns(2)

with load_column:
    load_example = st.button(
        "Load selected example",
        width="stretch",
    )

with reset_column:
    reset = st.button(
        "Reset / Clear",
        width="stretch",
    )

if reset:
    reset_application()

if load_example and example_name != "Custom input":
    example_set, example_relation = EXAMPLES[example_name]

    st.session_state["set_input"] = example_set
    st.session_state["relation_input"] = example_relation
    st.session_state["analysis"] = None
    st.session_state["input_error"] = None

if "set_input" not in st.session_state:
    st.session_state["set_input"] = EXAMPLES[DEFAULT_EXAMPLE][0]

if "relation_input" not in st.session_state:
    st.session_state["relation_input"] = EXAMPLES[DEFAULT_EXAMPLE][1]

if "analysis" not in st.session_state:
    st.session_state["analysis"] = None

if "input_error" not in st.session_state:
    st.session_state["input_error"] = None

with st.form("relation_form"):
    st.subheader("Set Input")

    set_input = st.text_input(
        "Finite set",
        key="set_input",
        help=(
            "Enter values separated by commas, for example "
            "1,2,3,6 or {1,2,3,6}."
        ),
    )

    st.subheader("Relation Input")

    relation_input = st.text_area(
        "Binary relation R",
        key="relation_input",
        height=120,
        help=(
            "Enter pairs separated by commas, for example "
            "(1,1),(1,2),(2,2)."
        ),
    )

    check_clicked = st.form_submit_button(
        "Check Relation",
        type="primary",
        width="stretch",
    )

if check_clicked:
    try:
        elements = parse_set_input(set_input)
        relation = parse_relation_input(relation_input)

        st.session_state["analysis"] = check_poset(
            elements,
            relation,
        )

        st.session_state["input_error"] = None

    except InputError as error:
        st.session_state["analysis"] = None
        st.session_state["input_error"] = str(error)

if st.session_state["input_error"]:
    st.error(f"Input error: {st.session_state['input_error']}")

if st.session_state["analysis"] is not None:
    st.header("Analysis")
    render_analysis(st.session_state["analysis"])
else:
    st.info(
        "Enter any finite set and binary relation, then select "
        "“Check Relation” to see the analysis."
    )

st.divider()

st.subheader("How the Algorithm Works")

st.markdown(
    """
    1. **Reflexive:** for every `a` in the set, the pair `(a,a)` must be in `R`.
    2. **Antisymmetric:** if both `(a,b)` and `(b,a)` are in `R`, then `a` must equal `b`.
    3. **Transitive:** if `(a,b)` and `(b,c)` are in `R`, then `(a,c)` must be in `R`.
    4. **POSET:** all three checks must be true.
    5. **Hasse diagram:** remove `(a,a)` and remove an edge `(a,b)` when an intermediate
       `c` makes `(a,c)` and `(c,b)` true.
    """
)