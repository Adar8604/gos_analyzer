Parameter

{{PARAMETER}}

---

{{RUBRIC}}

---

Current STR

{{STR}}

---

Tasks

1. Evaluate ONLY the "{{PARAMETER}}" parameter.
2. Check every required item.
3. Identify which required items are present.
4. Identify which required items are missing.
5. Assign exactly one score between 0 and 5.
6. Explain why that score was assigned.

Return ONLY this JSON.

{
  "parameter": "{{PARAMETER}}",
  "score": 0,
  "present": [],
  "missing": [],
  "reason": ""
}

Rules:

- score must be a single integer (0,1,2,3,4,5)
- never return multiple scores
- never return the rubric
- never include markdown
- return valid JSON only
