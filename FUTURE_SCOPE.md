# Limitations and Future Improvements

This solution was designed to be lightweight, fast, deterministic, and easy to reason about. While it performs well for structured insurance claim intake, there are a few known limitations.

## Current Limitations

### Rule-Based Information Extraction

The extractor relies primarily on domain vocabularies, keyword matching, and regular expressions.

While this works well for most common claim descriptions, it can struggle with:

* Highly unusual phrasing
* Long and complex narratives
* Multiple incidents mentioned in the same response
* Contradictory statements and corrections
* Spelling mistakes and informal language

### Lexical Retrieval

The current retrieval system uses TF-IDF based relevance scoring.

This performs well for insurance-specific terminology but depends heavily on keyword overlap. Questions may be ranked lower when users describe the same concept using very different wording.

### Limited Dependency Awareness

The current ranking system considers:

* Question priority
* Relevance
* Gap-filling potential

However, it does not explicitly model dependencies between fields.

For example, after determining that a third party was involved in a collision, the system may not always prioritize collecting the third-party vehicle details ahead of other semantically relevant questions.

---

## Future Improvements

### Dependency-Aware Question Ranking

A natural next step would be to introduce dependency-aware boosting.

Examples:

```text
third_party_involved = true
    → prioritize third_party_vehicle_id
    → prioritize third_party_driver_name

police_report_filed = true
    → prioritize FIR number
    → prioritize police station
```

This would help the conversation follow a more natural claim-processing workflow.

### Hybrid TF-IDF + Embedding Retrieval

During experimentation, sentence-embedding models such as SBERT were evaluated.

While SBERT improved semantic matching, it occasionally favored semantically similar questions over the next operationally useful question needed to progress the claim.

A promising future approach would be to combine:

* Dependency-aware ranking
* Structured state information
* SBERT-based semantic retrieval

In this setup:

1. Dependency rules would identify the most important missing information.
2. SBERT would rank questions within that constrained candidate set.

This would preserve workflow correctness while improving semantic understanding of user responses.

---

## Final Note

The current implementation intentionally prioritizes simplicity, explainability, and deterministic behaviour. The architecture was designed so that more advanced retrieval or ranking strategies can be introduced later without requiring significant changes to the overall system design.
