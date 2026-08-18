"""
    Financial Intelligence Workspace application entry point.

    Configures the Streamlit application, initializes shared session state,
    provides navigation between the GOS Analyzer, GOS Linker, and STR Quality
    Assessment modules, and routes user requests to the corresponding frontend
    pages.
"""

import sys
from datetime import datetime
from pathlib import Path
from style import apply_custom_css

import streamlit as st
import streamlit.components.v1 as components

from frontend_pages.gos_page import gos_analyzer_page
from frontend_pages.sqa_page import str_quality_assessment_page
from frontend_pages.gos_linker_page import gos_linker_page # <-- NEW IMPORT

from ui_helpers import (
    ANALYSIS_META,
    ANALYSIS_KEYS,
    tag_pill_html,
)

# BACKEND IMPORT - STR QUALITY ASSESSMENT

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT / "backend"))

from services.sqa.config import MODEL_NAME
from services.sqa import ui

# PAGE CONFIG
st.set_page_config(
    page_title="Financial Intelligence Workspace",
    page_icon="🗂️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# GLOBAL STYLE
apply_custom_css()

# SESSION STATE INITIALIZATION

if "text_results" not in st.session_state:
    st.session_state.text_results = {}
if "exhibit_counter" not in st.session_state:
    st.session_state.exhibit_counter = 0

# SIDEBAR — MASTER CONFIGURATION

with st.sidebar:
    st.markdown("""
    <div class='sidebar-brand'>
        <div class='brand-mark'>Financial Intelligence</div>
        <div class='brand-tag'>Workspace Control</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='section-label'>Select Mode</div>", unsafe_allow_html=True)
    app_mode = st.radio(
        "Application Mode",
        ["GOS Analyzer", "GOS Linker", "STR Quality Assessment"],
        label_visibility="collapsed"
    )

    if app_mode == "GOS Analyzer":
        st.markdown("<div class='section-label'>Input Source</div>", unsafe_allow_html=True)
        input_mode = st.radio(
            "Input Source",
            ["Text Input", "Excel Upload"],
            label_visibility="collapsed",
        )

        st.markdown("<div class='section-label'>Analysis Types</div>", unsafe_allow_html=True)

        analysis_display_options = [f"{ANALYSIS_META[k]['glyph']}  {ANALYSIS_META[k]['label']}" for k in ANALYSIS_KEYS]
        selected_display = st.multiselect(
            "Analysis Types",
            analysis_display_options,
            default=[analysis_display_options[0]],
            label_visibility="collapsed",
            help="Select one or more analysis types. Each will be run and shown as its own tagged section.",
        )

        selected_keys = [k for k, disp in zip(ANALYSIS_KEYS, analysis_display_options) if disp in selected_display]
        combo_key = tuple(selected_keys)

        if selected_keys:
            tag_list_html = "".join(
                f"<div>{tag_pill_html(k)}<div class='record-desc'>{ANALYSIS_META[k]['desc']}</div></div>"
                for k in selected_keys
            )
            st.markdown(f"<div class='sidebar-tag-list'>{tag_list_html}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<p class='record-desc'>Select at least one analysis type to continue.</p>", unsafe_allow_html=True)

        ner_label_list = None
        keyword_list = None

        if "ner" in selected_keys:
            st.markdown("<div class='section-label'>Entity Labels</div>", unsafe_allow_html=True)
            ner_labels = st.text_input("Entity Labels", value="Person, Organization, Location", label_visibility="collapsed")
            ner_label_list = [label.strip() for label in ner_labels.split(",") if label.strip()]

        if "keyword_search" in selected_keys:
            st.markdown("<div class='section-label'>Search Keywords</div>", unsafe_allow_html=True)
            search_keywords = st.text_input("Search Keywords", value="fraud, suspicious, illegal, Money Laundering", label_visibility="collapsed")
            keyword_list = [kw.strip() for kw in search_keywords.split(",") if kw.strip()]

        def extra_params_for(key):
            if key == "ner": return ner_label_list
            elif key == "keyword_search": return keyword_list
            return None
            
    elif app_mode == "GOS Linker":
        # <-- NEW SIDEBAR CONFIG FOR LINKER
        st.markdown("<p class='record-desc'>Upload multiple GOS documents to visualize interconnections across PAN, Accounts, Mobile, and Entities using graph linkages.</p>", unsafe_allow_html=True)

    elif app_mode == "STR Quality Assessment":
        ui.sidebar(MODEL_NAME)
        st.markdown("<p class='record-desc'>Evaluates STRs against key parameters and maps suitable Law Enforcement Agencies.</p>", unsafe_allow_html=True)

# DYNAMIC MASTHEAD 

if app_mode == "GOS Analyzer":
    emoji, title, sub, case_type = "🔎", "GOS Analyzer", "Ground of Suspicion — Intelligence Analysis Platform", "GOS"
elif app_mode == "GOS Linker": 
    emoji, title, sub, case_type = "🔗", "GOS Linker", "Entity Relationship & Network Linkage Visualization", "LNK"
else:
    emoji, title, sub, case_type = "⚖️", "STR Assessment", "STR Quality Evaluation & LEA Mapping", "STR"

st.markdown(f"""
<div class='classification-banner'>
    <span>Restricted — Authorized Compliance Use Only</span>
    <span class='case-ref'>SYS / {case_type} / {datetime.now().strftime('%Y-%m-%d')}</span>
</div>
<div class='masthead'>
    <div class='masthead-emblem'>{emoji}</div>
    <div>
        <div class='masthead-title'>{title}</div>
        <div class='masthead-sub'>{sub}</div>
    </div>
</div>
<hr class='masthead-rule' />
""", unsafe_allow_html=True)

# APP ROUTING 

if app_mode == "GOS Analyzer":  
    gos_analyzer_page(input_mode, combo_key, selected_keys, extra_params_for)

elif app_mode == "GOS Linker":
    gos_linker_page()

elif app_mode == "STR Quality Assessment":  
    str_quality_assessment_page()