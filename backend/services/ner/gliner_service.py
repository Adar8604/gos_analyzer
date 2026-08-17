from gliner import GLiNER
import re

from services.ner.regex_extractor import RegexExtractor


class NERService:
    """Service for performing named entity recognition using GLiNER."""

    _model = None
    def __init__(self):

        if NERService._model is None:

            NERService._model = GLiNER.from_pretrained(
                "urchade/gliner_medium-v2.1"
            )
        self.model = NERService._model

    def chunk_text(
        self,
        text,
        chunk_size=300,
        overlap=50
    ):
        """Process text and extract named entities.

        Args:
            text: Input text to analyze.

        Returns:
            Extracted entities.
        """

        words = text.split()

        chunks = []

        start = 0

        while start < len(words):

            end = start + chunk_size

            chunks.append(
                " ".join(words[start:end])
            )

            start += chunk_size - overlap

        return chunks

    def mask_regex_entities(self, text, regex_entities):
        """
        Takes the given text and entities returned by regex, and masks them with
        placeholder to prevent the LLM from learning patterns in names, race,
        gender, location etc.

        args:
            text: Input text to analyze

        returns:
            Same text but with names entities masked.
        """

        for entity in regex_entities:

            placeholder = (
                f"[{entity['Tag'].upper().replace(' ', '_')}]"
            )

            text = re.sub(
                re.escape(entity["Entity"]),
                placeholder,
                text,
                count=1
            )

        return text

    def extract_entities(self, text, labels):
        """
        Takes the given text and extracts entities associated with
        the provided labels

        args:
            text: Input text to extract entities from
        
        returns:
            List of final entities extracted.
        """

        # Regex Extraction
        regex_entities = RegexExtractor.extract(text)

        # Mask structured entities
        masked_text = self.mask_regex_entities(
            text,
            regex_entities
        )

        # Chunk text
        chunks = self.chunk_text(
            masked_text,
            chunk_size=300,
            overlap=50
        )

        # Run GLiNER on chunks
        gliner_entities = []

        for chunk in chunks:

            entities = self.model.predict_entities(
                chunk,
                labels,
                threshold=0.35
            )

            gliner_entities.extend(entities)

        # Label Mapping
        label_mapping = {

            "person": "Person",

            "company": "Organization",
            "organization": "Organization",
        }

        ml_entities = []

        for entity in gliner_entities:

            entity_text = entity["text"].strip()

            # Ignore placeholders
            if (
                entity_text.startswith("[")
                and entity_text.endswith("]")
            ):
                continue

            tag = label_mapping.get(
                entity["label"].lower(),
                entity["label"].title()
            )

            ml_entities.append({
                "Entity": entity_text,
                "Tag": tag,
                "Score": round(entity["score"], 3)
            })

        # Merge + Deduplicate
        seen = set()
        final_entities = []

        for entity in ml_entities + regex_entities:

            key = (
                entity["Entity"].lower().strip(),
                entity["Tag"].lower().strip()
            )

            if key not in seen:

                seen.add(key)

                final_entities.append(entity)

        return final_entities
    
ner_service = NERService()