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