import re

def luhn_check(card):

    digits = [int(d) for d in card]

    checksum = 0
    double = False

    for d in reversed(digits):

        if double:
            d *= 2

            if d > 9:
                d -= 9

        checksum += d
        double = not double

    return checksum % 10 == 0

def valid_card_prefix(card):

    if card.startswith("4"):
        return True

    if card.startswith(("34", "37")):
        return True

    if card.startswith(("51", "52", "53", "54", "55")):
        return True

    prefix4 = int(card[:4])

    if 2221 <= prefix4 <= 2720:
        return True

    if card.startswith(("60", "65")):
        return True

    if card.startswith(("81", "82")):
        return True

    return False

class RegexExtractor:

    @staticmethod
    def extract(text):

        entities = []
        card_numbers = set()
        mobile_numbers = set()
        structured_ids = set()

        # PAN
        for match in re.finditer(
            r"\b[A-Z]{5}[0-9]{4}[A-Z]\b",
            text,
            flags=re.IGNORECASE
        ):
            entities.append({
                "Entity": match.group().upper(),
                "Tag": "PAN Number",
                "Score": 1.0
            })

            structured_ids.add(match.group().upper())


        # IFSC
        
        for match in re.finditer(
            r"(?<![A-Z0-9])[A-Z]{4}0[A-Z0-9]{6}(?![A-Z0-9])",
            text,
            flags=re.IGNORECASE
        ):

            ifsc = match.group().upper()

            entities.append({
                "Entity": ifsc,
                "Tag": "IFSC Code",
                "Score": 1.0
            })

            structured_ids.add(ifsc)
            

        # UTR Number
        UTR_PATTERNS = [

            # UTR: N123456789012
            r"(?:UTR(?:\s*No)?|UTR Number)\s*[:\-]?\s*([A-Z0-9]{10,30})",

            # Ref No: HDFC1234567890
            r"(?:Reference(?:\s*No)?|Ref(?:\s*No)?)\s*[:\-]?\s*([A-Z0-9]{10,30})",

            # Transaction Reference: ICIC1234567890
            r"(?:Transaction\s*Reference)\s*[:\-]?\s*([A-Z0-9]{10,30})"
        ]

        BLACKLIST = {
            "DELHI",
            "BIHAR",
            "ADDRESS",
            "MUMBAI",
            "KOLKATA",
            "CHENNAI",
            "PUNE",
            "HYDERABAD",
            "BANGALORE"
        }

        for pattern in UTR_PATTERNS:

            for match in re.finditer(
                pattern,
                text,
                flags=re.IGNORECASE
            ):

                utr = match.group(1).upper()

                # Must contain both letters and digits
                if not (
                    any(c.isalpha() for c in utr)
                    and any(c.isdigit() for c in utr)
                ):
                    continue

                # Reject location-like values
                if any(
                    utr.startswith(word)
                    for word in BLACKLIST
                ):
                    continue

                entities.append({
                    "Entity": utr,
                    "Tag": "UTR Number",
                    "Score": 1.0
                })

                structured_ids.add(utr)


        # Mobile Numbers
        MOBILE_PATTERN = r"(?<!\d)(?:\+91[\s\-]?|91[\s\-]?|0)?[6-9]\d{9}(?!\d)"

        for match in re.finditer(MOBILE_PATTERN, text):

            original = match.group().strip()

            raw_digits = re.sub(r"\D", "", original)

            if len(raw_digits) > 12:
                continue

            digits = raw_digits

            if digits.startswith("91") and len(digits) == 12:
                digits = digits[2:]

            elif digits.startswith("0") and len(digits) == 11:
                digits = digits[1:]

            if len(digits) != 10:
                continue

            if digits[0] not in "6789":
                continue

            entities.append({
                "Entity": original,
                "Tag": "Mobile Number",
                "Score": 1.0
            })

            mobile_numbers.add(digits)

            
        # Email
        emails = set()

        for match in re.finditer(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
            text,
            flags=re.IGNORECASE
        ):
            email = match.group()

            emails.add(email.lower())

            entities.append({
                "Entity": email,
                "Tag": "Email",
                "Score": 1.0
            })


        # UPI ID

        UPI_PATTERN = re.compile(
            r"\b[a-zA-Z0-9][a-zA-Z0-9._-]{1,99}@[A-Za-z][A-Za-z0-9._-]{1,49}\b"
        )

        COMMON_EMAIL_SUFFIXES = (
            ".com",
            ".co.in",
            ".in",
            ".org",
            ".net",
            ".edu",
            ".gov"
        )

        KNOWN_UPI_HANDLES = {
            "upi",
            "ybl",
            "ibl",
            "axl",
            "apl",
            "paytm",
            "oksbi",
            "okaxis",
            "okicici",
            "okhdfcbank",
            "okyesbank",
            "okbizaxis",
            "airtel",
            "jio",
            "pthdfc",
            "barodampay",
            "fbl",
            "mahb",
            "indus",
            "kotak"
        }

        for match in UPI_PATTERN.finditer(text):

            upi = match.group()

            # Already extracted as Email
            if upi.lower() in emails:
                continue

            handle = upi.split("@", 1)[1].lower()

            # Looks like an email domain
            if any(handle.endswith(suffix) for suffix in COMMON_EMAIL_SUFFIXES):
                continue

            entities.append({
                "Entity": upi,
                "Tag": "UPI ID",
                "Score": 1.0
            })



        # Card Number

        CARD_PATTERN = re.compile(
            r'(?<!\d)(?:\d[ -]?){13,19}(?!\d)'
        )

        CARD_KEYWORDS = {
            "card",
            "card no",
            "card number",
            "credit card",
            "debit card",
            "visa",
            "mastercard",
            "master card",
            "rupay",
            "amex",
            "american express",
            "diners",
            "jcb"
        }

        WINDOW = 60

        for match in CARD_PATTERN.finditer(text):

            original = match.group()

            card = re.sub(r"[ -]", "", original)

            # Valid length
            if not (13 <= len(card) <= 19):
                continue

            if not valid_card_prefix(card):
                continue

            # Luhn validation
            if not luhn_check(card):
                continue

            start = max(0, match.start() - WINDOW)
            end = min(len(text), match.end() + WINDOW)

            context = text[start:end].lower()

            ACCOUNT_KEYWORDS = {
                "account",
                "a/c",
                "account no",
                "account number",
                "ac no",
                "beneficiary account",
                "customer account"
            }

            if any(keyword in context for keyword in ACCOUNT_KEYWORDS):
                continue

            has_card_context = any(
                keyword in context
                for keyword in CARD_KEYWORDS
            )

            if not has_card_context:
                continue

            score = 1.0

            card_numbers.add(card)
            entities.append({
                "Entity": original,
                "Tag": "Card Number",
                "Score": score
            })

        # ----------------------------
        # Account Numbers
        # ----------------------------

        ACCOUNT_PATTERN = re.compile(
            r'\b(?<!\d)\d{9,18}(?!\d)'
        )

        for match in ACCOUNT_PATTERN.finditer(text):

            account = match.group()

            normalized = re.sub(r"\D", "", account)

            # Skip mobile numbers
            if normalized in mobile_numbers:
                continue

            # Skip card numbers
            if normalized in card_numbers:
                continue

            # Skip obvious years
            if len(normalized) == 4 and normalized.startswith(("19", "20")):
                continue

            # Skip PIN codes
            if len(normalized) == 6:
                continue

            entities.append({
                "Entity": account,
                "Tag": "Account Number",
                "Score": 1.0
            })


        # Amount
        # amount_patterns = [

        #     r"₹\s?\d[\d,]*(?:\.\d+)?\s*(?:lakh|lakhs|lac|lacs|crore|crores|cr|thousand|million)?",

        #     r"INR\s+\d[\d,]*(?:\.\d+)?\s*(?:lakh|lakhs|lac|lacs|crore|crores|cr|thousand|million)?",

        #     r"Rs\.?\s*\d[\d,]*(?:\.\d+)?\s*(?:lakh|lakhs|lac|lacs|crore|crores|cr|thousand|million)?"
        # ]

        # for pattern in amount_patterns:

        #     for match in re.finditer(
        #         pattern,
        #         text,
        #         flags=re.IGNORECASE
        #     ):
        #         entities.append({
        #             "Entity": match.group().strip(),
        #             "Tag": "Amount",
        #             "Score": 1.0
        #         })
                
        # Dates
        date_patterns = [

            r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",

            r"\b\d{4}-\d{2}-\d{2}\b",

            r"\b\d{1,2}\s(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s\d{4}\b",

            r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s\d{1,2},?\s\d{4}\b"
        ]

        for pattern in date_patterns:

            for match in re.finditer(
                pattern,
                text,
                flags=re.IGNORECASE
            ):
                entities.append({
                    "Entity": match.group(),
                    "Tag": "Date",
                    "Score": 1.0
                })

        # Deduplicate
        seen = set()
        unique_entities = []

        for entity in entities:

            key = (
                entity["Entity"].lower(),
                entity["Tag"].lower()
            )

            if key not in seen:
                seen.add(key)
                unique_entities.append(entity)

        return unique_entities