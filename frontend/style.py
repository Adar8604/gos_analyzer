import streamlit as st

def apply_custom_css():
    st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700&family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

:root{
    --bg:#0A1220;
    --bg-elevated:#0F1A2C;
    --panel:#141F35;
    --panel-alt:#182545;
    --border:#243450;
    --border-soft:#1B2740;
    --text-primary:#E8EDF4;
    --text-secondary:#8CA0BC;
    --text-muted:#5B7089;

    --gold:#C9A227;      --gold-soft:rgba(201,162,39,0.14);
    --teal:#3E8E7E;      --teal-soft:rgba(62,142,126,0.16);
    --red:#C0524A;       --red-soft:rgba(192,82,74,0.16);
    --blue:#4C7EA8;      --blue-soft:rgba(76,126,168,0.16);

    --font-serif:'Source Serif 4', Georgia, serif;
    --font-sans:'Inter', -apple-system, sans-serif;
    --font-mono:'IBM Plex Mono', 'SFMono-Regular', monospace;
}

@media (prefers-reduced-motion: reduce){
    *{ transition:none !important; animation:none !important; }
}

#MainMenu{visibility:hidden;}
footer{visibility:hidden;}
header[data-testid="stHeader"]{background:transparent;}

.stApp{
    background:var(--bg);
    font-family:var(--font-sans);
}

html,body,h1,h2,h3,h4,h5,h6,p,label,span,li{
    color:var(--text-primary);
}

.block-container{
    padding-top:1.25rem;
    padding-left:3rem;
    padding-right:3rem;
    padding-bottom:3rem;
}

/* ---------- CLASSIFICATION BANNER ---------- */

.classification-banner{
    display:flex;
    justify-content:space-between;
    align-items:center;
    flex-wrap:wrap;
    gap:6px;
    border-top:1px solid var(--gold);
    border-bottom:1px solid var(--border);
    background:linear-gradient(90deg, rgba(201,162,39,0.10), rgba(201,162,39,0.02));
    padding:8px 14px;
    margin-bottom:28px;
    font-family:var(--font-mono);
    font-size:11px;
    letter-spacing:0.14em;
    text-transform:uppercase;
    color:var(--gold);
}
.classification-banner .case-ref{
    color:var(--text-muted);
    letter-spacing:0.08em;
}

/* ---------- MASTHEAD ---------- */

.masthead{
    display:flex;
    align-items:center;
    gap:18px;
    margin-bottom:8px;
}
.masthead-emblem{
    width:54px; height:54px;
    border:1px solid var(--gold);
    border-radius:10px;
    background:var(--panel);
    display:flex; align-items:center; justify-content:center;
    font-size:24px;
    flex-shrink:0;
}
.masthead-title{
    font-family:var(--font-serif);
    font-weight:700;
    font-size:32px;
    letter-spacing:-0.01em;
    color:var(--text-primary);
    line-height:1.1;
}
.masthead-sub{
    font-family:var(--font-mono);
    font-size:12px;
    letter-spacing:0.06em;
    text-transform:uppercase;
    color:var(--text-secondary);
    margin-top:4px;
}
.masthead-rule{
    border:none;
    border-top:1px solid var(--border);
    margin:20px 0 28px 0;
}

/* ---------- SIDEBAR ---------- */

section[data-testid="stSidebar"]{
    background:var(--bg-elevated);
    border-right:1px solid var(--border);
}
section[data-testid="stSidebar"] .block-container{
    padding-top:1.5rem;
    padding-left:1.25rem;
    padding-right:1.25rem;
}

.sidebar-brand{
    display:flex;
    flex-direction:column;
    align-items:flex-start;
    gap:2px;
    padding-bottom:16px;
    margin-bottom:14px;
    border-bottom:1px solid var(--border);
}
.sidebar-brand .brand-mark{
    font-family:var(--font-serif);
    font-weight:700;
    font-size:19px;
    letter-spacing:0.02em;
    color:var(--text-primary);
}
.sidebar-brand .brand-tag{
    font-family:var(--font-mono);
    font-size:10px;
    letter-spacing:0.12em;
    text-transform:uppercase;
    color:var(--text-muted);
}

.section-label{
    font-family:var(--font-mono);
    font-size:11px;
    letter-spacing:0.12em;
    text-transform:uppercase;
    color:var(--text-muted);
    display:flex;
    align-items:center;
    gap:8px;
    margin:18px 0 10px 0;
}
.section-label::before{
    content:"";
    width:14px; height:2px;
    background:var(--gold);
    display:inline-block;
    flex-shrink:0;
}

/* Radio groups -> segmented list */
div[role="radiogroup"]{
    background:transparent;
    padding:0;
    display:flex;
    flex-direction:column;
    gap:6px;
}
div[role="radiogroup"] label{
    background:var(--panel);
    border:1px solid var(--border);
    border-radius:8px;
    padding:9px 12px;
    margin:0 !important;
}
div[role="radiogroup"] label:has(input:checked){
    background:var(--gold-soft);
    border-color:var(--gold);
}
div[data-baseweb="radio"] > div:first-child{
    border-color:var(--text-muted) !important;
}
div[data-baseweb="radio"] > div:first-child > div{
    background:var(--gold) !important;
}

