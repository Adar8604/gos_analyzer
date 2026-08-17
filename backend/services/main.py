from services.ollama_service import OllamaClient
import json
import re

from services.prompts.summary import SUMMARY_PROMPT
from services.prompts.offence import OFFENCE_PROMPT
from services.prompts.transaction import TRANSACTION_PROMPT
from services.prompts.bank_details import BANK_DETAILS

from services.financial.amount_extractor import AmountExtractor
from services.ner.regex_extractor import RegexExtractor

from services.ner.gliner_service import ner_service
from services.ner.formatter import format_entities
from services.ner.formatter import filter_relations
from services.ner.formatter import filter_pan_relations
from services.ner.formatter import mask_bank_entities
from services.ner.ifsc_mapper import get_bank_name



# Lazy Load Ollama Client


_llm = None


def get_llm():

    global _llm

    if _llm is None:
        _llm = OllamaClient()

    return _llm



# Prompt Registry


PROMPTS = {
    "summary": SUMMARY_PROMPT,
    "offence": OFFENCE_PROMPT,
}



# Main Router


def bank_details_table(relations):

    lines = [
        "## 🏦 Bank Details",
        "",
        "| Account Number | IFSC Code | Bank Name |",
        "|---|---|---|"
    ]

    # If there is no data, add an empty row to force tabular rendering
    if not relations:
        lines.append("| - | - | - |")
    else:
        for row in relations:
            account = row.get("account_number", "-")
            ifsc = row.get("ifsc_code")

            if ifsc is None:
                ifsc_display = "-"
                bank = "-"
            else:
                ifsc_display = ifsc
                bank = get_bank_name(ifsc)

            lines.append(
                f"| {account} | {ifsc_display} | {bank} |"
            )

    return "\n".join(lines)


def pan_details_table(relations):

    lines = [
        "## 🪪 PAN Details",
        "",
        "| PAN Number | Person Name |",
        "|---|---|"
    ]

    # If there is no data, add an empty row to force tabular rendering
    if not relations:
        lines.append("| - | - |")
    else:
        for row in relations:
            pan = row.get("pan_number", "-")
            person = row.get("person_name")

            if person is None:
                person = "-"

            lines.append(
                f"| {pan} | {person} |"
            )

    return "\n".join(lines)

# Transaction Tab Components Formatter

def transaction_metrics_table(metrics):
    lines = [
        "| Metric Indicator | Amount |",
        "|---|---|"
    ]
    
    # If metrics dict is empty or None, render an empty row
    if not metrics:
        lines.append("| - | - |")
    else:
        lines.append(f"| **Total Credit Summation** | ₹ {metrics.get('total_credit_summation', 0.0):,.2f} |")
        lines.append(f"| **Total Debit Summation** | ₹ {metrics.get('total_debit_summation', 0.0):,.2f} |")
        lines.append(f"| **Current Account Balance** | ₹ {metrics.get('current_balance', 0.0):,.2f} |")
        
    return "\n".join(lines)


def transaction_ledger_table(ledger):
    lines = [
        "## 💸 Transaction Flow Ledger",
        "",
        "| Date | Flow Direction | Mode | Counterparty Entity | Acc / Card No. | IFSC Code | UPI ID | Location | Amount |",
        "|---|---|---|---|---|---|---|---|---|"
    ]
    
    # If there is no data, add an empty row (9 columns) to force tabular rendering
    if not ledger:
        lines.append("| - | - | - | - | - | - | - | - | - |")
    else:
        for row in ledger:
            direction = row.get("direction", "INFLOW")
            # Visual cues for flows
            flow_tag = "🟩 INFLOW (Credit)" if direction == "INFLOW" else "🟥 OUTFLOW (Debit)"
            
            date = row.get("date", "-")
            mode = row.get("mode", "-")
            counterparty = row.get("counterparty_name", "-")
            
            # Merge Account and Card numbers into one column to save space
            account = row.get("reference_account") or row.get("card_number") or "-"
            ifsc = row.get("ifsc_code", "-") or "-"
            loc = row.get("location", "-") or "-"
            amount = f"₹ {row.get('amount', 0.0):,.2f}"
            
            upi = row.get("upi_id", "-") or "-"
            
            lines.append(
                f"| {date} | {flow_tag} | {mode} | {counterparty} | {account} | {ifsc} | {upi} | {loc} | {amount} |"
            )
            
    return "\n".join(lines)

