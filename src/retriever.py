"""
retriever.py
------------
Question Retrieval Engine — Task 3

get_next_question(claim_state, question_bank) -> retrieval_output

Stage 1: Hard filter — drops questions whose triggers don't match claim state
         or whose targets are already filled.
Stage 2: Rank — composite score (priority + relevance + gap_fill)

No LLM API calls. Relevance scoring uses one of three backends, tried in order:
  1. sentence-transformers all-MiniLM-L6-v2  (semantic, best quality)
  2. scikit-learn TF-IDF cosine similarity    (lexical, good quality)
  3. keyword overlap                          (always available, baseline)
"""

import json
import os
import math
from typing import List, Dict, Optional, Any

SBERT_AVAILABLE = False
_SBERT_MODEL = None
try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity as _cos_sim
    import numpy as np
    _SBERT_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    SBERT_AVAILABLE = True
except Exception:
    pass

SKLEARN_AVAILABLE = False
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    SKLEARN_AVAILABLE = True
except ImportError:
    pass

RELEVANCE_BACKEND = (

    "tfidf" if SKLEARN_AVAILABLE else
    "keyword"
)

BASE = os.path.join(os.path.dirname(__file__), "..", "data")
BANK_PATH = os.path.join(BASE, "question_bank_validated.jsonl")




W_PRIORITY  = 0.50
W_RELEVANCE = 0.30
W_GAP_FILL  = 0.20

def load_question_bank(path: str = BANK_PATH) -> List[dict]:
    """Load validated question bank from JSONL."""
    qs = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                qs.append(json.loads(line))
    return qs





def _state_value(state: dict, field: str) -> Any:
    """Safely get a nested or flat field from claim state."""
    if field in state:
        return state[field]

    parts = field.split(".")
    obj = state
    for p in parts:
        if isinstance(obj, dict) and p in obj:
            obj = obj[p]
        else:
            return None
    return obj

def _field_is_known(state: dict, field: str) -> bool:
    """
    Return True if a field is considered 'known' (non-null, non-empty).
    Also checks already_extracted_categories.
    """
    already = state.get("already_extracted_categories", [])


    if field in already:
        return True


    base = field.split("_")[0] if "_" in field else field
    if any(a.startswith(base) for a in already):

        if field in already or base in already:
            return True


    val = _state_value(state, field)
    if val is None:
        return False
    if isinstance(val, bool):
        return True
    if isinstance(val, (int, float)):
        return True
    if isinstance(val, str):
        return val.strip().upper() not in ("", "NA", "NULL", "NONE", "UNKNOWN")
    if isinstance(val, list):
        return len(val) > 0
    if isinstance(val, dict):
        return any(v is not None for v in val.values())
    return False

def _trigger_matches(q: dict, state: dict) -> bool:
    """
    Check all triggers in q against claim_state.
    Returns True only if ALL trigger conditions are satisfied.
    """
    triggers = q.get("triggers", {})


    it_triggers = triggers.get("incident_type", [])
    state_category = state.get("category")
    if it_triggers and state_category not in it_triggers:
        return False


    req_fields = triggers.get("required_fields_present", [])
    for rf in req_fields:
        if not _field_is_known(state, rf):
            return False


    bool_conditions = {
        k: v for k, v in triggers.items()
        if k not in ("incident_type", "required_fields_present")
        and isinstance(v, bool)
    }
    for field, expected_val in bool_conditions.items():
        actual_val = _state_value(state, field)
        if actual_val is None:

            pass
        elif actual_val != expected_val:
            return False

    return True

def _target_already_filled(q: dict, state: dict) -> bool:
    """
    Return True if ALL fill_fields of this question are already known.
    If all targets are already filled, this question adds no value.
    """
    fill_fields = q.get("targets", {}).get("fill_fields", [])
    if not fill_fields:
        return False
    return all(_field_is_known(state, ff) for ff in fill_fields)

def hard_filter(questions: List[dict], state: dict) -> List[dict]:
    """
    Stage 1: Keep only questions that:
      - Are not already answered (not in answered_question_ids)
      - Whose question_field is not in already_extracted_categories
      - Whose triggers ALL match current claim state
      - Whose targets are not all already known
    """
    answered = set(state.get("answered_question_ids", []))
    extracted = set(state.get("already_extracted_categories", []))

    candidates = []
    for q in questions:

        if q["id"] in answered:
            continue


        qf = q.get("question_field", "")
        if qf in extracted:
            continue

        qf_base = qf.rsplit("_", 1)[0] if "_" in qf else qf
        if qf_base in extracted:
            continue


        if not _trigger_matches(q, state):
            continue


        if state.get("police_report_filed") is False:
            fill_fields = q.get("targets", {}).get("fill_fields", [])
            if any(ff in ("fir_number", "police_station") for ff in fill_fields):
                continue


        if _target_already_filled(q, state):
            continue

        candidates.append(q)

    return candidates





