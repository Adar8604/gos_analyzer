# GOS Analyzer

**Financial Intelligence Workspace** for structured analysis, linkage discovery, and quality assessment of Suspicious Transaction Reports (STRs) and Grounds of Suspicion (GOS).

GOS Analyzer brings three investigation workflows into a single workspace, enabling users to move from **GOS analysis → STR linkage → STR quality assessment**.

---

## GOS Analyzer

Analyze a GOS through multiple focused analysis views:

* **Overall Analysis** — Provides a consolidated summary of the GOS.
* **NER Extraction** — Identifies persons, organisations, locations, and key identifiers such as PAN, account numbers, UTRs, IFSC codes, and related entities.
* **Offence Details** — Presents potential offences, criminal activities, modus operandi, source of illicit funds, accused and victims, and supporting evidence.
* **Transaction Summary** — Presents the flow of funds in a structured table, including date, amount, credit/debit nature, transaction mode, account, and location.
* **Keyword Search** — Highlights user-specified keywords within the GOS to quickly locate relevant references.

---

## GOS Linker

Identify relationships across multiple STRs using graph-based linkage analysis.

Upload an **Excel or CSV** containing STR records and explore connections based on common identifiers such as:

`PAN` · `Account Number` · `UPI ID` · `Mobile Number` · `Card Number`

The resulting graph visualization helps users identify **common entities, interconnected STRs, and potential networks** across reports.

---

## STR Quality Assessment

Evaluate the quality of an STR against defined assessment parameters and identify the most appropriate **Law Enforcement Agency (LEA) tagging**.

Upload an STR to assess its quality and support consistent downstream classification and handling.

---

## Workspace Overview

```text
                    FINANCIAL INTELLIGENCE WORKSPACE
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
          ▼                    ▼                    ▼
     GOS Analyzer         GOS Linker       STR Quality Assessment
          │                    │                    │
          ▼                    ▼                    ▼
     Analyze GOS          Link Multiple          Assess STR
                           STRs                    Quality
          │                   │                    │
          │                   │                    │
          ├── Summary         ├── PAN              ├── Quality
          ├── NER             ├── Account            Assessment
          ├── Offence         ├── UPI ID           └── LEA Tagging
          ├── Transaction     ├── Mobile
          └── Keyword Search  └── Card
```

GOS Analyzer is designed to provide a **single, focused workspace for financial intelligence analysis**, helping users extract relevant information, discover linkages, and assess STR quality efficiently.
