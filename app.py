import streamlit as st

from parser import (
    InputError,
    format_pair,
    parse_set_input,
    parse_relation_input,
)

from poset_checker import check_poset

from relation_generators import (
    generate_less_equal,
    generate_greater_equal,
    generate_divisibility,
    generate_identity,
    generate_from_condition,
)

from hasse_diagram import (
    build_hasse_graph,
    draw_hasse_diagram,
    find_cover_relations,
)


# Page settings
st.set_page_config(
    page_title="POSET Math Lab",
    page_icon="∑",
    layout="wide"
)


# ---------------- CLEAR STATE ----------------

if "clear_count" not in st.session_state:
    st.session_state.clear_count = 0


# ---------------- TITLE ----------------

st.markdown(
    "<h3 style='text-align:center;'>∈ ⊆ ≤ ∀ ∃ ∑</h3>",
    unsafe_allow_html=True
)

st.markdown(
    "<h1 style='text-align:center;'>POSET Explorer</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<p style='text-align:center;'>"
    "Explore relations | Discover POSETs | Visualize order"
    "</p>",
    unsafe_allow_html=True
)


# ---------------- SET ----------------

st.header("1. Enter Your Set")

set_input = st.text_input(
    "Enter set elements",
    placeholder="Example: 1,2,3,4",
    key=f"set_input_{st.session_state.clear_count}"
)


# ---------------- RELATION ----------------

st.header("2. Choose Relation")

relation_type = st.radio(
    "Relation type",
    [
        "Custom Relation",
        "Less than or equal to (≤)",
        "Greater than or equal to (≥)",
        "Divisibility",
        "Identity",
    ],
    horizontal=True
)


relation = None
relation_input = ""
condition = ""


# ---------------- CUSTOM RELATION ----------------

if relation_type == "Custom Relation":

    custom_type = st.radio(
        "Custom relation method",
        [
            "Enter pairs manually",
            "Generate using condition"
        ],
        horizontal=True
    )

    if custom_type == "Enter pairs manually":

        relation_input = st.text_area(
            "Enter relation pairs",
            placeholder="Example: (1,1),(1,2),(2,2)",
            key=f"relation_input_{st.session_state.clear_count}"
        )

    else:

        condition = st.text_input(
            "Enter condition",
            placeholder="Example: a + b < 10",
            key=f"condition_{st.session_state.clear_count}"
        )

        st.caption(
            "Use a and b. Example: a<b, a+b<10, a*b>5"
        )


# ---------------- BUTTONS ----------------

col1, col2 = st.columns(2)

with col1:
    analyze = st.button(
        "Analyze Relation",
        type="primary",
        use_container_width=True
    )

with col2:
    clear = st.button(
        "Clear",
        use_container_width=True
    )


# ---------------- CLEAR ----------------

if clear:
    st.session_state.clear_count += 1
    st.rerun()


# ---------------- ANALYZE ----------------

if analyze:

    try:

        # Read set
        elements = parse_set_input(set_input)

        # Create relation
        if relation_type == "Custom Relation":

            if custom_type == "Enter pairs manually":

                if not relation_input.strip():
                    raise InputError(
                        "Please enter relation pairs."
                    )

                relation = parse_relation_input(
                    relation_input
                )

            else:

                if not condition.strip():
                    raise InputError(
                        "Please enter a condition."
                    )

                relation = generate_from_condition(
                    elements,
                    condition
                )

        elif relation_type == "Less than or equal to (≤)":

            relation = generate_less_equal(elements)

        elif relation_type == "Greater than or equal to (≥)":

            relation = generate_greater_equal(elements)

        elif relation_type == "Divisibility":

            relation = generate_divisibility(elements)

        else:

            relation = generate_identity(elements)


        # Check POSET
        analysis = check_poset(
            elements,
            relation
        )


        # ---------------- RESULT ----------------

        st.header("3. Relation Preview")

        pairs = sorted(
            relation,
            key=lambda x: (str(x[0]), str(x[1]))
        )

        text = ", ".join(
            format_pair(a, b)
            for a, b in pairs
        )

        st.code("R = {" + text + "}")


        # ---------------- PROPERTIES ----------------

        st.header("4. Relation Analysis")

        cols = st.columns(3)

        for col, result in zip(
            cols,
            analysis.properties
        ):

            with col:

                if result.passed:
                    st.success(
                        f"✓ {result.name}\n\nTRUE"
                    )
                else:
                    st.error(
                        f"✗ {result.name}\n\nFALSE"
                    )


        # ---------------- POSET ----------------

        if analysis.is_poset:

            st.success(
                "✓ This relation is a POSET."
            )


            # Hasse diagram
            st.header("5. Hasse Diagram")

            covers = find_cover_relations(
                elements,
                relation
            )

            graph = build_hasse_graph(
                elements,
                covers
            )

            st.pyplot(
                draw_hasse_diagram(graph),
                use_container_width=False
            )


            # Cover relations
            st.subheader("Cover Relations")

            if covers:

                covers.sort(
                    key=lambda x: (
                        str(x[0]),
                        str(x[1])
                    )
                )

                text = ", ".join(
                    format_pair(a, b)
                    for a, b in covers
                )

                st.code(
                    "C = {" + text + "}"
                )

            else:

                st.info(
                    "No cover relations found."
                )

        else:

            st.warning(
                "✗ This relation is not a POSET."
            )


        # ---------------- STEP BY STEP ----------------

        st.header("6. Step-by-Step Analysis")

        for result in analysis.properties:

            with st.expander(
                result.name
            ):

                for detail in result.details:
                    st.write(detail)

                if result.failure_reason:
                    st.error(
                        result.failure_reason
                    )

                for violation in result.violations:
                    st.write(
                        "• " + violation
                    )


    except (InputError, ValueError) as e:

        st.error(str(e))