def extract_metrics_via_regex(text: str) -> dict:
    """Dynamically extracts summary metrics if the LLM crashes."""
    metrics = {
        "total_credit_summation": 0.0,
        "total_debit_summation": 0.0,
        "current_balance": 0.0
    }
    
    # Extract Credits (Updated to handle "total credit in the account was Rs.")
    cred_match = re.search(r"Total\s+Credit.*?Rs\.?\s*([\d\.]+)\s*(lacs?|lakhs?|crores?|cr)?", text, re.IGNORECASE)
    if cred_match:
        val = float(cred_match.group(1))
        mult = cred_match.group(2)
        if mult:
            if 'lac' in mult.lower() or 'lakh' in mult.lower(): val *= 100000
            elif 'cr' in mult.lower() or 'crore' in mult.lower(): val *= 10000000
        metrics["total_credit_summation"] = val
        
    # Extract Debits
    deb_match = re.search(r"Total\s+Debit.*?Rs\.?\s*([\d\.]+)\s*(lacs?|lakhs?|crores?|cr)?", text, re.IGNORECASE)
    if deb_match:
        val = float(deb_match.group(1))
        mult = deb_match.group(2)
        if mult:
            if 'lac' in mult.lower() or 'lakh' in mult.lower(): val *= 100000
            elif 'cr' in mult.lower() or 'crore' in mult.lower(): val *= 10000000
        metrics["total_debit_summation"] = val
        
    # Extract Balance
    bal_match = re.search(r"Balance.*?Rs\.?\s*([\d\.]+)", text, re.IGNORECASE)
    if bal_match:
        metrics["current_balance"] = float(bal_match.group(1))
        
    return metrics


def parse_ledger_via_regex_fallback(text: str) -> list:
    
    ledger = []
    
    # Updated to capture [a-zA-Z]+ to handle "Card" alongside UPI/IMPS
    pattern = r"(\d{8})\s+Rs\.?\s*([\d\.]+)\s+(Credit|Debit)\s+through\s+([a-zA-Z]+)\s*(.*?)(?=(?:\d{8}\s+Rs)|$)"
    
    matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
    
    for match in matches:
        date_raw = match.group(1)
        amt = float(match.group(2))
        direction = "INFLOW" if "cred" in match.group(3).lower() else "OUTFLOW"
        mode = match.group(4).upper()
        
        rest_of_string = match.group(5).strip()
        
        # Extract all potential identifiers
        acct_match = re.search(r"(?:ac|Ac)\.?\s*No\.?\s*(\d+)", rest_of_string)
        ifsc_match = re.search(r"IFSC\s+No\.?\s*([A-Z0-9]{11})", rest_of_string, re.IGNORECASE)
        upi_match = re.search(r"(?:UPI\s+ID\s+)?([a-zA-Z0-9._-]+@[a-zA-Z0-9]+)", rest_of_string, re.IGNORECASE)
        card_match = re.search(r"Card\s+(?:No\.?\s*)?(\d{13,19})", rest_of_string, re.IGNORECASE)
        
        acct = acct_match.group(1) if acct_match else None
        ifsc = ifsc_match.group(1).upper() if ifsc_match else None
        upi = upi_match.group(1).lower() if upi_match else None
        card = card_match.group(1) if card_match else None
        
        # Strip out the identifiers to isolate the Name and Location
        clean_str = rest_of_string
        if acct_match: clean_str = clean_str.replace(acct_match.group(0), "")
        if ifsc_match: clean_str = clean_str.replace(ifsc_match.group(0), "")
        if upi_match: clean_str = clean_str.replace(upi_match.group(0), "")
        if card_match: clean_str = clean_str.replace(card_match.group(0), "")
        
        # Clean up leftover stray words like "ID" or "No"
        clean_str = re.sub(r"(?i)\b(UPI ID|Card No\.?|Ac No\.?|IFSC)\b", "", clean_str)
        
        words = [w.strip() for w in clean_str.split() if w.strip() and w.strip().lower() != "no"]
        
        name = "-"
        loc = "-"
        if words:
            # Expanded known locations list based on the new GoS
            known_locations = ["bihar", "n.delhi", "delhi", "karnataka", "h.p", "maharashtra", "w.bengal", "mumbai"]
            if len(words) > 1 and words[-1].lower() in known_locations:
                loc = words[-1]
                name = " ".join(words[:-1])
            else:
                name = " ".join(words)
        
        formatted_date = f"{date_raw[:2]}-{date_raw[2:4]}-{date_raw[4:]}"
        
        ledger.append({
            "date": formatted_date,
            "amount": amt,
            "mode": mode,
            "counterparty_name": name,
            "reference_account": acct,
            "ifsc_code": ifsc,
            "upi_id": upi,
            "card_number": card,
            "location": loc,
            "direction": direction
        })
        
    return ledger


