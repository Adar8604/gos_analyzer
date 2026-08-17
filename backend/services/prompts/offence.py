OFFENCE_PROMPT = """
    You are an FIU compliance analyst.

    Task:
    Analyze the following unstructured GOS (Ground of Suspicion) text and identify offensive details only.

    Extract:
    - Predicate offence(s)
    - Criminal activity
    - Modus operandi
    - Source of illicit funds
    - Movement/layering of funds
    - Victim(s), if mentioned
    - Accused/Suspect(s), if mentioned
    - Supporting evidence from the text

    Rules:
    - Use ONLY information explicitly present in the GOS.
    - Do NOT infer, assume, or add facts.
    - If a field is not mentioned, write "Not Mentioned".
    - Keep each answer concise (1-2 lines).

    GOS:
    {gos}
"""