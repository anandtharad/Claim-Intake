from typing import List, Dict, Tuple

REQUIRED_FIELDS_BY_INCIDENT: Dict[str, List[str]] = {
    "collision": [
        "loss_datetime", "loss_location", "vehicle",
        "third_party_involved", "police_report_filed",
        "drivable", "damage_severity",
    ],
    "collision_wall": [
        "loss_datetime", "loss_location",
        "drivable", "damage_severity", "impact_direction",
    ],
    "collision_animal": [
        "loss_datetime", "loss_location",
        "drivable", "damage_severity",
    ],
    "hit_and_run": [
        "loss_datetime", "loss_location",
        "police_report_filed", "drivable", "damage_severity",
    ],
    "theft": [
        "loss_datetime", "loss_location",
        "police_report_filed", "theft_keys_available",
    ],
    "theft_attempted": [
        "loss_datetime", "loss_location",
        "police_report_filed", "theft_forced_entry",
    ],
    "fire": [
        "loss_datetime", "loss_location",
        "fire_source", "fire_brigade_called", "damage_severity",
    ],
    "flood": [
        "loss_datetime", "loss_location",
        "flood_water_level", "flood_engine_cranked", "drivable",
    ],
    "vandalism": [
        "loss_datetime", "loss_location",
        "vandalism_type", "damage_severity", "police_report_filed",
    ],
    "natural_disaster": [
        "loss_datetime", "loss_location", "damage_severity",
    ],
    "self_accident": [
        "loss_datetime", "loss_location",
        "drivable", "damage_severity", "impact_direction",
    ],
    "rollover": [
        "loss_datetime", "loss_location",
        "injury_reported", "drivable", "damage_severity",
    ],
}

MAX_TURNS = 20
LOW_VALUE_PRIORITY_THRESHOLD = 4
LOW_VALUE_WINDOW = 3

def _field_is_filled(state: dict, field: str) -> bool:
    """Check if a field has a non-null, meaningful value."""
    val = state.get(field)
    if val is None:
        return False
    if isinstance(val, bool):
        return True
    if isinstance(val, str):
        return val.strip().upper() not in ("", "NA", "NULL", "NONE", "UNKNOWN")
    if isinstance(val, int):
        return True
    if isinstance(val, list):
        return len(val) > 0
    if isinstance(val, dict):
        return any(v is not None for v in val.values())
    return False

def _core_fields_complete(state: dict) -> Tuple[bool, str]:
    """Check if all required core fields for the active incident type are filled."""
    category = state.get("category")
    if not category:
        return False, "incident_type_unknown"

    required = REQUIRED_FIELDS_BY_INCIDENT.get(category, [])
    if not required:
        return False, f"no_required_fields_defined_for_{category}"

    missing = [f for f in required if not _field_is_filled(state, f)]
    if not missing:
        return True, f"core_fields_complete_for_{category}"
    return False, f"missing_core_fields:{missing}"

def _only_low_priority_remaining(history: List[dict]) -> Tuple[bool, str]:
    """
    Check if the last LOW_VALUE_WINDOW questions all had low priority.
    """
    if len(history) < LOW_VALUE_WINDOW:
        return False, "not_enough_history"
    recent = history[-LOW_VALUE_WINDOW:]
    priorities = [h.get("question_priority", 3) for h in recent]
    if all(p >= LOW_VALUE_PRIORITY_THRESHOLD for p in priorities):
        return True, f"last_{LOW_VALUE_WINDOW}_questions_all_low_priority>=_{LOW_VALUE_PRIORITY_THRESHOLD}"
    return False, "high_priority_questions_remain"

def _no_eligible_questions(pool_size: int) -> Tuple[bool, str]:
    """Check if the retrieval engine returned no candidates."""
    if pool_size == 0:
        return True, "no_eligible_questions_remaining"
    return False, "questions_remain"

