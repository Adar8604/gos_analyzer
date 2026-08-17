import re

class AccountIFSCExtractor:
    """
    Extracts IFSC codes from text.
    """

    @staticmethod
    def extract(text):

        entities = []

        
        # IFSC Code
        
        IFSC_PATTERN = re.compile(
            r'(?<![A-Z0-9])[A-Z]{4}0[A-Z0-9]{6}(?![A-Z0-9])',
            re.IGNORECASE
        )

        for match in IFSC_PATTERN.finditer(text):

            entities.append({
                "Entity": match.group().upper(),
                "Tag": "IFSC Code",
                "Score": 1.0
            })

        
        # Mobile Numbers
        
        mobile_numbers = set()

        MOBILE_PATTERN = re.compile(
            r'(?<!\d)(?:\+91[\s-]?|91[\s-]?|0)?([6-9]\d{9})(?!\d)'
        )

        for match in MOBILE_PATTERN.finditer(text):
            mobile_numbers.add(match.group(1))

        
        # Account Numbers
        

        ACCOUNT_PATTERN = re.compile(r'(?<!\d)\d{9,18}(?!\d)')

        for match in ACCOUNT_PATTERN.finditer(text):

            account = match.group()

            # Skip mobile numbers
            if account in mobile_numbers:
                continue

            # Skip obvious years
            if len(account) == 4 and account.startswith(("19", "20")):
                continue

            # Skip PIN codes
            if len(account) == 6:
                continue

            entities.append({
                "Entity": account,
                "Tag": "Account Number",
                "Score": 1.0
            })

        
        # Remove duplicates
        

        seen = set()
        result = []

        for entity in entities:

            key = (
                entity["Entity"].upper(),
                entity["Tag"]
            )

            if key not in seen:
                seen.add(key)
                result.append(entity)

        return result