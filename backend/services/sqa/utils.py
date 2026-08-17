from pathlib import Path
import yaml
import streamlit as st

# Directory containing utils.py
BASE_DIR = Path(__file__).resolve().parent

# Prompt directory inside backend/services/sqa/prompts
PROMPTS_DIR = BASE_DIR / "prompts"


@st.cache_data
def load_yaml(path):
    path = Path(path)

    if not path.is_absolute():
        path = PROMPTS_DIR / path

    if not path.exists():
        raise FileNotFoundError(f"YAML file not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if data is None:
        raise ValueError(f"{path} is empty.")

    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a YAML dictionary.")

    return data


@st.cache_data
def load_text(path):
    path = Path(path)

    if not path.is_absolute():
        path = PROMPTS_DIR / path

    if not path.exists():
        raise FileNotFoundError(f"Text file not found: {path}")

    return path.read_text(encoding="utf-8")


def build_system_prompt():
    system = load_yaml("system.yaml")

    prompt = f"""
{system['role']}

Objective

{system['objective']}

Instructions

"""

    for instruction in system["instructions"]:
        prompt += f"- {instruction}\n"

    return prompt.strip()


def rubric_to_prompt(rubric):
    required = "\n".join(
        f"- {x}" for x in rubric.get("required_items", [])
    )

    scoring = ""

    for score in sorted(rubric.get("scoring", {}).keys(), reverse=True):
        scoring += (
            f"{score} = {rubric['scoring'][score]['description']}\n"
        )

    return f"""
Purpose

{rubric.get("purpose","")}

Required Items

{required}

Scoring

Choose EXACTLY ONE score from 0 to 5.

{scoring}

Rules:
- Choose only ONE score.
- Do not return multiple scores.
- Do not reproduce the rubric.
"""