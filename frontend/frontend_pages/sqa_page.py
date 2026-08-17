import sys
from pathlib import Path
import pandas as pd
import streamlit as st

from utils import markdown_to_text

from ui_helpers import (
    extract_semantic_summary
)

# BACKEND IMPORT - GOS ANALYZER

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT / "backend"))

try:
    from services.main import analyze_gos
except ImportError:
    # Fallback/Mock for testing if module is not available
    def analyze_gos(*args, **kwargs):
        yield "GOS Analysis Mock Result"

# BACKEND IMPORT - STR QUALITY ASSESSMENT

from services.sqa.config import PARAMETERS, MODEL_NAME
from services.sqa.scorer import score_parameter
from services.sqa.retriever import search
from ollama import chat
from services.sqa.regex_extractor import extract_fields
from services.sqa.segmenter import semantic_segment
from services.sqa import ui

def str_quality_assessment_page():
    st.markdown("<div class='section-label'>Upload Source Document</div>", unsafe_allow_html=True)
    str_csv = st.file_uploader(label="Upload an STR", type=['csv'], label_visibility="collapsed")
    
    str_text = ""
    if str_csv:
        try:
            # MEMORY SAFE: Load only the first row to prevent OOM
            str_df = pd.read_csv(str_csv, nrows=1)
            if not str_df.empty and 'GOS' in str_df.columns:
                str_row = str_df.iloc[0, :]
                with st.container(border=True):
                    st.markdown("<div class='exhibit-badge' style='border-color:var(--text-muted); color:var(--text-secondary); margin-bottom:12px;'>UPLOADED RECORD</div>", unsafe_allow_html=True)

                    st.dataframe(str_df, use_container_width=False)
                str_text = str_row['GOS']
            else:
                st.error("Uploaded CSV must contain a 'GOS' column.")
        except Exception as e:
            st.error(f"Error reading the file: {str(e)}")

    analyze = st.button("Analyze STR", use_container_width=False)

    if analyze:
        if not str_text or not str_text.strip():
            st.error("Please provide valid STR text / upload an STR file to analyze.")
        else:
            progress = st.progress(0)
            status = st.empty()

            quality_results = {}
            total_steps = len(PARAMETERS) + 1
            current_step = 0

            regex_matches = extract_fields(str_text)

            for parameter in PARAMETERS:
                status.info(f"Scoring **{parameter.title()}**...")
                quality_results[parameter] = score_parameter(parameter, str_text, regex_matches)
                current_step += 1
                progress.progress(current_step / total_steps)

            status.info("Segmenting STR...")
            segments = semantic_segment(str_text)
            all_results = []
            semantic_summaries = []

            for i, segment in enumerate(segments):
                status.info(f"Analyzing Segment {i+1}/{len(segments)}...")
                summary = extract_semantic_summary(segment)
                semantic_summaries.append(summary)
                results = search(summary, k=5)
                all_results.extend(results)

            unique_results = {}
            for r in all_results:
                key = r["guideline"]
                if key not in unique_results or r["score"] > unique_results[key]["score"]:
                    unique_results[key] = r

            retrieved_chunks = sorted(unique_results.values(), key=lambda x: x["score"], reverse=True)
            lea_mapping = retrieved_chunks

            current_step += 1
            progress.progress(current_step / total_steps)
            progress.empty()
            status.success("Assessment Complete ✅")

            ui.render_results(
                parameters=PARAMETERS,
                quality_results=quality_results,
                lea_mapping=lea_mapping,
                retrieved_chunks=retrieved_chunks,
            )