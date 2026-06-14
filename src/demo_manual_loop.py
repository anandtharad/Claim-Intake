"""
demo_manual_loop.py
-------------------
Multi-turn vehicle insurance claim intake CLI.

Usage:
    python src/demo_manual_loop.py                  # interactive
    python src/demo_manual_loop.py --auto           # scripted collision demo
    python src/demo_manual_loop.py --auto-fire      # scripted fire demo
    python src/demo_manual_loop.py --auto-theft     # scripted theft demo
"""

import json
import os
import sys
import argparse
from copy import deepcopy
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from state_extractor import extract_delta, apply_delta
from retriever import load_question_bank, get_next_question
from terminator import should_terminate

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNS_DIR = os.path.join(BASE_DIR, "sample_runs")
os.makedirs(RUNS_DIR, exist_ok=True)

EMPTY_STATE = {
    "category": None,
    "loss_datetime": None,
    "loss_location": {"city": None, "road_type": None},
    "vehicle": {"make": None, "model": None, "year": None},
    "drivable": None,
    "vehicle_towed": None,
    "airbags_deployed": None,
    "injury_reported": None,
    "third_party_involved": None,
    "third_party_vehicle_id": None,
    "third_party_driver_name": None,
    "third_party_contact": None,
    "third_party_insurer": None,
    "hit_and_run": None,
    "police_report_filed": None,
    "fir_number": None,
    "police_station": None,
    "witnesses_present": None,
    "evidence_photos_available": None,
    "evidence_video_available": None,
    "dashcam_available": None,
    "damage_areas": None,
    "vehicle_registration": None,
    "damage_severity": None,
    "impact_direction": None,
    "speed_estimate": None,
    "vehicle_moving_status": None,
    "weather_condition": None,
    "road_condition": None,
    "signal_compliance": None,
    "lane_action": None,
    "policy_active": None,
    "policy_number": None,
    "driver_is_owner": None,
    "driver_license_valid": None,
    "vehicle_usage_type": None,
    "coverage_type": None,
    "add_ons": None,
    "settlement_preference": None,
    "repair_preference": None,
    "towing_required": None,
    "previous_claims": None,
    "theft_keys_available": None,
    "theft_forced_entry": None,
    "theft_tracking_device": None,
    "fire_source": None,
    "fire_brigade_called": None,
    "flood_water_level": None,
    "flood_engine_cranked": None,
    "vandalism_type": None,
    "already_extracted_categories": [],
    "answered_question_ids": [],
}

def _divider(char="─", width=64):
    print(char * width)

def _print_question(result: dict, turn: int):
    _divider()
    print(f"  TURN {turn} | Question {result['question_id']}")
    _divider()
    print(f"  {result['question_text']}")
    print()
    print(f"  Field   : {result['question_field']}")
    print(f"  Trigger : {result['trigger']}")
    sb = result['score_breakdown']
    print(f"  Scores  : priority={sb['priority']:.2f}  relevance={sb['relevance']:.2f}  "
          f"gap_fill={sb['gap_fill']:.2f}  composite={sb['composite']:.2f}")
    print(f"  Pool    : {result['audit']['hard_filter_pool_size']} candidates "
          f"({result['audit']['total_suppressed']} suppressed)")
    _divider()

def _print_state_diff(old_state: dict, delta: dict, corrections: list):
    changed = []
    for k, v in delta.items():
        if v is not None and old_state.get(k) != v:
            changed.append(f"    + {k}: {old_state.get(k)!r} → {v!r}")
    for c in corrections:
        changed.append(f"    - {c}: RETRACTED")
    if changed:
        print("  State changes this turn:")
        for line in changed:
            print(line)
    else:
        print("  (No new fields extracted this turn)")

def _print_summary(state: dict):
    print("  Final claim state:")
    skip = {"already_extracted_categories", "answered_question_ids"}
    for k, v in state.items():
        if k in skip or v is None:
            continue
        if isinstance(v, dict) and all(vv is None for vv in v.values()):
            continue
        print(f"    {k}: {v}")
    print(f"  Extracted categories : {state.get('already_extracted_categories', [])}")
    print(f"  Answered QIDs        : {state.get('answered_question_ids', [])}")

