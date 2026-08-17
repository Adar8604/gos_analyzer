import sys
import json
from pathlib import Path
from datetime import datetime
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT / "backend"))

import streamlit.components.v1 as components
from ollama import chat
from services.sqa.config import MODEL_NAME

# STATIC METADATA

ANALYSIS_META = {
    "summary": {
        "label": "Overall Analysis",
        "glyph": "◆",
        "color": "gold",
        "desc": "Consolidated narrative summary of the suspicious activity.",
    },
    "ner": {
        "label": "NER Extraction",
        "glyph": "●",
        "color": "teal",
        "desc": "Named entities referenced in the report — people, orgs, places.",
    },
    "offence": {
        "label": "Offence Details",
        "glyph": "▲",
        "color": "red",
        "desc": "Predicate offence and relevant statutory indicators.",
    },
    "transaction": {
        "label": "Transaction Summary",
        "glyph": "■",
        "color": "blue",
        "desc": "Flow of funds and transaction pattern described in the report.",
    },
    "keyword_search": {
        "label": "Keyword Search",
        "glyph": "★",
        "color": "teal", 
        "desc": "Highlights exact occurrences of specified keywords in the text.",
    },
}

ANALYSIS_KEYS = list(ANALYSIS_META.keys())

COLUMN_MAP = {
    "summary": "Summary",
    "ner": "NER Extraction",
    "offence": "Offence Details",
    "transaction": "Transaction Summary",
    "keyword_search": "Keyword Search",
}

def color_var(name):
    return {"gold": "var(--gold)", "teal": "var(--teal)", "red": "var(--red)", "blue": "var(--blue)"}[name]

def color_soft_var(name):
    return {"gold": "var(--gold-soft)", "teal": "var(--teal-soft)", "red": "var(--red-soft)", "blue": "var(--blue-soft)"}[name]

def timestamp():
    return datetime.now().strftime("%H:%M:%S")

def tag_pill_html(analysis_key):
    meta = ANALYSIS_META[analysis_key]
    color = color_var(meta["color"])
    soft = color_soft_var(meta["color"])
    return (
        f"<span class='tag-pill' style='background:{soft}; border:1px solid {color}; color:{color};'>"
        f"{meta['glyph']} {meta['label']}</span>"
    )

def container_header(number_label, number, timestamp_str):
    st.markdown(f"""
    <div class='exhibit-stripe'></div>
    <div class='exhibit-header'>
        <span class='exhibit-badge'>{number_label} {number}</span>
        <span class='exhibit-time'>{timestamp_str}</span>
    </div>
    """, unsafe_allow_html=True)

def build_tagged_text(selected_keys, text_by_key):
    parts = []
    for key in selected_keys:
        label = ANALYSIS_META[key]["label"].upper()
        parts.append(f"[{label}]\n{text_by_key.get(key, '')}")
    return "\n\n".join(parts)

def copy_button(text):
    # json.dumps handles all quotes, newlines, and special characters flawlessly for JavaScript
    safe_text = json.dumps(text)
    
    # We move the logic to a script block so we don't have to worry about HTML attribute escaping
    copy_html = f"""
        <script>
        function copyToClipboard() {{
            navigator.clipboard.writeText({safe_text}).then(function() {{
                const btn = document.getElementById('copy-btn');
                btn.innerHTML = 'Copied!';
                setTimeout(() => btn.innerHTML = 'Copy All', 2000);
            }});
        }}
        </script>
        <button id="copy-btn" onclick="copyToClipboard()"
                style="background:#141F35; color:#E8EDF4; border:1px solid #243450; padding:6px 10px;
                border-radius:8px; cursor:pointer; font-weight:600; width:100%;
                font-family:'Inter',sans-serif; font-size:13px;">
            Copy All
        </button>
    """
    components.html(copy_html, height=40)

# HELPERS - STR QUALITY ASSESSMENT

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

Return only these two lines.

STR:
{str_text}
"""
    response = chat(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}]
    )
    return response["message"]["content"].strip()