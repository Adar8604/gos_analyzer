import json

from .config import client, MODEL_NAME
from .utils import (
    load_yaml,
    load_text,
    rubric_to_prompt,
    build_system_prompt,
)

SYSTEM_PROMPT = build_system_prompt()


def score_parameter(parameter_name, str_text, regex_matches=None):

    if regex_matches is None:
        regex_matches = {}

    rubric = load_yaml(f"{parameter_name}.yaml")

    rubric_text = rubric_to_prompt(rubric)

    template = load_text("parameter_scoring.md")

    prompt = (
        template
        .replace("{{PARAMETER}}", rubric["parameter"])
        .replace("{{RUBRIC}}", rubric_text)
        .replace("{{STR}}", str_text)
    )

    response = client.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        format="json",
        options={
            "temperature": 0,
            "num_predict": 512,
        },
    )

    result = json.loads(response["message"]["content"])

    present = set(result.get("present", []))
    missing = set(result.get("missing", []))

    # ---------------------------------------------------
    # Override regex-detectable fields for Completeness
    # ---------------------------------------------------

    if parameter_name.lower() == "completeness":

        for item in rubric.get("required_items", []):

            if item in regex_matches:

                if regex_matches[item]:
                    present.add(item)
                    missing.discard(item)
                else:
                    present.discard(item)
                    missing.add(item)

    result["present"] = sorted(present)
    result["missing"] = sorted(missing)

    # ---------------------------------------------------
    # Score Calculation
    # ---------------------------------------------------

    required_items = rubric.get("required_items", [])
    required_count = len(required_items)

    present_count = sum(
        1 for item in required_items
        if item in result["present"]
    )

    if required_count == 0:
        score = 0
    else:
        completion = present_count / required_count

        if completion == 1:
            score = 5
        elif completion >= 0.8:
            score = 4
        elif completion >= 0.6:
            score = 3
        elif completion >= 0.4:
            score = 2
        elif completion > 0:
            score = 1
        else:
            score = 0

    result["score"] = score

    return result