def _priority_score(q: dict) -> float:
    """Higher priority (lower int) → higher score. Priority 1 → 1.0, Priority 5 → 0.2"""
    p = q.get("priority", 3)
    return (6 - p) / 5.0

def _gap_fill_score(q: dict, state: dict) -> float:
    """
    Fraction of fill_fields NOT yet known.
    = questions with more unknowns to fill are preferred.
    """
    fill_fields = q.get("targets", {}).get("fill_fields", [])
    if not fill_fields:
        return 0.0
    unknown = sum(1 for ff in fill_fields if not _field_is_known(state, ff))
    return unknown / len(fill_fields)

def _build_state_text(state: dict) -> str:
    """Convert claim state to a plain text string for TF-IDF."""
    parts = []
    category = state.get("category", "")
    if category:
        parts.append(category.replace("_", " "))

    loc = state.get("loss_location") or {}
    if isinstance(loc, dict):
        if loc.get("city"):
            parts.append(loc["city"])
        if loc.get("road_type"):
            parts.append(loc["road_type"].replace("_", " "))

    for field in ["weather_condition", "road_condition", "lane_action",
                  "impact_direction", "vehicle_moving_status", "speed_estimate"]:
        val = state.get(field)
        if val:
            parts.append(str(val).replace("_", " "))


    if state.get("third_party_involved"):
        parts.append("third party involved")
    if state.get("police_report_filed") is False:
        parts.append("no police report")
    if state.get("police_report_filed"):
        parts.append("police report filed")
    if state.get("drivable") is False:
        parts.append("not drivable")

    return " ".join(parts) if parts else category or "unknown"

def _relevance_score_sbert(candidates: List[dict], state: dict) -> Dict[str, float]:
    """
    Semantic relevance via sentence-transformers all-MiniLM-L6-v2.
    Encodes the current claim state summary + all candidate question texts
    in one batch, then returns cosine similarity scores normalised to [0, 1].
    """
    if not SBERT_AVAILABLE or not candidates:
        return {q["id"]: 0.5 for q in candidates}
    try:
        state_text = _build_state_text(state)
        q_texts = [q["text"] for q in candidates]
        all_texts = [state_text] + q_texts
        embeddings = _SBERT_MODEL.encode(all_texts, convert_to_numpy=True,
                                          show_progress_bar=False)
        state_emb = embeddings[0:1]
        q_embs    = embeddings[1:]
        sims = _cos_sim(state_emb, q_embs).flatten()

        lo, hi = sims.min(), sims.max()
        if hi > lo:
            sims = (sims - lo) / (hi - lo)
        else:
            sims = np.ones_like(sims) * 0.5
        return {q["id"]: float(sims[i]) for i, q in enumerate(candidates)}
    except Exception:
        return {q["id"]: 0.5 for q in candidates}

def _relevance_score_tfidf(candidates: List[dict], state: dict) -> Dict[str, float]:
    """
    TF-IDF cosine similarity between state text and each question text.
    Returns {qid: score}.
    """
    if not SKLEARN_AVAILABLE or not candidates:
        return {q["id"]: 0.5 for q in candidates}

    state_text = _build_state_text(state)
    texts = [state_text] + [q["text"] for q in candidates]

    try:
        vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            min_df=1,
            stop_words=None,
            max_features=5000
        )
        tfidf_matrix = vectorizer.fit_transform(texts)
        state_vec = tfidf_matrix[0]
        q_vecs = tfidf_matrix[1:]
        sims = cosine_similarity(state_vec, q_vecs).flatten()


        min_s, max_s = sims.min(), sims.max()
        if max_s > min_s:
            sims = (sims - min_s) / (max_s - min_s)
        else:
            sims = np.ones_like(sims) * 0.5

        return {q["id"]: float(sims[i]) for i, q in enumerate(candidates)}
    except Exception:
        return {q["id"]: 0.5 for q in candidates}

