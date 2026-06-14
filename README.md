# Vehicle Insurance Claim Intake System

### Validated Dynamic Questioning System with Retrieval-Grounded Triggering and Parallel State Fusion

A multi-turn claim intake engine that conducts structured interviews using **no LLM API calls at runtime**. All extraction, retrieval, and termination logic is rule-based and fully offline.

---

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm   # optional; system falls back to regex

# Run interactive intake
python src/demo_manual_loop.py

```

---

## System Components

| Module                      | Purpose                                                                                           |
| --------------------------- | ------------------------------------------------------------------------------------------------- |
| `src/state_extractor.py`  | Parallel NLP extraction — incident type, dates, vehicle, FIR, boolean flags                      |
| `src/retriever.py`        | Two-stage retrieval: hard filter → composite scoring (priority 50% + TF-IDF 30% + gap-fill 20%)  |
| `src/terminator.py`       | 5-check termination policy (user done, no questions, max turns, core fields, low-priority window) |
| `src/demo_manual_loop.py` | CLI demo loop with turn-by-turn logging                                                           |
| `src/validate.py`         | 4-pass corpus validation (schema, logic, dedup, coverage)                                         |
| `src/generate_corpus.py`  | Template × slot question generator                                                               |

---

## Corpus

- **1,265 raw questions** generated across 13 incident categories via template × slot expansion
- **839 validated questions** after 4-pass pipeline (exact dedup, Jaccard near-dedup at 0.85, schema checks, logic checks)
- Stored in `data/question_bank_validated.jsonl` (one JSON object per line)

---

## How It Works

1. User provides free-text describing the incident
2. **State extractor** runs all sub-extractors in parallel on the same text, merges into a delta, applies corrections/retractions
3. **Retrieval engine** hard-filters the 839-question bank (drops answered, already-extracted, unmatched triggers), then ranks survivors by composite score
4. **Terminator** checks 5 conditions in order; if any fires, intake ends
5. Best-scoring question is presented; loop repeats

A single utterance can fill 6+ fields simultaneously (parallel state fusion). If a user corrects a prior statement, the relevant field is retracted from state.

---

## No LLM Runtime Dependency

All extraction uses:

- **Keyword FSM** with subtype priority tiebreaking for incident classification
- **Regex** for registration numbers, FIR numbers, dates
- **`dateparser`** library for flexible date parsing ("yesterday", "5th March 2026", "March 10")
- **Vocabulary lookups** for vehicle makes/models, Indian cities, road types
- **`scikit-learn` TF-IDF** for relevance scoring (cosine similarity, bigrams)
- **Negation-first pattern matching** for boolean extraction

---

## Repository Structure

```
├── data/
│   ├── vocabulary.json
│   ├── claim_state_schema.json
│   ├── priority_policy.md
│   ├── question_bank_validated.jsonl    ← 839 questions
│   └── validation_report.json
├── schemas/
│   └── retrieval_output_schema.json
├── src/
│   ├── generate_corpus.py
│   ├── generate_corpus_ext.py
│   ├── validate.py
│   ├── retriever.py
│   ├── state_extractor.py
│   ├── terminator.py
│   └── demo_manual_loop.py
├── sample_runs/                         ← Turn-by-turn JSON logs
├── APPROACH.md                          ← Methodology document
└── requirements.txt
```
