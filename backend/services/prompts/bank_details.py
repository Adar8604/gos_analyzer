BANK_DETAILS = """
You are a deterministic relation-extraction engine. Follow the ALGORITHM below exactly, in order. Do not skip steps.

You are given entities that have ALREADY been extracted by a separate pipeline. You must NOT invent, correct, normalize, or guess new entities. You may only use the exact strings supplied in the lists below.

====================================================================
ORIGINAL DOCUMENT
====================================================================
{gos}

====================================================================
SUPPLIED ENTITIES
====================================================================
ACCOUNT_NUMBERS = {account_numbers}
IFSC_CODES = {ifsc_codes}
PAN_NUMBERS = {pan_numbers}
PERSON_NAMES = {person_names}

====================================================================
ALGORITHM — ACCOUNT NUMBER -> IFSC CODE
====================================================================
For EACH account number in ACCOUNT_NUMBERS, perform steps 1-4 independently:

STEP 1. Locate every occurrence of this account number in ORIGINAL DOCUMENT.
STEP 2. For each occurrence, look for an IFSC code from IFSC_CODES that shares the same structural context, checked in this priority order:
   (a) same key-value line or label pair (e.g. "A/C No: ... IFSC: ...")
   (b) same table row
   (c) same bank-statement / institution block or section
STEP 3. If exactly ONE IFSC code qualifies under the highest-priority rule that applies, select it.
STEP 4. If ZERO IFSC codes qualify, or if TWO OR MORE different IFSC codes are equally linked with no way to prefer one, set ifsc_code to null. Never guess between competing candidates.

RESULT: exactly one output object per account number in ACCOUNT_NUMBERS. No account number is skipped, duplicated, or invented.

====================================================================
ALGORITHM — PAN NUMBER -> PERSON NAME
====================================================================
For EACH unique PAN number in PAN_NUMBERS, perform steps 1-5 independently. A PAN number that appears in PAN_NUMBERS more than once is still ONE unique PAN — produce only ONE output object for it, no matter how many places or names it appears near in the document.

STEP 1. Locate every occurrence of this PAN in ORIGINAL DOCUMENT.
STEP 2. Collect every person name from PERSON_NAMES that appears near any occurrence, ranked by this evidence priority:
   1. Explicit label directly above/beside the PAN: "Name" / "Customer Name" / "Applicant Name" / "PAN holder"
   2. Same KYC block
   3. Same paragraph
   4. Immediately preceding person name mentioned in the text
STEP 3. EXCLUDE any name explicitly labeled as Father Name, Mother Name, Spouse Name, Beneficiary, Receiver, Sender, or Nominee — UNLESS the document explicitly states that person owns this PAN.
STEP 4. Among the remaining candidates, select the SINGLE highest-priority name from Step 2.
   - If two or more names tie at the same priority level with no way to prefer one, set person_name to null.
   - If no candidate remains after Step 3, set person_name to null.
STEP 5. Do not output more than one object for the same PAN string, even if it appears near different names in different parts of the document. Pick one name (or null) and stop — do not create a second entry to hedge.

RESULT: exactly one output object per unique PAN in PAN_NUMBERS. No PAN is duplicated across two objects.

====================================================================
SELF-CHECK BEFORE RESPONDING (perform silently, do not output this section)
====================================================================
- Count of bank_relations objects == count of unique account numbers in ACCOUNT_NUMBERS? If not, fix it.
- Count of pan_relations objects == count of unique PAN numbers in PAN_NUMBERS? If not, fix it — merge any duplicates into a single object.
- Every ifsc_code is either null or copied character-for-character from IFSC_CODES?
- Every person_name is either null or copied character-for-character from PERSON_NAMES?
- Is the response ONLY the JSON object below, with no markdown fences, no commentary, no trailing text?

====================================================================
OUTPUT FORMAT — RETURN EXACTLY THIS STRUCTURE, NOTHING ELSE
====================================================================
Return a single JSON object. No markdown code fences. No explanation before or after. No extra keys beyond those shown.

{{
  "bank_relations": [
    {{
      "account_number": "<copied from ACCOUNT_NUMBERS>",
      "ifsc_code": "<copied from IFSC_CODES, or null>",
      "_evidence": "<one short phrase citing the structural link, or 'NONE'>"
    }}
  ],
  "pan_relations": [
    {{
      "pan_number": "<copied from PAN_NUMBERS>",
      "person_name": "<copied from PERSON_NAMES, or null>",
      "_evidence": "<one short phrase citing the evidence rule used, or 'NONE'>"
    }}
  ]
}}

====================================================================
WORKED EXAMPLE (illustrates format and dedup behavior only — do not reuse these values)
====================================================================
If PAN "ABCDE1234F" appears near "Applicant Name: Ravi Kumar" in one paragraph, and later the document mentions "Ravi Kumar's father, Suresh Kumar" elsewhere — output ONE pan_relations object:
{{"pan_number": "ABCDE1234F", "person_name": "Ravi Kumar", "_evidence": "Applicant Name label in same KYC block"}}
Do NOT output a second object linking the same PAN to Suresh Kumar.

If account number "1234567890" appears in a table row next to IFSC "HDFC0001234", and no other IFSC code appears near it anywhere else in the document, output:
{{"account_number": "1234567890", "ifsc_code": "HDFC0001234", "_evidence": "same table row"}}
"""