import streamlit as st
import streamlit.components.v1 as components
import os
import tempfile
import uuid
from pathlib import Path
from neo4j import GraphDatabase

# Import backend processor
from services.linker.backend_processor import process_and_visualize

# Setup your DB Credentials
URI = "neo4j://127.0.0.1:7687"
AUTH = ("neo4j", "123456789")

def gos_linker_page():
    """
        Render the GOS Linker interface and generate an interactive linkage graph.

        Provides a Streamlit interface for uploading multiple GOS reports,
        specifying report and GOS-text column names, and generating a Neo4j-based
        entity relationship graph. Uploaded files are processed in an isolated
        session to prevent data from previous runs from being merged into the
        current graph.

        The generated PyVis visualization is embedded directly in the Streamlit
        application and the temporary HTML output is removed after rendering.
    """
    st.markdown("### Upload Files for Graph Linkage")
    
    # Optional inputs in case the column names change
    col1, col2 = st.columns(2)
    with col1:
        id_col = st.text_input("Report ID Column Name", value="reportId")
    with col2:
        gos_col = st.text_input("GOS Column Name", value="GOS")
        
    st.info("💡 Note: If you are uploading a new file, make sure to click the 'X' on the old file in the uploader below so it isn't processed again.")
    
    # Accept CSV and Excel files
    uploaded_files = st.file_uploader(
        "Upload GOS Files (Excel or CSV)", 
        type=["xlsx", "xls", "csv"], 
        accept_multiple_files=True
    )

    if uploaded_files:
        if st.button("Generate Linkage Graph", type="primary"):
            
            with st.spinner("Extracting entities and generating graph database. This may take a minute for large files..."):
                driver = GraphDatabase.driver(URI, auth=AUTH)
                
                # 1. Generate a fresh ID for this specific button click
                current_run_id = str(uuid.uuid4())
                
                # 2. Clean up the database from the LAST run (if it exists) to prevent merging graphs
                if 'last_run_id' in st.session_state:
                    with driver.session() as session:
                        session.run(
                            "MATCH (n {session_id: $session_id}) DETACH DELETE n", 
                            session_id=st.session_state.last_run_id
                        )
                
                # 3. Save the new ID to the session state for the next time you click
                st.session_state.last_run_id = current_run_id
                
                # Save uploaded files to a temporary directory so Pandas can read them
                temp_dir = tempfile.mkdtemp()
                temp_file_paths = []
                
                for uploaded_file in uploaded_files:
                    temp_path = os.path.join(temp_dir, uploaded_file.name)
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Convert to pathlib Path object for the backend processor
                    temp_file_paths.append(Path(temp_path))
                
                try:
                    # Execute the backend pipeline with the FRESH session ID
                    html_file_path = process_and_visualize(
                        file_paths=temp_file_paths, 
                        driver=driver, 
                        session_id=current_run_id, 
                        id_col=id_col, 
                        gos_col=gos_col
                    )
                    
                    st.success("Graph generated successfully! Isolated GOS reports have been filtered out.")
                    st.markdown("### FIU Network Map")
                    
                    # Read the Pyvis HTML directly inside the Streamlit app
                    with open(html_file_path, 'r', encoding='utf-8') as f:
                        source_code = f.read()
                        
                    components.html(source_code, height=850, scrolling=True)
                    
                    # Delete the HTML file from your local system after it's loaded
                    if os.path.exists(html_file_path):
                        os.remove(html_file_path)
                    
                except Exception as e:
                    st.error(f"An error occurred: {e}")
                finally:
                    driver.close()