from collections import defaultdict
import re


def clean_location(location):

    location = location.strip()

    # Remove trailing digits
    location = re.sub(r"\d+$", "", location)

    # Remove trailing punctuation
    location = re.sub(r"[-_/,:;]+$", "", location)

    location = location.strip()

    # Reject empty values
    if not location:
        return None

    # Reject pure numbers
    if location.isdigit():
        return None

    return location



def format_entities(entities):

    HIDDEN_TAGS = {
        "Account Number",
        "IFSC Code",
        "PAN Number"
    }

    PERSON_BLACKLIST = {
        "customer",
        "customers",
        "beneficiary",
        "beneficiaries",
        "account holder",
        "holder",
        "applicant",
        "complainant",
        "accused",
        "victim",
        "sender",
        "receiver",
        "remitter",
        "payee",
        "drawer",
        "issuer",
        "employee",
        "manager",
        "director",
        "officer"
    }

    grouped = defaultdict(list)
    seen = set()

    for entity in entities:

        tag = entity["Tag"]
        value = entity["Entity"]

        if entity["Tag"] == "Person":
            if entity["Entity"].strip().lower() in PERSON_BLACKLIST:
                continue

        if tag in HIDDEN_TAGS:
            continue

        # Clean Location entities
        if tag == "Location":
            value = clean_location(value)

            # Skip invalid locations
            if not value:
                continue

            # Skip purely numeric locations like 08559
            if value.isdigit():
                continue

        # Remove duplicates after cleaning
        key = (tag, value.lower())

        if key in seen:
            continue

        seen.add(key)

        grouped[tag].append({
            "Entity": value,
            "Score": entity["Score"]
        })

    output = ""

    for tag in grouped:

        output += f"## {tag}\n"

        for entity in grouped[tag]:

            output += (
                f"- **{entity['Entity']}**\n"
            )

        output += "\n"

    return output

def mask_bank_entities(text, account_numbers, ifsc_codes):
    """
    Masks every account number and IFSC except those supplied.

    Unknown account numbers -> <ACCOUNT_NUMBER>
    Unknown IFSC codes      -> <IFSC_CODE>
    """

    allowed_accounts = set(account_numbers)
    allowed_ifscs = {x.upper() for x in ifsc_codes}

    
    # Mask IFSC Codes
    
    def replace_ifsc(match):
        value = match.group().upper()

        if value in allowed_ifscs:
            return value

        return "<IFSC_CODE>"

    text = re.sub(
        r'(?<![A-Z0-9])[A-Z]{4}0[A-Z0-9]{6}(?![A-Z0-9])',
        replace_ifsc,
        text,
        flags=re.IGNORECASE
    )

    
    # Mask Account Numbers
    
    def replace_account(match):
        value = match.group()

        if value in allowed_accounts:
            return value

        return "<ACCOUNT_NUMBER>"

    text = re.sub(
        r'(?<!\d)\d{9,18}(?!\d)',
        replace_account,
        text
    )

    return text


def filter_relations(
    relations,
    account_numbers,
    ifsc_codes,
    card_numbers
):

    # Normalize account numbers
    valid_accounts = {
        re.sub(r"\D", "", acc)
        for acc in account_numbers
    }

    # Normalize card numbers
    valid_cards = {
        re.sub(r"\D", "", card)
        for card in card_numbers
    }

    valid_ifscs = set(ifsc_codes)

    filtered = []
    seen = set()

    for row in relations:

        account = row.get("account_number")
        ifsc = row.get("ifsc_code")

        if not account:
            continue

        normalized = re.sub(r"\D", "", account)

        # Skip if this is actually a card number
        if normalized in valid_cards:
            continue

        # Skip hallucinated account numbers
        if normalized not in valid_accounts:
            continue

        # Remove hallucinated IFSC codes
        if ifsc not in valid_ifscs:
            ifsc = None

        # Remove duplicate accounts
        if normalized in seen:
            continue

        seen.add(normalized)

        filtered.append({
            "account_number": account,
            "ifsc_code": ifsc
        })

    return filtered

def normalize_person(name):

    return " ".join(name.lower().split())

def filter_pan_relations(
    relations,
    pan_numbers,
    person_names
):

    valid_pans = {
        pan.upper()
        for pan in pan_numbers
    }

    valid_persons = {
        normalize_person(person)
        for person in person_names
    }

    filtered = []
    seen = set()

    for row in relations:

        pan = row.get("pan_number")
        person = row.get("person_name")

        if not pan:
            continue

        pan = pan.upper()

        # Skip hallucinated PANs
        if pan not in valid_pans:
            continue

        # Remove hallucinated Person Names
        if person is not None:

            if normalize_person(person) not in valid_persons:
                person = None

        # Remove duplicate PANs
        if pan in seen:
            continue

        seen.add(pan)

        filtered.append({
            "pan_number": pan,
            "person_name": person
        })

    return filtered