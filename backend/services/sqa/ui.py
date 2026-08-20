import streamlit as st
import pandas as pd


# Sidebar

def sidebar(model_name):
    with st.sidebar:
        st.write(f"Model Name: {model_name}")


# Header

def header():

    st.title("STR Analysis Dashboard")

    st.caption(
        "Recommends LEAs based on relevant RBI Guidelines, "
        "explains reasoning, and evaluates STR quality."
    )


# LEA Results

def lea_results(lea_results):

    st.header("Recommended LEAs")

    if not lea_results:
        st.warning("No matching dissemination guideline found.")
        return

    lea_scores = {}

    for result in lea_results:

        for lea in result["target_leas"]:

            lea_scores.setdefault(lea, 0)

            lea_scores[lea] += result["score"]

    ranked = sorted(
        lea_scores.items(),
        key=lambda x: x[1],
        reverse=True,
    )

    cols = st.columns(min(4, len(ranked)))

    for col, (lea, score) in zip(cols, ranked):

        with col:

            st.metric(
                lea,
                f"{score:.2f}"
            )


# Retrieved Context

def retrieved_context(results):

    st.header("📚 Retrieved Guideline Chunks")

    if not results:
        st.info("No retrieved context.")
        return

    rows = []

    for r in results:

        rows.append(
            {
                "Similarity": round(r["score"], 3),
                "Category": r["category"],
                "Guideline": r["guideline"],
                "LEAs": ", ".join(r["target_leas"])
            }
        )

    st.dataframe(
        pd.DataFrame(rows),
        hide_index=True,
        use_container_width=True,
    )


# Overall Quality

def overall_results(results):

    st.header("📊 Overall STR Quality")

    total = sum(r["score"] for r in results.values())

    max_score = len(results) * 5

    pct = total / max_score * 100

    if pct >= 90:
        rating = "🟢 Excellent"

    elif pct >= 75:
        rating = "🟢 Good"

    elif pct >= 60:
        rating = "🟡 Average"

    elif pct >= 45:
        rating = "🟠 Poor"

    else:
        rating = "🔴 Very Poor"

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Overall Score",
        f"{total}/{max_score}"
    )

    c2.metric(
        "Percentage",
        f"{pct:.1f}%"
    )

    c3.metric(
        "Rating",
        rating
    )

    st.progress(pct / 100)

    st.divider()


# Parameter Assessment

def parameter_tabs(parameters, results):

    st.header("📝 Parameter Assessment")

    tabs = st.tabs(
        [p.title() for p in parameters]
    )

    for tab, parameter in zip(tabs, parameters):

        result = results[parameter]

        with tab:

            st.metric(
                "Score",
                f"{result['score']}/5"
            )

            st.progress(
                result["score"] / 5
            )

            left, right = st.columns(2)

            with left:

                st.success("Present")

                for item in result.get(
                    "present",
                    []
                ):
                    st.write(f"✅ {item}")

            with right:

                st.error("Missing")

                for item in result.get(
                    "missing",
                    []
                ):
                    st.write(f"❌ {item}")

            st.markdown("### Reason")

            st.info(
                result.get(
                    "reason",
                    ""
                )
            )


# Summary

def summary(
    parameters,
    results,
    lea_results=None,
    retrieved=None,
):

    st.header("📋 Summary")

    data = []

    for p in parameters:

        data.append(
            {
                "Parameter": p.title(),
                "Score": results[p]["score"]
            }
        )

    st.dataframe(
        pd.DataFrame(data),
        hide_index=True,
        use_container_width=True
    )


# Complete Page

def render_results(
    parameters,
    quality_results,
    lea_mapping,
    retrieved_chunks,
):

    lea_results(lea_mapping)

    st.divider()

    retrieved_context(retrieved_chunks)

    st.divider()

    overall_results(quality_results)

    parameter_tabs(
        parameters,
        quality_results
    )

    st.divider()

    summary(
        parameters,
        quality_results,
        lea_mapping,
        retrieved_chunks,
    )