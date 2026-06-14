import json
import os
import hashlib
from collections import defaultdict, Counter
from typing import List, Dict, Tuple


BASE = os.path.join(os.path.dirname(__file__), "..", "data")
RAW_PATH      = os.path.join(BASE, "question_bank_raw.jsonl")
VALID_PATH    = os.path.join(BASE, "question_bank_validated.jsonl")
REJECT_PATH   = os.path.join(BASE, "rejected_questions.jsonl")
REPORT_PATH   = os.path.join(BASE, "validation_report.json")
VOCAB_PATH    = os.path.join(BASE, "vocabulary.json")


with open(VOCAB_PATH) as f:
    VOCAB = json.load(f)

VALID_INCIDENT_TYPES = set(VOCAB["incident_types"])
VALID_SCHEMA_FIELDS = {
    "category", "loss_datetime", "loss_location", "vehicle", "drivable",
    "vehicle_towed", "airbags_deployed", "injury_reported", "injury_details",
    "third_party_involved", "third_party_vehicle_id", "third_party_driver_name",
    "third_party_contact", "third_party_insurer", "hit_and_run",
    "police_report_filed", "fir_number", "police_station", "witnesses_present",
    "witness_contact", "evidence_photos_available", "evidence_video_available",
    "dashcam_available", "damage_areas", "damage_severity", "impact_direction",
    "speed_estimate", "vehicle_moving_status", "weather_condition", "road_condition",
    "signal_compliance", "lane_action", "policy_active", "policy_number",
    "driver_is_owner", "driver_name", "driver_license_valid", "driver_relationship",
    "vehicle_usage_type", "coverage_type", "add_ons", "settlement_preference",
    "repair_preference", "workshop_name", "towing_required", "previous_claims",
    "theft_keys_available", "theft_forced_entry", "theft_tracking_device",
    "fire_source", "fire_brigade_called", "flood_water_level", "flood_engine_cranked",
    "vandalism_type", "already_extracted_categories", "answered_question_ids",
}

REQUIRED_KEYS = {"id", "text", "question_field", "priority", "triggers", "targets"}
REQUIRED_TRIGGER_KEYS = {"incident_type"}

MIN_CATEGORY_COUNT = 30
NEAR_DUP_THRESHOLD = 0.85

def text_fingerprint(text: str) -> str:
    return hashlib.md5(text.strip().lower().encode()).hexdigest()

def trigrams(text: str):
    s = text.strip().lower()
    return set(s[i:i+3] for i in range(len(s)-2))

def jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)

def is_near_dup(text_a: str, text_b: str) -> bool:
    tg_a = trigrams(text_a)
    tg_b = trigrams(text_b)
    return jaccard(tg_a, tg_b) >= NEAR_DUP_THRESHOLD

def load_jsonl(path: str) -> List[dict]:
    qs = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                qs.append(json.loads(line))
    return qs

def write_jsonl(questions: List[dict], path: str):
    with open(path, "w", encoding="utf-8") as f:
        for q in questions:
            f.write(json.dumps(q, ensure_ascii=False) + "\n")





