import streamlit as st

from config import PARAMETERS, MODEL_NAME
from scorer import score_parameter
from retriever import search
from ollama import chat
from regex_extractor import extract_fields
from segmenter import semantic_segment
import pandas as pd

import ui

def extract_semantic_summary(str_text):

    prompt = f"""
You are an Anti-Money Laundering (AML) analyst.

Your task is to convert the following Suspicious Transaction Report (STR) into a standardized AML semantic description for vector search against RBI AML guidelines.

Objective:
Produce a concise semantic representation that captures only the suspicious behaviour described in the STR so that it closely matches RBI guideline language.

Instructions:

1. Focus ONLY on the suspicious activity.
2. Ignore customer names, account numbers, PAN, Aadhaar, addresses, phone numbers, emails, IFSC codes, transaction reference numbers, branch names, and other identifying information.
3. Do NOT summarize the entire STR.
4. Do NOT infer crimes that are not explicitly supported.
5. Do NOT introduce terms such as money laundering, layering, round tripping, shell company, hawala, terrorist financing, mule account, pass-through account, etc. unless the STR clearly describes those behaviours.
6. Use only behaviours and patterns directly supported by the STR.
7. Preserve important transaction characteristics including:
   - newly opened account
   - high transaction volume
   - rapid inflow/outflow
   - transaction velocity
   - customer profile mismatch
   - income mismatch
   - multiple counterparties
   - electronic fund transfers
   - cash/non-cash behaviour
   - geographic risk
   - foreign remittances
   - unusual turnover
   - no apparent economic rationale
   - transaction inconsistency
   - funnel account behaviour
   - structured transactions
   - suspicious cash activity
   (include only those actually present)
8. Use terminology similar to RBI AML guideline descriptions.
9. Do not mention RBI, STR filing, reporting entity, investigation, recommendation, or law enforcement.
10. Keep the output factual and objective.

Output Format:

Line 1:
One concise sentence describing the suspicious transaction behaviour.

Line 2:
Comma-separated AML concepts, transaction patterns, and synonyms extracted from the STR.

Example Output:

Newly opened account receiving high-volume electronic credits followed by immediate outward transfers inconsistent with the customer's declared business profile and income.

newly opened account, high-volume inflow/outflow, rapid electronic credits, immediate outward transfers, business profile mismatch, income mismatch, multiple counterparties, high transaction velocity, unusual turnover, electronic fund transfers, no apparent economic rationale

Return only these two lines.

STR:
{str_text}
"""

    response = chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"].strip()

st.set_page_config(
    page_title="STR Assessment & LEA Mapper",
    layout="wide",
)

ui.header()

str_csv = st.file_uploader(label="Upload an STR", type='.csv')
if str_csv:
    str_ = pd.read_csv(str_csv).iloc[0,:]
    st.write(str_)
    str_text = str_['GOS']


analyze = st.button(
    "Analyze STR",
    use_container_width=True,
)

if analyze:

    if not str_text.strip():
        st.error("Please enter an STR.")
        st.stop()

    progress = st.progress(0)
    status = st.empty()

    quality_results = {}

    total_steps = len(PARAMETERS) + 1
    current_step = 0

    regex_matches = extract_fields(str_text)


    # Quality Assessment

    for parameter in PARAMETERS:

        status.info(f"Scoring **{parameter.title()}**...")

        quality_results[parameter] = score_parameter(
        parameter,
        str_text,
        regex_matches,
    )

        current_step += 1
        progress.progress(current_step / total_steps)

    # Retrieve LEA Recommendations

    status.info("Segmenting STR...")

    segments = semantic_segment(str_text)

    all_results = []
    semantic_summaries = []

    for i, segment in enumerate(segments):

        status.info(
            f"Analyzing Segment {i+1}/{len(segments)}..."
        )

        summary = extract_semantic_summary(segment)

        semantic_summaries.append(summary)

        results = search(
            summary,
            k=5,
        )

        all_results.extend(results)

    # Remove duplicate guidelines

    unique_results = {}

    for r in all_results:

        key = r["guideline"]

        if (
            key not in unique_results
            or r["score"] > unique_results[key]["score"]
        ):
            unique_results[key] = r

    retrieved_chunks = sorted(
        unique_results.values(),
        key=lambda x: x["score"],
        reverse=True,
    )

    lea_mapping = retrieved_chunks

    current_step += 1
    progress.progress(current_step / total_steps)

    progress.empty()

    status.success("Assessment Complete ✅")