def chunk_transaction_text(text: str, max_chars: int = 2500) -> list:
    """
    Splits massive text blobs into safe LLM-sized bites.
    Handles both line-by-line ledgers and giant unformatted paragraphs.
    """
    chunks = []
    
    # 1. Force line breaks after periods to break up giant paragraphs
    text_with_breaks = text.replace('. ', '.\n')
    sentences = [s.strip() for s in text_with_breaks.split('\n') if s.strip()]
    
    current_chunk = ""
    
    # 2. Group sentences into chunks of max 2500 characters
    for sentence in sentences:
        # If a single sentence/line is absurdly long, force split it
        if len(sentence) > max_chars:
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = ""
            # Split the giant sentence by brute force
            for i in range(0, len(sentence), max_chars):
                chunks.append(sentence[i:i+max_chars])
            continue
            
        if len(current_chunk) + len(sentence) > max_chars:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + " "
        else:
            current_chunk += sentence + " "
            
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
        
    return chunks

def analyze_gos(gos, analysis_type, labels=None):

    # Summary / Offence

    if analysis_type in PROMPTS:

        prompt = PROMPTS[analysis_type].format(
            gos=gos
        )

        yield from get_llm().generate(prompt)
        return

    # Transaction Analysis

    if analysis_type == "transaction":
            
            # 1. Split text into safe chunks to avoid LLM token overflow
            text_chunks = chunk_transaction_text(gos, max_chars=2500)
            
            llm_extracted_metrics = {} # Stores the LLM's attempt as a backup
            master_ledger = []
            
            # 2. Iterate and process each chunk independently
            for chunk in text_chunks:
                
                # Pre-calculate Math for THIS specific chunk
                raw_amounts = AmountExtractor.extract(chunk)
                amount_cheat_sheet = []
                for raw in raw_amounts:
                    normalized = AmountExtractor.normalize_to_float(raw)
                    amount_cheat_sheet.append(f"- '{raw}' use exactly: {normalized}")
                
                amount_text = "\n".join(amount_cheat_sheet) if amount_cheat_sheet else "None Detected"

                # Whitelist Entities for THIS specific chunk via RegexExtractor
                regex_entities = RegexExtractor.extract(chunk)
                
                ifsc_codes = {e["Entity"] for e in regex_entities if e["Tag"] == "IFSC Code"}
                account_nos = {e["Entity"] for e in regex_entities if e["Tag"] == "Account Number"}
                upi_ids = {e["Entity"] for e in regex_entities if e["Tag"] == "UPI ID"}
                card_nos = {e["Entity"] for e in regex_entities if e["Tag"] == "Card Number"}
                
                ifsc_text = ", ".join(ifsc_codes) if ifsc_codes else "None Detected"
                account_text = ", ".join(account_nos) if account_nos else "None Detected"
                upi_text = ", ".join(upi_ids) if upi_ids else "None Detected"
                card_text = ", ".join(card_nos) if card_nos else "None Detected"

                # Format Prompt tailored just for this chunk
                prompt = TRANSACTION_PROMPT.format(
                    gos=chunk,
                    amounts=amount_text,
                    ifsc_whitelist=ifsc_text,
                    account_whitelist=account_text,
                    upi_whitelist=upi_text,
                    card_whitelist=card_text
                )

                # Generate & Parse
                response = "".join(get_llm().generate(prompt)).strip()

                # Sanitize common markdown wrapper string leaks
                if response.startswith("```json"):
                    response = response[7:]
                if response.startswith("```"):
                    response = response[3:]
                if response.endswith("```"):
                    response = response[:-3]
                response = response.strip()

                try:
                    data = json.loads(response)
                    
                    # Save the LLM's metric attempt (just in case)
                    if data.get("metrics") and data["metrics"].get("total_credit_summation", 0) > 0:
                        llm_extracted_metrics = data["metrics"]
                        
                    # Append the ledger items from this chunk to the master list
                    if data.get("ledger"):
                        master_ledger.extend(data["ledger"])
                        
                except Exception:
                    print("[Warning] LLM failed on a chunk. Using regex fallback for this chunk.")
                    master_ledger.extend(parse_ledger_via_regex_fallback(chunk))

            # Run the flawless regex on the entire GoS text to get the real totals
            master_metrics = extract_metrics_via_regex(gos)
            
            # If the regex completely failed to find the summary (returns 0.0), 
            # only then do we fall back to what the LLM found.
            if master_metrics.get("total_credit_summation", 0) == 0.0:
                master_metrics = llm_extracted_metrics

            # 4. Yield the final aggregated tables to the frontend
            yield transaction_metrics_table(master_metrics)
            yield "\n\n"
            yield transaction_ledger_table(master_ledger)

            return

    # Named Entity Recognition

    if analysis_type == "ner":

        if labels is None:

            labels = [
                "Person",
                "Organization",
                "Location"
            ]

        entities = ner_service.extract_entities(
            gos,
            labels
        )

        yield format_entities(entities)

        bank_details = RegexExtractor.extract(gos)

        account_numbers = [
            x["Entity"]
            for x in bank_details
            if x["Tag"] == "Account Number"
        ]

        ifsc_codes = [
            x["Entity"]
            for x in bank_details
            if x["Tag"] == "IFSC Code"
        ]

        pan_numbers = [
            x["Entity"]
            for x in bank_details
            if x["Tag"] == "PAN Number"
        ]

        person_names = [
            x["Entity"]
            for x in entities
            if x["Tag"] == "Person"
        ]

        account_numbers_text = (
            "\n".join(f"- {x}" for x in account_numbers)
            if account_numbers
            else "None"
        )

        ifsc_codes_text = (
            "\n".join(f"- {x}" for x in ifsc_codes)
            if ifsc_codes
            else "None"
        )

        pan_numbers_text = (
            "\n".join(f"- {x}" for x in pan_numbers)
            if pan_numbers
            else "None"
        )

        person_names_text = (
            "\n".join(f"- {x}" for x in person_names)
            if person_names
            else "None"
        )

        card_numbers = [
            x["Entity"]
            for x in bank_details
            if x["Tag"] == "Card Number"
        ]

        card_set = {
            re.sub(r"\D", "", card)
            for card in card_numbers
        }

        account_numbers = [
            acc
            for acc in account_numbers
            if re.sub(r"\D", "", acc) not in card_set
        ]

        masked_gos = mask_bank_entities(
            gos,
            account_numbers,
            ifsc_codes
        )

        prompt = BANK_DETAILS.format(
            gos=masked_gos,
            account_numbers=account_numbers_text,
            ifsc_codes=ifsc_codes_text,
            pan_numbers=pan_numbers_text,
            person_names=person_names_text
        )

        response = "".join(get_llm().generate(prompt)).strip()

        # Remove markdown code fences if present
        if response.startswith("```json"):
            response = response[7:]

        if response.startswith("```"):
            response = response[3:]

        if response.endswith("```"):
            response = response[:-3]

        response = response.strip()

        try:
            data = json.loads(response)

            bank_relations = data["bank_relations"]
            pan_relations = data["pan_relations"]

            bank_relations = filter_relations(
                bank_relations,
                account_numbers,
                ifsc_codes,
                card_numbers
            )

            filter_pan_relations(
                pan_relations,
                pan_numbers,
                person_names
            )

            yield bank_details_table(bank_relations)

            yield pan_details_table(pan_relations)

        except Exception:
            # If parsing fails, show raw output for debugging
            yield "## 🏦 Bank Details\n\n" + response

        return

    # Keyword Search

    if analysis_type == "keyword_search":
        if not labels:
            yield "_No search keywords provided._"
            return
            
        highlighted_text = gos
        
        for keyword in labels:
            # Escape keyword to prevent regex crashes on special characters
            escaped_kw = re.escape(keyword.strip())
            if not escaped_kw:
                continue
                
            # \b ensures exact word boundaries (no partial matches)
            pattern = rf"\b({escaped_kw})\b"
            
            # Replace with HTML <mark> styled to match your custom theme
            replacement = r'<mark style="background-color: #C9A227; color: #191207; font-weight: 600; padding: 2px 4px; border-radius: 4px;">\1</mark>'
            
            highlighted_text = re.sub(pattern, replacement, highlighted_text, flags=re.IGNORECASE)
            
        # Ensure paragraphs are preserved in Markdown format
        highlighted_text = highlighted_text.replace("\n", "\n\n")
        
        yield highlighted_text
        return


    # Unknown Module

    raise ValueError(
        f"Unknown analysis type: {analysis_type}"
    )