def _relevance_score_fallback(q: dict, state: dict) -> float:
    """
    Keyword-overlap relevance when sklearn is unavailable.
    """
    state_text = _build_state_text(state).lower()
    q_text = q.get("text", "").lower()
    state_words = set(state_text.split())
    q_words = set(q_text.split())
    if not state_words or not q_words:
        return 0.5
    overlap = len(state_words & q_words)
    return min(1.0, overlap / max(len(q_words), 1) * 2)

def score_candidates(candidates: List[dict], state: dict) -> List[Dict]:
    """
    Compute composite score for each candidate and return sorted list.
    """
    if not candidates:
        return []


    if RELEVANCE_BACKEND == "sbert":
        relevance_map = _relevance_score_sbert(candidates, state)
    elif RELEVANCE_BACKEND == "tfidf":
        relevance_map = _relevance_score_tfidf(candidates, state)
    else:
        relevance_map = {q["id"]: _relevance_score_fallback(q, state) for q in candidates}

    scored = []
    for q in candidates:
        ps = _priority_score(q)
        rs = relevance_map.get(q["id"], 0.5)
        gs = _gap_fill_score(q, state)
        composite = W_PRIORITY * ps + W_RELEVANCE * rs + W_GAP_FILL * gs

        scored.append({
            "question": q,
            "score_breakdown": {
                "priority": round(ps, 4),
                "relevance": round(rs, 4),
                "gap_fill": round(gs, 4),
                "composite": round(composite, 4),
            }
        })

    scored.sort(key=lambda x: x["score_breakdown"]["composite"], reverse=True)
    return scored

def get_next_question(
    claim_state: dict,
    question_bank: List[dict]
) -> Optional[dict]:
    """
    Main retrieval function.

    Args:
        claim_state: Current JSON claim state
        question_bank: Full validated question bank (list of question dicts)

    Returns:
        retrieval_output dict, or None if no questions remain.
    """

    candidates = hard_filter(question_bank, claim_state)

    if not candidates:
        return None


    scored = score_candidates(candidates, claim_state)
    best = scored[0]
    q = best["question"]

    return {
        "question_id": q["id"],
        "question_text": q["text"],
        "question_field": q.get("question_field", ""),
        "trigger": claim_state.get("category", "unknown"),
        "score_breakdown": best["score_breakdown"],
        "audit": {
            "hard_filter_pool_size": len(candidates),
            "total_suppressed": len(question_bank) - len(candidates),
            "relevance_backend": RELEVANCE_BACKEND,
            "selected_reason": (
                f"Highest composite score ({best['score_breakdown']['composite']:.4f}) "
                f"among {len(candidates)} candidates after hard filter. "
                f"Priority={q.get('priority')}, "
                f"Category={q.get('category_tag','?')}."
            ),
            "answered_so_far": len(claim_state.get("answered_question_ids", [])),
            "extracted_so_far": len(claim_state.get("already_extracted_categories", [])),
        }
    }

if __name__ == "__main__":
    import sys as _sys
    print("Loading question bank...")
    bank = load_question_bank()
    print(f"Loaded {len(bank)} validated questions.")
    print(f"Relevance backend: {RELEVANCE_BACKEND}")

    test_states = [
        {
            "name": "Initial collision state",
            "state": {
                "category": "collision",
                "loss_datetime": "Feb 3rd, 2026",
                "loss_location": {"city": "Pune", "road_type": "urban"},
                "vehicle": {"make": "Honda", "model": "City", "year": 2021},
                "already_extracted_categories": ["incident_type"],
                "answered_question_ids": [],
            },
        },
        {
            "name": "Fire incident",
            "state": {
                "category": "fire",
                "loss_datetime": None,
                "loss_location": {"city": None, "road_type": None},
                "already_extracted_categories": ["fire"],
                "answered_question_ids": [],
            },
        },
    ]

    print("\n" + "=" * 60)
    for test in test_states:
        print(f"\nTest: {test['name']}")
        result = get_next_question(test["state"], bank)
        if result:
            print(f"  -> Q{result['question_id']}: {result['question_text'][:80]}")
            print(f"     Score: {result['score_breakdown']}")
            print(f"     Backend: {result['audit']['relevance_backend']}")
            print(f"     Pool: {result['audit']['hard_filter_pool_size']} candidates")
        else:
            print("  -> No question returned (pool exhausted).")
    print("\nRetriever self-test complete.")