def pass_a_schema(questions: List[dict]) -> Tuple[List[dict], List[dict]]:
    valid, rejected = [], []
    seen_ids = set()

    for q in questions:
        reasons = []


        missing = REQUIRED_KEYS - set(q.keys())
        if missing:
            reasons.append(f"missing_keys:{sorted(missing)}")


        qid = q.get("id", "")
        if qid in seen_ids:
            reasons.append(f"duplicate_id:{qid}")
        else:
            seen_ids.add(qid)


        text = q.get("text", "")
        if not isinstance(text, str) or len(text.strip()) < 10:
            reasons.append("text_too_short_or_invalid")


        priority = q.get("priority")
        if not isinstance(priority, int) or not (1 <= priority <= 5):
            reasons.append(f"invalid_priority:{priority}")


        triggers = q.get("triggers", {})
        if not isinstance(triggers, dict):
            reasons.append("triggers_not_dict")
        else:
            it = triggers.get("incident_type", [])
            if not isinstance(it, list) or len(it) == 0:
                reasons.append("triggers.incident_type_missing_or_empty")
            else:
                bad_it = [x for x in it if x not in VALID_INCIDENT_TYPES]
                if bad_it:
                    reasons.append(f"unknown_incident_types:{bad_it}")


        targets = q.get("targets", {})
        if not isinstance(targets, dict) or "fill_fields" not in targets:
            reasons.append("targets.fill_fields_missing")
        else:
            ff = targets.get("fill_fields", [])
            if not isinstance(ff, list) or len(ff) == 0:
                reasons.append("fill_fields_empty")

        if reasons:
            q["rejection_reason"] = "; ".join(reasons)
            rejected.append(q)
        else:
            valid.append(q)

    return valid, rejected





def pass_b_logic(questions: List[dict]) -> Tuple[List[dict], List[dict]]:
    valid, rejected = [], []

    for q in questions:
        reasons = []
        triggers = q.get("triggers", {})
        targets = q.get("targets", {})
        fill_fields = targets.get("fill_fields", [])
        qfield = q.get("question_field", "")
        req_present = triggers.get("required_fields_present", [])


        if qfield in req_present:
            reasons.append(f"circular_dependency:{qfield}_in_required_fields_present")



        for ff in fill_fields:
            if ff in req_present:
                reasons.append(f"fill_field_also_required_present:{ff}")


        incident_types_in_trigger = triggers.get("incident_type", [])
        is_theft_only = set(incident_types_in_trigger) <= {"theft", "theft_attempted"}
        is_collision_only = set(incident_types_in_trigger) <= {
            "collision", "hit_and_run", "self_accident", "rollover",
            "collision_wall", "collision_animal"
        }

        if "flood_engine_cranked" in fill_fields and is_collision_only:
            reasons.append("flood_field_used_for_collision_only_trigger")

        if "theft_keys_available" in fill_fields and is_collision_only:
            reasons.append("theft_field_used_for_non_theft_incident")


        text = q.get("text", "")
        if not text.endswith("?") and not any(
            text.lower().startswith(w) for w in
            ["select", "describe", "list", "confirm", "provide", "walk", "tell"]
        ):
            reasons.append("text_not_a_question_form")


        if q.get("priority") == 1 and not incident_types_in_trigger:
            reasons.append("priority1_without_incident_type_trigger")

        if reasons:
            q["rejection_reason"] = "; ".join(reasons)
            rejected.append(q)
        else:
            valid.append(q)

    return valid, rejected





def pass_c_dedup(questions: List[dict]) -> Tuple[List[dict], List[dict]]:
    valid, rejected = [], []
    seen_hashes: Dict[str, str] = {}
    kept_texts: List[Tuple[str, str]] = []

    for q in questions:
        text = q["text"].strip()
        fp = text_fingerprint(text)


        if fp in seen_hashes:
            q["rejection_reason"] = f"exact_duplicate_of:{seen_hashes[fp]}"
            rejected.append(q)
            continue


        near_dup_of = None
        for kept_text, kept_id in kept_texts:
            if is_near_dup(text, kept_text):
                near_dup_of = kept_id
                break

        if near_dup_of:
            q["rejection_reason"] = f"near_duplicate_of:{near_dup_of}"
            rejected.append(q)
        else:
            seen_hashes[fp] = q["id"]
            kept_texts.append((text, q["id"]))
            valid.append(q)

    return valid, rejected

