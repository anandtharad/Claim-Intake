
# Vehicle Insurance Claim Intake System – Approach & Methodology

## Objective

The objective of this solution is to build a lightweight conversational claim intake system that can:

* Extract structured claim information from free-form user responses.
* Maintain an evolving claim state throughout the conversation.
* Determine the most relevant next question to ask.
* Avoid redundant questioning.
* Terminate intelligently once sufficient information has been collected.

The design prioritizes:

* Fast response time
* Low computational overhead
* High explainability
* Deterministic behaviour
* Ease of maintenance and debugging

---

# Problem Framing

Instead of treating claim intake as a general chatbot problem, I modelled it as a structured information collection workflow.

Insurance claims ultimately require a fixed set of information to be collected before processing can begin. Therefore, the conversation can be viewed as a state completion problem.

```text
User Response
        ↓
Information Extraction
        ↓
Claim State Update
        ↓
Missing Information Detection
        ↓
Question Selection
        ↓
Claim Completion
```

This perspective allows the system to focus on collecting missing information rather than generating open-ended conversational responses.

---

# High-Level Architecture

```text
User Response
        ↓
State Extractor
        ↓
Claim State
        ↓
Question Retrieval & Ranking
        ↓
Next Question
        ↓
Termination Engine
```

The system is composed of three primary components:

1. State Extraction
2. Question Retrieval & Ranking
3. Termination Engine

---

# 1. State Extraction

## Purpose

Convert unstructured user responses into structured claim attributes.

Example:

```text
"My car was hit from the side by a bike in Pune."
```

Extracted information:

```json
{
  "category": "collision",
  "loss_location": {
    "city": "Pune"
  },
  "third_party_involved": true,
  "impact_direction": "side"
}
```

---

## Methodology

The extractor uses a combination of:

* Domain vocabulary matching
* Pattern-based extraction
* Regular expressions
* Optional NLP utilities where available

Examples of extracted entities include:

* Incident category
* Vehicle registration number
* Date and time references
* FIR numbers
* Location information
* Damage descriptions
* Third-party involvement indicators
* Fire, theft, and collision-specific attributes

Multiple extractors operate on the same user utterance, allowing several fields to be populated in a single conversational turn.

---

## Why a Rule-Based Extractor?

A deterministic extractor was chosen because claim intake involves a relatively constrained domain with predictable terminology.

Advantages include:

### Speed

Pattern matching and vocabulary-based extraction execute very quickly and are suitable for real-time interaction.

### Explainability

Every extracted field can be traced back to a specific rule, pattern, or vocabulary match.

### Consistency

The same input produces the same output across runs, making behaviour predictable and easy to validate.

### Auditability

Structured extraction logic is significantly easier to inspect and debug than black-box generation systems.

---

# 2. Claim State Management

The system maintains a structured claim state throughout the conversation.

Example:

```json
{
  "category": "collision",
  "loss_datetime": "...",
  "third_party_involved": true,
  "police_report_filed": false
}
```

Each new user response updates only the relevant fields while preserving previously collected information.

---

## Benefits

### Context Preservation

Information collected in earlier turns remains available throughout the conversation.

### Duplicate Prevention

Questions targeting already known information can be suppressed.

### Incremental Completion

The system continuously tracks which information is available and which information is still missing.

---

# 3. Question Retrieval & Ranking

## Problem

Once the claim state has been updated, the system must determine the most useful next question.

Rather than generating questions dynamically, the system retrieves questions from a curated question bank.

This ensures consistency and avoids unpredictable outputs.

---

## Candidate Filtering

Before ranking, the system removes ineligible questions.

Examples include:

* Questions already asked earlier in the conversation.
* Questions whose target fields are already populated.
* Questions that do not apply to the current incident type.
* Questions whose trigger conditions are not satisfied.

This filtering stage substantially reduces the search space before ranking begins.

---

## Ranking Strategy

After filtering, remaining candidates are scored using three signals:

```text
Score =
0.50 × Priority
+ 0.30 × Relevance
+ 0.20 × Gap-Fill
```

---

### Priority Score

Represents the business importance of a question.

Questions required for claim registration and liability determination receive higher priority than informational or administrative questions.

This ensures that critical claim information is collected early in the conversation.

---

### Relevance Score

The system uses TF-IDF similarity between:

* The current claim state
* Candidate questions

TF-IDF was selected because it is:

* Lightweight
* Fast
* Deterministic
* Easy to interpret

The insurance domain contains strong lexical signals such as:

```text
third party
vehicle registration
police report
FIR
collision
theft
fire
```

These keywords play an important role in determining useful follow-up questions.

---

## Evaluation of Embedding-Based Retrieval

Sentence-embedding approaches such as SBERT were evaluated during development.

While embeddings improved semantic matching, they occasionally prioritised semantically related questions over questions that were more useful for claim progression.

For example, after identifying that a third party was involved in an accident, embedding-based retrieval sometimes preferred questions discussing third-party involvement itself rather than collecting the next critical piece of information such as the third-party registration number.

Although these rankings were semantically reasonable, they were not always aligned with the operational goal of completing a claim efficiently.

In comparison, TF-IDF preserved important domain-specific keywords and consistently produced more practical follow-up questions for this workflow.

Given the requirements of being lightweight, fast, and predictable, TF-IDF provided the best balance between retrieval quality and system complexity.

---

### Gap-Fill Score

The ranking function also rewards questions that target fields which are currently missing from the claim state.

This encourages the system to move steadily toward claim completion rather than repeatedly exploring already-known information.

---

# Question Bank Design

A structured question bank was created to support retrieval.

Each question contains metadata such as:

* Question text
* Priority level
* Trigger conditions
* Target fields
* Applicable incident categories

Example:

```json
{
  "text": "What is the registration number of the third-party vehicle?",
  "priority": 2,
  "targets": {
    "fill_fields": ["third_party_vehicle_id"]
  }
}
```

This design allows retrieval logic to remain simple while keeping business rules configurable through data rather than code.

---

# 4. Termination Strategy

The system continuously evaluates whether additional questioning is necessary.

Termination occurs when one or more of the following conditions are met:

* Required information for the active claim type has been collected.
* No useful unanswered questions remain.
* The user explicitly indicates completion.
* The maximum turn limit is reached.

---

## Why Explicit Termination Logic?

Without a dedicated termination mechanism, conversational systems often continue asking low-value questions after sufficient information has already been gathered.

The termination layer ensures:

* Shorter conversations
* Reduced user effort
* Consistent completion behaviour
* Better overall user experience

---

# Key Design Decisions

| Decision                    | Reason                                                   |
| --------------------------- | -------------------------------------------------------- |
| Structured claim state      | Enables deterministic tracking of collected information  |
| Rule-based extraction       | Fast, explainable, and easy to validate                  |
| Question-bank retrieval     | Consistent and controllable question generation          |
| Trigger-based filtering     | Removes irrelevant candidates early                      |
| TF-IDF relevance scoring    | Lightweight and effective for domain-specific vocabulary |
| Gap-fill scoring            | Encourages efficient state completion                    |
| Explicit termination engine | Prevents unnecessary questioning                         |

---

# Conclusion

The final solution treats insurance claim intake as a structured state-completion problem rather than an open-ended conversational AI task.

By combining deterministic information extraction, state management, question-bank retrieval, TF-IDF-based relevance scoring, and explicit termination logic, the system remains lightweight, fast, explainable, and practical for real-world claim intake workflows.

The architecture is intentionally simple, auditable, and extensible, making it suitable for deployment in environments where reliability, transparency, and operational efficiency are more important than generative conversational capabilities.