def save_turn_log(turn, user_input, delta, corrections,
                  state_before, state_after, retrieval, termination):
    log = {
        "turn": turn,
        "timestamp": datetime.now().isoformat(),
        "user_input": user_input,
        "extracted_delta": {k: v for k, v in delta.items() if v is not None},
        "corrections": corrections,
        "state_before": state_before,
        "state_after": state_after,
        "retrieval_output": retrieval or {},
        "termination_check": termination,
    }
    path = os.path.join(RUNS_DIR, f"Turn_{turn:02d}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)

def run_loop(question_bank, auto_inputs=None):
    state = deepcopy(EMPTY_STATE)
    history = []
    turn = 0
    auto_idx = 0

    print()
    _divider("═")
    print("  VEHICLE INSURANCE CLAIM INTAKE SYSTEM")
    print("  Dynamic Follow-up Question Generator")
    _divider("═")
    print()
    print("  Please describe what happened to your vehicle.")
    print("  Type 'done' or 'exit' to finish.")
    print()

    while True:
        if auto_inputs is not None:
            if auto_idx >= len(auto_inputs):
                break
            user_input = auto_inputs[auto_idx]
            auto_idx += 1
            print(f"  > {user_input}")
        else:
            try:
                user_input = input("  > ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n  Session ended.")
                break

        if not user_input:
            continue

        turn += 1
        state_before = deepcopy(state)

        last_qid = history[-1]["question_id"] if history else None
        last_qfield = history[-1]["question_field"] if history else None
        delta, corrections = extract_delta(user_input, state, context_field=last_qfield)
        state = apply_delta(state, delta, corrections, answered_qid=last_qid)

        print()
        _print_state_diff(state_before, delta, corrections)
        print()

        retrieval = get_next_question(state, question_bank)
        pool_size = retrieval["audit"]["hard_filter_pool_size"] if retrieval else 0
        termination = should_terminate(state, history, pool_size=pool_size, user_text=user_input)

        if termination["terminate"]:
            _divider("═")
            print("  ✅  INTAKE COMPLETE")
            print(f"  Reason : {termination['reason']}")
            _divider("═")
            print()
            _print_summary(state)
            save_turn_log(turn, user_input, delta, corrections,
                          state_before, state, retrieval or {}, termination)
            print(f"\n  Turn logs saved to sample_runs/")
            break

        if retrieval is None:
            print("  ⚠  No more questions available.")
            break

        _print_question(retrieval, turn)

        q_in_bank = next((q for q in question_bank if q["id"] == retrieval["question_id"]), {})
        history.append({
            "turn": turn,
            "question_id": retrieval["question_id"],
            "question_field": retrieval["question_field"],
            "question_priority": q_in_bank.get("priority", 3),
            "score": retrieval["score_breakdown"]["composite"],
        })

        save_turn_log(turn, user_input, delta, corrections,
                      state_before, state, retrieval, termination)

    print("\n  Thank you. Your claim intake has been recorded.")
    return state

AUTO_SCRIPT = [

    "I was driving on the expressway near Nagpur last Sunday around 9pm in heavy rain when a truck hit me from behind really hard",

    "No, I wasn't injured thank god, but the airbags went off on impact",

    "actually they did stop, it wasn't a hit and run, we exchanged details at the spot",

    "yes we called the police. FIR 112/2026 was filed at Nagpur Civil Lines station",

    "the rear bumper and left quarter panel are completely smashed, car can't be driven",
    "done",
]

AUTO_SCRIPT_FIRE = [

    "My Maruti Alto 800 caught fire this morning around 8am on the Pune-Mumbai expressway",

    "think the LPG kit was leaking and it just blew up, the whole front is burnt",

    "yes called them immediately, fire brigade arrived in about 10 minutes",

    "car is totally gutted, nothing salvageable. I jumped out in time so no injuries",

    "filed a police report at the local station, FIR number is 89/2026",
    "done",
]

AUTO_SCRIPT_THEFT = [

    "My Honda City KA05MN7890 was stolen last Tuesday night from my apartment parking in Whitefield Bangalore",

    "I have both sets of keys with me. The car also had a GPS tracker installed",

    "windows were all intact, no signs of forced entry, no idea how they got in",

    "yes reported it this morning at HSR Layout police station, FIR number 234/2026",
    "done",
]

AUTO_SCRIPT_FLOOD = [

    "My car got submerged in the floods near Hyderabad last week during the heavy rains",

    "the water was up to the dashboard level, almost chest height from outside",

    "yes I tried starting it after the water receded but engine wouldn't crank at all",

    "interior is completely damaged, engine is gone for sure, total write-off I think",

    "I didn't file any FIR, just filed a complaint with the municipality",
    "done",
]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Vehicle Insurance Claim Intake Demo")
    parser.add_argument("--auto",       action="store_true", help="Collision: rain, correction, FIR")
    parser.add_argument("--auto-fire",  action="store_true", help="Fire: LPG, yes/no brigade, total loss")
    parser.add_argument("--auto-theft", action="store_true", help="Theft: parallel fusion, keys, tracker")
    parser.add_argument("--auto-flood", action="store_true", help="Flood: water level, engine crank, no FIR")
    parser.add_argument("--bank",       default=None,        help="Path to question bank JSONL")
    args = parser.parse_args()

    print("Loading question bank...")
    bank_path = args.bank or os.path.join(BASE_DIR, "data", "question_bank_validated.jsonl")
    bank = load_question_bank(bank_path)
    from retriever import RELEVANCE_BACKEND
    print(f"Loaded {len(bank)} validated questions.")
    print(f"Relevance backend : {RELEVANCE_BACKEND.upper()}\n")

    if args.auto:
        run_loop(bank, auto_inputs=AUTO_SCRIPT)
    elif args.auto_fire:
        run_loop(bank, auto_inputs=AUTO_SCRIPT_FIRE)
    elif args.auto_theft:
        run_loop(bank, auto_inputs=AUTO_SCRIPT_THEFT)
    elif args.auto_flood:
        run_loop(bank, auto_inputs=AUTO_SCRIPT_FLOOD)
    else:
        run_loop(bank)