def pass_d_coverage(questions: List[dict]) -> dict:
    cats = Counter(q.get("category_tag", "unknown") for q in questions)
    priorities = Counter(q.get("priority") for q in questions)
    incident_coverage = defaultdict(int)
    for q in questions:
        for it in q.get("triggers", {}).get("incident_type", []):
            incident_coverage[it] += 1

    coverage_warnings = []
    for cat, count in cats.items():
        if count < MIN_CATEGORY_COUNT:
            coverage_warnings.append(f"LOW_COVERAGE: {cat} has only {count} questions (min {MIN_CATEGORY_COUNT})")


    p1_count = priorities.get(1, 0)
    if p1_count < 10:
        coverage_warnings.append(f"LOW_RED_FLAGS: only {p1_count} priority-1 questions")

    return {
        "category_counts": dict(sorted(cats.items())),
        "priority_counts": {str(k): v for k, v in sorted(priorities.items())},
        "incident_type_coverage": dict(sorted(incident_coverage.items())),
        "warnings": coverage_warnings,
    }

def run():
    print("=" * 60)
    print("VALIDATION PIPELINE")
    print("=" * 60)


    raw = load_jsonl(RAW_PATH)
    print(f"\nLoaded {len(raw)} raw questions from {RAW_PATH}")

    all_rejected = []


    print("\n--- Pass A: Schema Validation ---")
    valid_a, rej_a = pass_a_schema(raw)
    all_rejected.extend(rej_a)
    print(f"  Passed: {len(valid_a)}  |  Rejected: {len(rej_a)}")
    if rej_a:
        for q in rej_a[:3]:
            print(f"    [{q['id']}] {q.get('rejection_reason','')[:80]}")


    print("\n--- Pass B: Logic Validation ---")
    valid_b, rej_b = pass_b_logic(valid_a)
    all_rejected.extend(rej_b)
    print(f"  Passed: {len(valid_b)}  |  Rejected: {len(rej_b)}")
    if rej_b:
        for q in rej_b[:3]:
            print(f"    [{q['id']}] {q.get('rejection_reason','')[:80]}")


    print("\n--- Pass C: Deduplication ---")
    valid_c, rej_c = pass_c_dedup(valid_b)
    all_rejected.extend(rej_c)
    print(f"  Passed: {len(valid_c)}  |  Rejected: {len(rej_c)}")
    exact = sum(1 for q in rej_c if "exact_duplicate" in q.get("rejection_reason",""))
    near  = sum(1 for q in rej_c if "near_duplicate" in q.get("rejection_reason",""))
    print(f"    Exact duplicates: {exact}  |  Near-duplicates: {near}")


    print("\n--- Pass D: Coverage Check ---")
    coverage = pass_d_coverage(valid_c)
    for w in coverage["warnings"]:
        print(f"  WARNING: {w}")
    if not coverage["warnings"]:
        print("  All categories meet minimum coverage. ✓")

    print(f"\nCategory counts:")
    for cat, count in coverage["category_counts"].items():
        bar = "█" * (count // 5)
        print(f"  {cat:<35} {count:>4}  {bar}")

    print(f"\nPriority distribution:")
    for p, count in coverage["priority_counts"].items():
        print(f"  Priority {p}: {count}")


    write_jsonl(valid_c, VALID_PATH)
    write_jsonl(all_rejected, REJECT_PATH)

    report = {
        "summary": {
            "raw_count": len(raw),
            "valid_count": len(valid_c),
            "rejected_count": len(all_rejected),
            "pass_a_rejected": len(rej_a),
            "pass_b_rejected": len(rej_b),
            "pass_c_rejected": len(rej_c),
        },
        "coverage": coverage,
        "rejection_breakdown": {
            "schema_errors": len(rej_a),
            "logic_errors": len(rej_b),
            "exact_duplicates": exact,
            "near_duplicates": near,
        }
    }
    with open(REPORT_PATH, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n{'='*60}")
    print(f"FINAL: {len(valid_c)} valid questions  |  {len(all_rejected)} rejected")
    print(f"Outputs written to data/")
    print(f"  → question_bank_validated.jsonl")
    print(f"  → rejected_questions.jsonl")
    print(f"  → validation_report.json")

if __name__ == "__main__":
    run()
