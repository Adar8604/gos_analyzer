import sys
import csv
import tempfile
from datetime import datetime
from pathlib import Path
from style import apply_custom_css

import pandas as pd
import streamlit as st

from utils import markdown_to_text

from ui_helpers import (
    ANALYSIS_META,
    ANALYSIS_KEYS,
    COLUMN_MAP,
    tag_pill_html,
    container_header,
    build_tagged_text,
    copy_button,
    timestamp,
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


def gos_analyzer_page(input_mode, combo_key, selected_keys, extra_params_for):
    if input_mode == "Text Input":
        st.markdown("<div class='section-label'>Ground of Suspicion (GOS)</div>", unsafe_allow_html=True)
        gos_text = st.text_area("Ground of Suspicion", placeholder="Paste or enter the ground of suspicion narrative here.", label_visibility="collapsed")
        run_clicked = st.button("Run Analysis", use_container_width=False)

        if run_clicked and not selected_keys:
            st.warning("Select at least one analysis type in the sidebar before running.")
        elif run_clicked and selected_keys:
            st.session_state.exhibit_counter += 1
            exhibit_no = st.session_state.exhibit_counter
            run_time = timestamp()
            per_type = {}

            with st.container(border=True):
                container_header("EXHIBIT", f"{exhibit_no:03d}", run_time)
                for i, key in enumerate(selected_keys):
                    st.markdown(f"<div class='tag-section'>{tag_pill_html(key)}</div>", unsafe_allow_html=True)
                    placeholder = st.empty()
                    full_response = ""

                    for chunk in analyze_gos(gos_text, key, extra_params_for(key)):
                        full_response += chunk
                        placeholder.markdown(full_response, unsafe_allow_html=True)

                    formatted = markdown_to_text(full_response)
                    per_type[key] = {"markdown": full_response, "formatted": formatted}

                    if i < len(selected_keys) - 1:
                        st.markdown("<hr class='tag-divider'/>", unsafe_allow_html=True)

                st.markdown("<div class='exhibit-stamp'>✓ All selected analyses processed</div>", unsafe_allow_html=True)
                st.session_state.text_results[combo_key] = {"per_type": per_type, "exhibit_no": exhibit_no, "timestamp": run_time}

                export_keys = [k for k in selected_keys if k != "keyword_search"]
                if export_keys:
                    combined_formatted = build_tagged_text(export_keys, {k: v["formatted"] for k, v in per_type.items() if k in export_keys})
                    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
                    action_col1, action_col2 = st.columns([1, 1])
                    with action_col1:
                        st.download_button("Download All", data=combined_formatted, file_name="analysis.txt", mime="text/plain", use_container_width=True)
                    with action_col2:
                        copy_button(combined_formatted)

        elif combo_key in st.session_state.text_results and selected_keys:
            saved_data = st.session_state.text_results[combo_key]
            per_type = saved_data["per_type"]

            with st.container(border=True):
                container_header("EXHIBIT", f"{saved_data['exhibit_no']:03d}", saved_data["timestamp"])
                for i, key in enumerate(selected_keys):
                    st.markdown(f"<div class='tag-section'>{tag_pill_html(key)}</div>", unsafe_allow_html=True)
                    st.markdown(per_type.get(key, {}).get("markdown", "_No cached result for this tag — run analysis again._"))
                    if i < len(selected_keys) - 1:
                        st.markdown("<hr class='tag-divider'/>", unsafe_allow_html=True)

                export_keys = [k for k in selected_keys if k != "keyword_search"]
                if export_keys:
                    combined_formatted = build_tagged_text(export_keys, {k: v["formatted"] for k, v in per_type.items() if k in export_keys})
                    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
                    action_col1, action_col2 = st.columns([1, 1])
                    with action_col1:
                        st.download_button("Download All", data=combined_formatted, file_name="analysis.txt", mime="text/plain", use_container_width=True)
                    with action_col2:
                        copy_button(combined_formatted)

    else:
        # ====================================================================
        # EXCEL / CSV BATCH MODE
        # ====================================================================
        st.markdown("<div class='section-label'>Batch Upload</div>", unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            "Upload GOS File",
            type=["xlsx", "xls", "csv"],
            help="Supported formats: Excel (.xlsx, .xls) and CSV (.csv).",
            label_visibility="collapsed",
        )

        if uploaded_file is not None:
            file_name = uploaded_file.name.lower()
            is_csv = file_name.endswith(".csv")

            # 1. MEMORY-SAFE PREVIEW (Read only 5 rows & identify columns)
           
            try:
                if is_csv:
                    preview_df = pd.read_csv(uploaded_file, nrows=5)
                else:
                    preview_df = pd.read_excel(uploaded_file, nrows=5, engine="calamine")
                
                uploaded_file.seek(0) # Reset file pointer

                columns = preview_df.columns.tolist()
                if not columns:
                    st.error("The uploaded file appears to be empty.")
                    st.stop()

                # Determine dynamic column default index
                default_idx = columns.index("GOS") if "GOS" in columns else 0

                st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)
                
                # Dropdown for column selection
                col_sel, _ = st.columns([1, 1])
                with col_sel:
                    gos_col = st.selectbox(
                        "Select the column containing Ground of Suspicion:", 
                        options=columns,
                        index=default_idx,
                        help="Choose the specific column that houses the GOS narrative you want to analyze."
                    )

                with st.container(border=True):
                    st.markdown("<div class='exhibit-badge' style='border-color:var(--text-muted); color:var(--text-secondary); margin-bottom: 12px;'>PREVIEW (FIRST 5 ROWS)</div>", unsafe_allow_html=True)
                    st.dataframe(
                        preview_df, 
                        use_container_width=True,
                        column_config={
                            gos_col: st.column_config.TextColumn(gos_col, width="large")
                        }
                    )

            except Exception as e:
                st.error(f"Error reading file preview: {str(e)}")
                st.stop()

            # 2. CHUNKED PROCESSING & STREAMING TO DISK (WITH ERROR RESILIENCY)
            
            run_clicked = st.button("Run Analysis", use_container_width=False)

            if run_clicked and not selected_keys:
                st.warning("Select at least one analysis type in the sidebar before running.")
            elif run_clicked and selected_keys:
                export_keys = [k for k in selected_keys if k != "keyword_search"]
                tags_label = " · ".join(ANALYSIS_META[k]["label"] for k in selected_keys)

                st.markdown(f"<div class='section-label'>Batch Results — {tags_label}</div>", unsafe_allow_html=True)
                
                status = st.empty()
                results_container = st.container()

                temp_output = tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="w", encoding="utf-8-sig", newline="")
                output_filepath = temp_output.name
                
                processed_count = 0
                record_idx = 0

                try:
                    if is_csv:
                        chunks = pd.read_csv(uploaded_file, chunksize=100)
                    else:
                        full_excel = pd.read_excel(uploaded_file, engine="calamine")
                        chunks = [full_excel[i:i+100] for i in range(0, len(full_excel), 100)]
                        
                    writer = None

                    try:
                        for chunk in chunks:
                            for _, row in chunk.iterrows():
                                record_idx += 1
                                gos_val = str(row[gos_col]) if pd.notna(row[gos_col]) else ""
                                status.info(f"Processing record #{record_idx}...")

                                row_dict = row.to_dict()
                                
                                with results_container:
                                    with st.expander(f"RECORD {record_idx:03d}", expanded=False):
                                        for i, key in enumerate(selected_keys):
                                            st.markdown(f"<div class='tag-section'>{tag_pill_html(key)}</div>", unsafe_allow_html=True)
                                            placeholder = st.empty()
                                            full_response = ""

                                            # Inner try/except handles individual LLM errors without breaking the loop
                                            try:
                                                for chunk_text in analyze_gos(gos_val, key, extra_params_for(key)):
                                                    full_response += chunk_text
                                                    placeholder.markdown(full_response, unsafe_allow_html=True)
                                            except Exception as e:
                                                full_response = f"Error: {str(e)}"
                                                st.error(full_response)

                                            if key in export_keys:
                                                row_dict[COLUMN_MAP[key]] = full_response

                                            if i < len(selected_keys) - 1:
                                                st.markdown("<hr class='tag-divider'/>", unsafe_allow_html=True)

                                        st.markdown("<div class='exhibit-stamp'>✓ Processed</div>", unsafe_allow_html=True)

                                # Stream output row immediately to disk
                                if writer is None:
                                    fieldnames = list(row_dict.keys())
                                    writer = csv.DictWriter(temp_output, fieldnames=fieldnames)
                                    writer.writeheader()

                                writer.writerow(row_dict)
                                temp_output.flush()
                                processed_count += 1
                                
                    except Exception as loop_error:
                        # Catch catastrophic loop errors (e.g. fatal disconnects) but preserve the progress made
                        st.error(f"Processing interrupted at record #{record_idx} due to an error: {str(loop_error)}")
                        st.warning("Partial results have been saved. You can download the records processed so far.")
                        
                except Exception as file_error:
                    # Catch file reading errors
                    st.error(f"Error loading file for batch processing: {str(file_error)}")
                finally:
                    temp_output.close()
                
                # Only offer the download if at least one record was processed successfully
                if processed_count > 0:
                    status.success(f"Successfully processed {processed_count} records!")
                    out_name = f"{Path(uploaded_file.name).stem}_analyzed.csv"
                    
                    with st.container(border=True):
                        col1, col2 = st.columns([7.6, 2.4])
                        with col1:
                            st.success(f"Ready to export {processed_count} records.")
                        with col2:
                            with open(output_filepath, "rb") as f:
                                st.download_button(
                                    label="Download Results (CSV)",
                                    data=f, 
                                    file_name=out_name,
                                    mime="text/csv",
                                    use_container_width=True,
                                )