import pandas as pd
from neo4j import GraphDatabase
from pyvis.network import Network
import os
from pathlib import Path
from services.ner.regex_extractor import RegexExtractor 

FIU_LINKABLE_ENTITIES = {
    "PAN Number", "Account Number", "Mobile Number", 
    "Email", "UPI ID", "Card Number", "UTR Number"
}

def process_and_visualize(file_paths, driver, session_id, id_col="reportId", gos_col="GOS"):
    """
        Process GOS reports and generate an interactive entity-linkage graph.

        Reads GOS reports from CSV or Excel files, extracts linkable entities
        using the regex-based NER extractor, stores report-entity relationships
        in Neo4j, and generates a session-specific PyVis visualization.

        Parameters
        ----------
        file_paths : iterable of pathlib.Path
            Paths to the input CSV or Excel files containing GOS reports.
        driver : neo4j.Driver
            Active Neo4j driver used for storing and querying graph data.
        session_id : str
            Unique identifier used to isolate graph data for the current
            processing session.
        id_col : str, optional
            Name of the column containing the GOS report identifier.
            Defaults to ``"reportId"``.
        gos_col : str, optional
            Name of the column containing the GOS report text.
            Defaults to ``"GOS"``.

        Returns
        -------
        str
            Path to the generated interactive PyVis HTML graph.

        Raises
        ------
        ValueError
            If an input file has an unsupported file format.
    """

    # 1. Clear ONLY the previous graph data for THIS specific session
    with driver.session() as session:
        session.run("MATCH (n {session_id: $session_id}) DETACH DELETE n", session_id=session_id)

    # 2. Process Files in Batches
    for file_path in file_paths:
        print(f"Processing {file_path.name}...")
        ext = file_path.suffix.lower()
        
        if ext == '.csv':
            df = pd.read_csv(file_path, usecols=[id_col, gos_col])
        elif ext in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path, usecols=[id_col, gos_col])
        else:
            raise ValueError(f"Unsupported file format: {ext}")
            
        df = df.dropna(subset=[gos_col]) 
        
        batch_size = 500
        for start in range(0, len(df), batch_size):
            batch_df = df.iloc[start:start+batch_size]
            _ingest_batch_to_neo4j(batch_df, id_col, gos_col, driver, session_id)
            
    # 3. Generate Visualization
    html_output_path = f"gos_linkages_{session_id}.html" # Save uniquely per session
    _generate_filtered_graph(driver, html_output_path, session_id)
    
    return html_output_path

def _ingest_batch_to_neo4j(df, id_col, gos_col, driver, session_id):
    ingest_payloads = {tag.replace(" ", "_"): [] for tag in FIU_LINKABLE_ENTITIES}
    
    for _, row in df.iterrows():
        report_id = str(row[id_col])
        text = str(row[gos_col])
        
        extracted = RegexExtractor.extract(text)
        
        for item in extracted:
            tag = item["Tag"]
            if tag in FIU_LINKABLE_ENTITIES:
                safe_tag = tag.replace(" ", "_")
                ingest_payloads[safe_tag].append({
                    "report_id": report_id,
                    "value": item["Entity"]
                })
                
    with driver.session() as session:
        for safe_tag, records in ingest_payloads.items():
            if not records:
                continue
                
            # Cypher query now includes session_id in the MERGE statements
            query = f"""
            UNWIND $batch AS record
            MERGE (g:GOS_Document {{id: record.report_id, session_id: $session_id}})
            MERGE (e:Entity:{safe_tag} {{id: record.value, session_id: $session_id}})
            MERGE (g)-[:SHARES_{safe_tag.upper()}]->(e)
            """
            session.run(query, batch=records, session_id=session_id)

def _generate_filtered_graph(driver, output_path, session_id):
    """
        Generate an interactive graph of shared entities across GOS reports.

        Queries Neo4j for entities that are linked to multiple GOS reports
        within the specified session and renders the resulting relationships
        as an interactive PyVis network.

        Parameters
        ----------
        driver : neo4j.Driver
            Active Neo4j driver used to query graph data.
        output_path : str
            Destination path for the generated PyVis HTML file.
        session_id : str
            Session identifier used to restrict the graph to the current
            processing session.
    """

    query = """
    MATCH (e:Entity {session_id: $session_id})
    WHERE COUNT { (e)<--() } > 1
    MATCH (g:GOS_Document {session_id: $session_id})-[r]->(e)
    RETURN g, r, e
    """
    
    net = Network(
        height="800px",
        width="100%",
        bgcolor="#111111",
        font_color="white",
        notebook=False,
        directed=True
    )
    
    colors = {
        "GOS_Document": "#EE79A4",
        "PAN_Number": "#EE79A4",     
        "Account_Number": "#E5A8D9", 
        "Mobile_Number": "#BAA867",  
        "Email": "#A8E6F0",          
        "UPI_ID": "#AAF2C9",         
        "UTR_Number": "#FFC681",     
        "Card_Number": "#C7A2B0",    
    }
    
    with driver.session() as session:
        results = session.run(query, session_id=session_id)
        
        for record in results:
            gos_node = record["g"]
            entity_node = record["e"]
            relationship = record["r"]
            
            # 1. Add GOS Node
            gos_id = str(gos_node["id"])
            net.add_node(
                gos_id,
                label=gos_id,
                title=f"Report ID : {gos_id}<br>",
                color=colors.get("GOS_Document"),
                shape="dot",
                size=38, 
                group="GOS_Document"
            )
            
            # 2. Add Entity Node
            entity_labels = [lbl for lbl in entity_node.labels if lbl not in ('Entity', 'session_id')]
            entity_type = entity_labels[0] if entity_labels else "Unknown"
            entity_id = str(entity_node["id"])
            
            net.add_node(
                entity_id,
                label=entity_id,
                title=f"{entity_type.replace('_', ' ')} : {entity_id}<br>",
                color=colors.get(entity_type, "#AAAAAA"),
                shape="dot",
                size=18, 
                group=entity_type
            )
            
            # 3. Add Edge
            net.add_edge(
                gos_id,
                entity_id,
                label=relationship.type.replace("SHARES_", ""),
                color="#AAAAAA"
            )
            
    # Restored your exact JSON layout options
    net.set_options("""
    {
      "physics": {
        "enabled": true,
        "barnesHut": {
          "gravitationalConstant": -12000,
          "centralGravity": 0.05,
          "springLength": 250,
          "springConstant": 0.04,
          "damping": 0.4
        },
        "solver": "barnesHut"
      },
      "nodes": {
        "font": {
          "size": 18,
          "color": "white"
        },
        "borderWidth": 4,
        "shadow": {
          "enabled": true,
          "color": "rgba(0,0,0,0.5)",
          "size": 10,
          "x": 2,
          "y": 2
        }
      },
      "edges": {
        "color": "#AAAAAA",
        "smooth": {
          "enabled": true,
          "roundness": 0.2
        },
        "shadow": false,
        "arrows": {
          "to": {
            "enabled": true,
            "scaleFactor": 1
          }
        },
        "font": {
          "size": 14,
          "color": "#DDDDDD",
          "align": "middle",
          "strokeWidth": 0,
          "strokeColor": "rgba(0,0,0,0.5)"
        }
      },
      "interaction": {
        "hover": true,
        "navigationButtons": true,
        "keyboard": true
      }
    }
    """)
    
    net.save_graph(output_path)