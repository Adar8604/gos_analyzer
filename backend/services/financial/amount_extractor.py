import re


class AmountExtractor:

    @staticmethod
    def extract(text):

        amounts = []

        amount_patterns = [

            # ₹5 lakh / ₹5,00,000 / ₹2.5 crore
            r"₹\s*\d[\d,]*(?:\.\d+)?\s*(?:lakh|lakhs|lac|lacs|crore|crores|cr|thousand|million)?",

            # Rs 5 lakh / Rs.5 lakh
            r"Rs\.?\s*\d[\d,]*(?:\.\d+)?\s*(?:lakh|lakhs|lac|lacs|crore|crores|cr|thousand|million)?",

            # INR 5 lakh / INR:5 lakh
            r"INR[:\s]*\d[\d,]*(?:\.\d+)?\s*(?:lakh|lakhs|lac|lacs|crore|crores|cr|thousand|million)?",

            # Plain textual amounts
            r"\b\d[\d,]*(?:\.\d+)?\s*(?:lakh|lakhs|lac|lacs|crore|crores|cr|thousand|million)\b"
        ]

        seen = set()

        for pattern in amount_patterns:

            for match in re.finditer(
                pattern,
                text,
                flags=re.IGNORECASE
            ):

                amount = match.group().strip()

                key = amount.lower()

                if key not in seen:

                    seen.add(key)

                    amounts.append(amount)

        return amounts
    
    @staticmethod
    def normalize_to_float(amount_str: str) -> float:
        """
        Converts Indian formatted financial strings into strict floats.
        e.g., 'Rs. 58.35 lacs' -> 5835000.0
        """
        # Clean the string: remove currency symbols and commas
        clean_str = re.sub(r"[₹,]|rs\.?|inr", "", amount_str, flags=re.IGNORECASE).strip()
        
        # Extract the base number
        number_match = re.search(r"(\d+(?:\.\d+)?)", clean_str)
        if not number_match:
            return 0.0
            
        base_val = float(number_match.group(1))
        
        # Apply multipliers using strict regex word boundaries
        lower_str = clean_str.lower()
        
        # Matches "lakh", "lakhs", "lac", "lacs" exactly as standalone words
        if re.search(r"\b(lakhs?|lacs?)\b", lower_str):
            base_val *= 100000.0
            
        # Matches "crore", "crores", "cr"
        elif re.search(r"\b(crores?|cr)\b", lower_str):
            base_val *= 10000000.0
            
        # Matches "million", "millions"
        elif re.search(r"\bmillions?\b", lower_str):
            base_val *= 1000000.0
            
        # Matches "thousand", "thousands"
        elif re.search(r"\bthousands?\b", lower_str):
            base_val *= 1000.0
            
        return round(base_val, 2)