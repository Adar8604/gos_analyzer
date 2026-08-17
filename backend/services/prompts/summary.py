SUMMARY_PROMPT = """
You are an AML (Anti-Money Laundering) analyst.

Analyze the following Ground of Suspicion (GOS) and provide:

1. Main transaction activity
2. Parties involved
3. Transaction amounts
4. Suspicious indicators
5. Overall conclusion

GOS:
{gos}

Return exactly 5 bullet points. 
"""