/* Selectbox / Multiselect shell */
div[data-testid="stSelectbox"] > div > div,
div[data-testid="stMultiSelect"] > div > div{
    background:var(--panel) !important;
    border:1px solid var(--border) !important;
    border-radius:8px !important;
    color:var(--text-primary) !important;
}
div[data-baseweb="popover"] li{
    font-family:var(--font-sans);
}

/* Multiselect chips */
span[data-baseweb="tag"], div[data-baseweb="tag"]{
    background:var(--gold-soft) !important;
    border:1px solid var(--gold) !important;
    border-radius:6px !important;
}
span[data-baseweb="tag"] span, div[data-baseweb="tag"] span{
    color:var(--gold) !important;
    font-family:var(--font-mono) !important;
    font-size:11px !important;
    letter-spacing:0.03em;
}
span[data-baseweb="tag"] svg, div[data-baseweb="tag"] svg{
    fill:var(--gold) !important;
}

/* Text input / text area */
.stTextInput input,
.stTextArea textarea{
    background:var(--panel) !important;
    color:var(--text-primary) !important;
    border:1px solid var(--border) !important;
    border-radius:8px !important;
    font-family:var(--font-sans) !important;
}
.stTextArea textarea{ min-height:260px !important; }
.stTextInput input:focus,
.stTextArea textarea:focus{
    border-color:var(--gold) !important;
    box-shadow:0 0 0 1px var(--gold) !important;
}

/* Buttons */
.stButton button,
.stDownloadButton button{
    background:var(--gold) !important;
    color:#191207 !important;
    border:none !important;
    border-radius:8px !important;
    font-weight:600 !important;
    font-family:var(--font-sans) !important;
    letter-spacing:0.01em;
}
.stButton button:hover,
.stDownloadButton button:hover{
    background:#B79322 !important;
    color:#191207 !important;
}
.stButton button:focus-visible,
.stDownloadButton button:focus-visible,
a:focus-visible,
input:focus-visible{
    outline:2px solid var(--teal) !important;
    outline-offset:2px;
}

/* File uploader */
[data-testid="stFileUploader"]{
    background:var(--panel) !important;
    border:1.5px dashed var(--border) !important;
    border-radius:12px;
    padding:18px;
}
[data-testid="stFileUploader"] *{
    color:var(--text-primary) !important;
}
[data-testid="stFileUploader"] section{
    background:transparent !important;
}

/* Expanders */
details{
    background:var(--panel) !important;
    border:1px solid var(--border) !important;
    border-radius:10px !important;
    margin-bottom:12px;
}
details summary{
    color:var(--text-primary) !important;
    font-family:var(--font-mono) !important;
    font-size:13px !important;
    letter-spacing:0.04em;
}

/* Progress bar */
[data-testid="stProgressBar"]{
    background-color:var(--panel-alt) !important;
    border-radius:8px;
}
[data-testid="stProgressBar"] > div{
    background-color:var(--gold) !important;
    border-radius:8px;
}

/* Alerts */
[data-testid="stAlert"]{
    border-radius:8px;
    font-family:var(--font-sans);
}

/* Bordered containers */
[data-testid="stVerticalBlockBorderWrapper"]{
    border-radius:12px !important;
    border:1px solid var(--border) !important;
    background:var(--panel);
}

/* Exhibit / tag internals */
.exhibit-stripe{
    height:3px;
    border-radius:3px;
    background:var(--gold);
    margin:-1px -1px 14px -1px;
}
.exhibit-header{
    display:flex;
    align-items:baseline;
    flex-wrap:wrap;
    gap:12px;
    margin-bottom:10px;
}
.exhibit-badge{
    font-family:var(--font-mono);
    font-size:11px;
    letter-spacing:0.08em;
    border:1px solid var(--gold);
    color:var(--gold);
    border-radius:4px;
    padding:2px 8px;
    white-space:nowrap;
}
.exhibit-time{
    font-family:var(--font-mono);
    font-size:11px;
    color:var(--text-muted);
    margin-left:auto;
    white-space:nowrap;
}
.exhibit-stamp{
    display:inline-block;
    font-family:var(--font-mono);
    font-size:10px;
    letter-spacing:0.1em;
    text-transform:uppercase;
    color:var(--teal);
    border:1px dashed var(--teal);
    border-radius:4px;
    padding:2px 8px;
    transform:rotate(-1.5deg);
    margin-top:10px;
}

.tag-pill{
    display:inline-flex;
    align-items:center;
    gap:6px;
    font-family:var(--font-mono);
    font-size:11px;
    font-weight:600;
    letter-spacing:0.07em;
    text-transform:uppercase;
    border-radius:999px;
    padding:4px 12px;
    margin-bottom:10px;
}
.tag-section{ margin-bottom:6px; }
.tag-divider{
    border:none;
    border-top:1px dashed var(--border-soft);
    margin:16px 0;
}
.record-desc{
    font-family:var(--font-sans);
    font-size:12.5px;
    color:var(--text-secondary);
    line-height:1.5;
    margin:2px 0 0 0;
}
.sidebar-tag-list{
    display:flex;
    flex-direction:column;
    gap:6px;
    margin-top:10px;
}
.stMarkdown p{ line-height:1.65; }

</style>
""", unsafe_allow_html=True)