def _max_turns_reached(state: dict) -> Tuple[bool, str]:
    """Check if maximum turns have been exhausted."""
    n = len(state.get("answered_question_ids", []))
    if n >= MAX_TURNS:
        return True, f"max_turns_reached:{n}>={MAX_TURNS}"
    return False, f"turns_so_far:{n}"

def _user_requested_termination(user_text: str) -> Tuple[bool, str]:
    """Detect if the user explicitly wants to end the session."""
    if not user_text:
        return False, "no_termination_signal"
    TERMINATION_PHRASES = [
        "done", "that's all", "submit", "finish", "end",
        "no more questions", "stop", "complete", "exit",
        "i'm done", "that is all", "nothing more", "that's it"
    ]
    text_l = user_text.lower().strip()
    for phrase in TERMINATION_PHRASES:
        if text_l == phrase or text_l.startswith(phrase + " ") or text_l.endswith(" " + phrase):
            return True, f"user_requested_termination:'{phrase}'"
    return False, "no_termination_signal"

def should_terminate(
    state: dict,
    history: List[dict],
    pool_size: int = 1,
    user_text: str = ""
) -> Dict:
    """
    Evaluate whether the interview should terminate.

    Args:
        state:      Current claim state
        history:    List of turn dicts, each with at least {"question_priority": int}
        pool_size:  Number of candidates from last retrieval (0 = exhausted)
        user_text:  Raw user input this turn (for explicit termination detection)

    Returns:
        {"terminate": bool, "reason": str, "checks": dict}
    """
    checks = {}

    user_done, user_reason = _user_requested_termination(user_text)
    checks["user_requested"] = user_reason
    if user_done:
        return {"terminate": True, "reason": user_reason, "checks": checks}

    no_qs, no_qs_reason = _no_eligible_questions(pool_size)
    checks["no_eligible_questions"] = no_qs_reason
    if no_qs:
        return {"terminate": True, "reason": no_qs_reason, "checks": checks}

    max_done, max_reason = _max_turns_reached(state)
    checks["max_turns"] = max_reason
    if max_done:
        return {"terminate": True, "reason": max_reason, "checks": checks}

    core_done, core_reason = _core_fields_complete(state)
    checks["core_fields"] = core_reason
    if core_done:
        return {"terminate": True, "reason": core_reason, "checks": checks}

    low_val, low_reason = _only_low_priority_remaining(history)
    checks["low_priority"] = low_reason
    if low_val:
        return {"terminate": True, "reason": low_reason, "checks": checks}

    return {"terminate": False, "reason": "continue_interview", "checks": checks}

if __name__ == "__main__":

    full_state = {
        "category": "collision",
        "loss_datetime": "Feb 3rd 2026",
        "loss_location": {"city": "Pune", "road_type": "urban"},
        "vehicle": {"make": "Maruti", "model": "Baleno", "year": 2021},
        "third_party_involved": True,
        "police_report_filed": False,
        "drivable": True,
        "damage_severity": "minor",
        "answered_question_ids": ["Q0001", "Q0002"],
        "already_extracted_categories": [],
    }
    result = should_terminate(full_state, [{"question_priority": 3}], pool_size=50)
    print("Test 1 (core complete):", result)

    partial_state = {
        "category": "collision",
        "loss_datetime": "Feb 3rd 2026",
        "loss_location": {"city": "Pune", "road_type": "urban"},
        "answered_question_ids": ["Q0001"],
        "already_extracted_categories": [],
    }
    history = [{"question_priority": 5}, {"question_priority": 4}, {"question_priority": 5}]
    result2 = should_terminate(partial_state, history, pool_size=20)
    print("Test 2 (low priority):", result2)

    result3 = should_terminate(partial_state, [], pool_size=10, user_text="done")
    print("Test 3 (user done):", result3)

    many_answered = {"category": "collision", "answered_question_ids": [f"Q{i:04d}" for i in range(20)],
                     "already_extracted_categories": []}
    result4 = should_terminate(many_answered, [], pool_size=10)
    print("Test 4 (max turns):", result4)
