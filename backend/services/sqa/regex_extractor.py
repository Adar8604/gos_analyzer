import re

import re

PAN_REGEX = r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"

AADHAAR_REGEX = r"\b\d{4}\s?\d{4}\s?\d{4}\b"

ACCOUNT_REGEX = (
    r"(?i)(?:current|saving|current account|savings account|account|a/c)"
    r"(?:\s*no\.?|\s*number)?[:\s]*([0-9]{8,18})"
)

CUSTOMER_ID_REGEX = (
    r"(?i)(?:customer\s*id|cust\s*id|cif)\s*[:\-]?\s*[A-Za-z0-9]+"
)

BRANCH_REGEX = (
    r"(?i)(?:opened at|branch|reporting branch)\s+([A-Za-z0-9 .,&()-]+)"
)

DATE_REGEX = (
    r"\b(?:\d{1,2}[./-]\d{1,2}[./-]\d{2,4}"
    r"|\d{4}[./-]\d{1,2}[./-]\d{1,2})\b"
)

AMOUNT_REGEX = (
    r"(?i)(?:₹|rs\.?|inr)?\s*\d[\d,]*(?:\.\d+)?\s*(?:lakhs?|crores?)?"
)

SOURCE_REGEX = (
    r"(?i)(source\s+of\s+funds|major\s+credits?|credit\s+of|from)"
)

DESTINATION_REGEX = (
    r"(?i)(destination\s+of\s+funds|major\s+debits?|debit\s+of|to)"
)

MODE_REGEX = (
    r"(?i)\b(IMPS|RTGS|NEFT|UPI|CHEQUE|DD|WIRE|TRANSFER|EFT|CASH)\b"
)

NAME_REGEX = (
    r"(?i)(?:in the name of|customer name|entity name|name of)\s+([A-Za-z0-9 ./&()-]+)"
)

def extract_fields(text):

    source_present = bool(re.search(SOURCE_REGEX, text))
    destination_present = bool(re.search(DESTINATION_REGEX, text))
    mode_present = bool(re.search(MODE_REGEX, text))

    return {

        "Customer identity (name or entity name)":
            bool(re.search(NAME_REGEX, text)),

        "Customer identifier (Customer ID or equivalent)":
            bool(re.search(CUSTOMER_ID_REGEX, text)),

        "Account number":
            bool(re.search(ACCOUNT_REGEX, text)),

        "Bank or reporting branch":
            bool(re.search(BRANCH_REGEX, text)),

        "Customer identification (PAN, Aadhaar, Passport, or equivalent)":
            bool(
                re.search(PAN_REGEX, text)
                or re.search(AADHAAR_REGEX, text)
            ),

        "Transaction date or reporting period":
            len(re.findall(DATE_REGEX, text)) > 0,

        "Transaction amount or turnover":
            len(re.findall(AMOUNT_REGEX, text)) > 0,

        "Sufficient transaction details (source, destination, or transaction mode)":
            source_present or destination_present or mode_present,
    }