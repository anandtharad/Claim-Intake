import re
import json
import os
from typing import Dict, Any, List, Tuple, Optional
from copy import deepcopy
from datetime import datetime


try:
    import spacy
    _nlp = spacy.load("en_core_web_sm")
    SPACY_AVAILABLE = True
except Exception:
    SPACY_AVAILABLE = False
    _nlp = None


try:
    import dateparser
    DATEPARSER_AVAILABLE = True
except ImportError:
    DATEPARSER_AVAILABLE = False


_VOCAB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "vocabulary.json")
with open(_VOCAB_PATH) as f:
    VOCAB = json.load(f)

VEHICLE_MAKES = [m.lower() for m in VOCAB["vehicle_makes"]]





NEGATION_WORDS = {"no", "not", "never", "none", "didn't", "did not", "wasn't",
                  "was not", "don't", "do not", "cannot", "can't", "without",
                  "neither", "nor", "nothing", "nowhere", "nobody", "actually",
                  "incorrect", "wrong", "mistake", "correction", "retract"}

def _has_negation(text, keyword):
    words = text.lower().split()
    for i, w in enumerate(words):
        if keyword.lower() in w:
            window = words[max(0, i-5):i]
            if any(neg in " ".join(window) for neg in NEGATION_WORDS):
                return True
    return False

def _negated(text, pattern):
    m = re.search(pattern, text, re.IGNORECASE)
    if not m:
        return False
    start = m.start()
    prefix = text[max(0, start-40):start].lower()
    return any(neg in prefix for neg in NEGATION_WORDS)





INCIDENT_KEYWORDS = {
    "collision":        ["collision", "collided", "hit", "accident", "crash", "crashed",
                         "smash", "smashed", "ram", "rammed", "fender", "bumper hit",
                         "side impact", "rear end", "head.on", "t-bone"],
    "collision_wall":   ["wall", "pillar", "pole", "post", "barrier", "divider",
                         "median", "fence", "railing", "gate", "bollard"],
    "collision_animal": ["animal", "dog", "cow", "deer", "goat", "buffalo",
                         "stray", "wildlife", "creature"],
    "hit_and_run":      ["hit and run", "hit-and-run", "fled", "fled the scene",
                         "drove away", "ran away", "number plate partial",
                         "did not stop", "escaped"],
    "theft":            ["stolen", "theft", "thief", "stole", "missing vehicle",
                         "vehicle gone", "car gone", "bike stolen", "car stolen"],
    "theft_attempted":  ["attempted theft", "tried to steal", "break-in attempt",
                         "tried to break", "theft attempt"],
    "fire":             ["fire", "burnt", "burning", "flame", "caught fire",
                         "on fire", "blaze", "combustion", "engulfed"],
    "flood":            ["flood", "flooded", "submerged", "waterlogged",
                         "water level", "inundated", "storm drain", "water entered"],
    "vandalism":        ["vandal", "vandalism", "scratched", "keyed", "tyre slashed",
                         "graffiti", "spray paint", "window broken", "damage intentional",
                         "deliberate", "tampered"],
    "natural_disaster": ["earthquake", "cyclone", "storm", "hail", "hailstorm",
                         "tornado", "landslide", "tree fell", "fallen tree",
                         "lightning", "natural", "calamity", "disaster"],
    "self_accident":    ["self accident", "lost control", "skidded", "swerved",
                         "went off road", "hit a pothole", "brake fail"],
    "rollover":         ["rollover", "rolled over", "flipped", "overturned",
                         "toppled", "capsized", "inverted"],
}

def extract_incident_type(text):
    text_l = text.lower()
    scores = {}
    for inc_type, keywords in INCIDENT_KEYWORDS.items():
        score = 0
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', text_l):
                score += 2
            elif kw in text_l:
                score += 1
        if score > 0:
            scores[inc_type] = score
    if not scores:
        return None
    SUBTYPE_PRIORITY = {
        "hit_and_run": 10, "collision_animal": 9, "collision_wall": 8,
        "rollover": 7, "theft_attempted": 6, "theft": 5,
        "fire": 4, "flood": 4, "vandalism": 4, "natural_disaster": 4,
        "self_accident": 3, "collision": 1,
    }
    top_score = max(scores.values())
    top_candidates = [k for k, v in scores.items() if v == top_score]
    best = max(top_candidates, key=lambda k: SUBTYPE_PRIORITY.get(k, 0))
    return best





DATE_PATTERNS = [
    r'\b(\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)[,\s]+\d{4})\b',
    r'\b((?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2}(?:st|nd|rd|th)?[,\s]+\d{4})\b',
    r'\b((?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2}(?:st|nd|rd|th)?)\b',
    r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b',
    r'\b(\d{4}-\d{2}-\d{2})\b',
]
RELATIVE_DATE_PATTERNS = {
    "today": "today", "yesterday": "yesterday",
    "day before yesterday": "day before yesterday",
    "last night": "last night", "this morning": "this morning",
    "this evening": "this evening", "last monday": "last monday",
    "last tuesday": "last tuesday", "last wednesday": "last wednesday",
    "last thursday": "last thursday", "last friday": "last friday",
    "last saturday": "last saturday", "last sunday": "last sunday",
}

def extract_datetime(text):
    text_l = text.lower()
    for phrase, label in RELATIVE_DATE_PATTERNS.items():
        if phrase in text_l:
            if DATEPARSER_AVAILABLE:
                try:
                    parsed = dateparser.parse(phrase)
                    if parsed:
                        return parsed.strftime("%B %d, %Y")
                except Exception:
                    pass
            return label.title()
    for pattern in DATE_PATTERNS:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            raw = m.group(1)
            if DATEPARSER_AVAILABLE:
                try:
                    parsed = dateparser.parse(raw)
                    if parsed:
                        return parsed.strftime("%B %d, %Y")
                except Exception:
                    pass
            return raw
    if SPACY_AVAILABLE and _nlp:
        doc = _nlp(text)
        for ent in doc.ents:
            if ent.label_ == "DATE":
                if DATEPARSER_AVAILABLE:
                    try:
                        parsed = dateparser.parse(ent.text)
                        if parsed:
                            return parsed.strftime("%B %d, %Y")
                    except Exception:
                        pass
                return ent.text
    return None





ROAD_TYPE_KEYWORDS = {
    "highway":    ["highway", "nh ", "sh ", "national highway", "state highway", "expressway", "freeway"],
    "urban":      ["urban", "city road", "city street", "main road", "market road", "city centre", "town"],
    "rural":      ["rural", "village", "village road", "countryside", "outskirts"],
    "parking_lot":["parking lot", "parking area", "car park", "multi-storey", "basement parking", "mall parking"],
    "flyover":    ["flyover", "overpass", "bridge", "elevated road"],
    "private_road":["private road", "gated community", "colony road", "society road", "campus"],
}

KNOWN_CITIES = [
    "mumbai", "delhi", "pune", "bangalore", "bengaluru", "hyderabad", "chennai",
    "kolkata", "ahmedabad", "surat", "jaipur", "lucknow", "kanpur", "nagpur",
    "indore", "bhopal", "visakhapatnam", "patiala", "ludhiana", "agra",
    "nashik", "vadodara", "thane", "patna", "coimbatore", "kochi",
    "chandigarh", "gurgaon", "noida", "faridabad", "ghaziabad", "meerut",
    "wakad", "hinjewadi", "bandra", "andheri", "powai", "navi mumbai",
    "whitefield", "hsr layout", "indiranagar",
]

def extract_location(text):
    result = {"city": None, "road_type": None}
    text_l = text.lower()
    for rtype, keywords in ROAD_TYPE_KEYWORDS.items():
        if any(kw in text_l for kw in keywords):
            result["road_type"] = rtype
            break
    for city in KNOWN_CITIES:
        if city in text_l:
            result["city"] = city.title()
            break
    if SPACY_AVAILABLE and _nlp and not result["city"]:
        doc = _nlp(text)
        for ent in doc.ents:
            if ent.label_ in ("GPE", "LOC") and len(ent.text) > 2:
                result["city"] = ent.text
                break
    return result





YEAR_PATTERN = re.compile(r'\b(19[89]\d|20[0-2]\d)\b')
REG_PATTERN  = re.compile(r'\b([A-Z]{2}\s?\d{2}\s?[A-Z]{1,3}\s?\d{4})\b', re.IGNORECASE)

VEHICLE_MODEL_MAP = {
    "maruti":   ["baleno", "swift", "dzire", "wagon r", "vitara", "ertiga", "ciaz", "alto", "brezza", "s-cross", "celerio"],
    "hyundai":  ["creta", "verna", "i20", "i10", "venue", "tucson", "elantra", "santro", "grand i10", "alcazar"],
    "tata":     ["nexon", "harrier", "safari", "altroz", "tiago", "punch", "tigor", "hexa", "zest"],
    "honda":    ["city", "amaze", "jazz", "wr-v", "cr-v", "accord", "civic", "br-v"],
    "toyota":   ["innova", "fortuner", "glanza", "urban cruiser", "camry", "etios", "corolla", "hilux"],
    "mahindra": ["scorpio", "thar", "xuv700", "xuv300", "bolero", "marazzo", "kuv100"],
    "kia":      ["seltos", "sonet", "carnival", "ev6"],
    "mg":       ["hector", "astor", "gloster", "zs", "comet"],
}

def extract_vehicle(text):
    result = {"make": None, "model": None, "year": None}
    text_l = text.lower()
    year_m = YEAR_PATTERN.search(text)
    if year_m:
        result["year"] = int(year_m.group(1))
    for make, models in VEHICLE_MODEL_MAP.items():
        if make in text_l:
            result["make"] = make.title()
            for model in models:
                if model in text_l:
                    result["model"] = model.title()
                    break
            break
    if not result["make"]:
        for make in VEHICLE_MAKES:
            if make in text_l:
                result["make"] = make.title()
                break
    return result

def extract_registration(text):
    m = REG_PATTERN.search(text)
    if m:
        return m.group(1).upper().replace(" ", "")
    return None





def extract_drivable(text):
    text_l = text.lower()
    if any(p in text_l for p in [
        "not drivable", "cannot drive", "can't drive", "undrivable",
        "towed", "needs towing", "total loss", "not running", "immobile",
        "not moving", "won't start", "won't move"
    ]):
        return False
    if any(p in text_l for p in [
        "still drivable", "car is fine", "drivable", "i can drive",
        "was driving", "drove away", "drive it home", "running fine"
    ]):
        return True
    return None

def extract_third_party(text):
    text_l = text.lower()
    if any(p in text_l for p in [
        "no other vehicle", "no third party", "alone", "solo",
        "only my car", "just my vehicle", "hit a wall", "hit the wall",
        "hit a pole", "no one else", "no bike", "actually just a wall",
        "wasn't another vehicle", "was not another"
    ]):
        return False
    if any(p in text_l for p in [
        "other vehicle", "another vehicle", "third party", "other car",
        "another car", "motorcycle", "bike", "truck", "bus", "auto",
        "tempo", "lorry", "scooter", "two-wheeler", "cab", "taxi"
    ]):
        return True
    return None

def extract_police_report(text):
    text_l = text.lower()
    if any(p in text_l for p in [
        "no police", "did not call police", "not reported to police",
        "handled privately", "settled privately", "no fir",
        "without police", "didn't call", "no report filed", "no complaint"
    ]):
        return False
    if any(p in text_l for p in [
        "police report", "filed fir", "fir number", "police station",
        "called police", "registered fir", "police came",
        "police arrived", "reported to police", "lodged complaint"
    ]):
        return True
    return None

def extract_injury(text):
    text_l = text.lower()

    if any(p in text_l for p in [
        "no injury", "no one injured", "not injured", "nobody hurt",
        "no casualties", "everyone is fine", "no one was hurt",
        "wasn't injured", "was not injured", "weren't injured",
        "no one hurt", "i am fine", "i'm fine", "we are fine",
        "not hurt", "wasn't hurt", "was not hurt", "nobody injured",
        "jumped out in time", "i jumped out"
    ]):
        return False

    if any(p in text_l for p in [
        "injured", "hurt", "hospital", "ambulance", "fracture",
        "bleeding", "casualty", "casualties", "wound", "wounded",
        "medical", "doctor"
    ]):
        if not any(neg in text_l for neg in [
            "wasn't injured", "not injured", "was not injured",
            "not hurt", "wasn't hurt", "was not hurt"
        ]):
            return True
    return None

def extract_airbags(text):
    text_l = text.lower()
    if any(p in text_l for p in ["airbag deployed", "airbags deployed",
                                   "airbag activated", "airbags went off",
                                   "airbag came out"]):
        return True
    if any(p in text_l for p in ["airbag did not", "airbags did not",
                                   "no airbag", "airbags not deployed"]):
        return False
    return None

def extract_witnesses(text):
    text_l = text.lower()
    if any(p in text_l for p in ["witness", "bystander", "saw it happen",
                                   "people saw", "someone saw", "onlooker",
                                   "saw the accident", "saw what happened"]):
        if _has_negation(text_l, "witness") or "no witness" in text_l:
            return False
        return True
    if any(p in text_l for p in ["no witnesses", "nobody saw", "no one saw",
                                   "noone saw", "no bystander"]):
        return False
    if any(p in text_l for p in ["i don't think so", "i dont think so",
                                   "don't think anyone", "dont think anyone",
                                   "not that i know", "not sure if anyone saw"]):
        return False
    return None

def extract_photos(text):
    text_l = text.lower()
    if any(p in text_l for p in ["took photos", "photos taken", "photographs",
                                   "clicked pictures", "have photos", "have pictures",
                                   "video available", "dashcam", "cctv"]):
        return True
    if any(p in text_l for p in ["no photos", "didn't take photos", "no pictures",
                                   "no video", "no camera"]):
        return False
    return None

def extract_fir_number(text):
    patterns = [
        r'\bfir\b\s*(?:no\.?|number)?\s*(?:is\s+)?[:\-]?\s*([A-Z0-9][A-Z0-9\-/]{2,})',
        r'\bcase\b\s*(?:no\.?|number)?\s*(?:is\s+)?[:\-]?\s*([A-Z0-9][A-Z0-9\-/]{2,})',
        r'\b(\d{3,6}/\d{4})\b',
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            val = m.group(1).strip()
            if not any(c.isdigit() for c in val):
                continue
            if val.lower() not in ("filed", "number", "station", "report", "registered"):
                return val
    return None

def extract_impact_direction(text):
    text_l = text.lower().strip()
    if any(p in text_l for p in ["from the front", "head on", "head-on", "frontal",
                                   "front impact", "hit from front"]):
        return "front"
    if any(p in text_l for p in ["from behind", "rear end", "from the back", "back of",
                                   "rear impact", "hit from behind", "hit from the rear",
                                   "rear collision", "hit me from behind"]):
        return "rear"
    if any(p in text_l for p in ["from the left", "left side", "driver side",
                                   "driver's side", "hit from left"]):
        return "left_side"
    if any(p in text_l for p in ["from the right", "right side", "passenger side",
                                   "passenger's side", "hit from right"]):
        return "right_side"
    if any(p in text_l for p in ["rolled over", "rollover", "flipped", "overturned"]):
        return "rollover"
    if any(p in text_l for p in ["t-bone", "t bone", "side on", "side impact",
                                   "broadside", "from the side"]):
        return "side"
    _SINGLE = {
        "front": "front", "rear": "rear", "back": "rear", "side": "side",
        "left": "left_side", "right": "right_side", "rollover": "rollover",
    }
    tokens = text_l.rstrip(".!?").split()
    if len(tokens) <= 3:
        for tok in tokens:
            if tok in _SINGLE:
                return _SINGLE[tok]
    return None

def extract_damage_severity(text):
    text_l = text.lower()
    if any(p in text_l for p in ["total loss", "write off", "completely destroyed",
                                   "beyond repair", "scrap", "totally burnt",
                                   "completely burnt", "gutted", "burnt out"]):
        return "total_loss"
    if any(p in text_l for p in ["severe", "heavy damage", "major damage",
                                   "badly damaged", "serious damage",
                                   "heavily damaged", "extensive damage"]):
        return "severe"
    if any(p in text_l for p in ["moderate", "medium damage", "significant"]):
        return "moderate"
    if any(p in text_l for p in ["minor", "small dent", "scratch", "light damage",
                                   "minor damage", "slight"]):
        return "minor"
    return None

def extract_theft_specifics(text):
    result = {"theft_keys_available": None, "theft_forced_entry": None, "theft_tracking_device": None}
    text_l = text.lower()
    if "keys" in text_l or "key" in text_l:
        if any(p in text_l for p in [
                "did not leave", "didn't leave", "not leave",
                "keys with me", "have the keys", "have both keys",
                "both keys with me", "still have both keys",
                "both sets of keys", "keys at home", "keys on me",
                "key with me", "key is with me", "i have the key"]):
            result["theft_keys_available"] = False
        elif any(p in text_l for p in ["keys inside", "left keys", "key in car",
                                        "spare key", "keys were in", "key inside",
                                        "keys in the car", "key was in"]):
            result["theft_keys_available"] = True
    if any(p in text_l for p in ["no forced entry", "no damage to lock", "windows intact",
                                   "intact window", "no signs of forced"]):
        result["theft_forced_entry"] = False
    elif any(p in text_l for p in ["forced entry", "broken window", "smashed window",
                                    "tampered", "lock broken", "door forced"]):
        result["theft_forced_entry"] = True
    if any(p in text_l for p in ["gps", "tracking device", "tracker", "location device"]):
        result["theft_tracking_device"] = True
    elif any(p in text_l for p in ["no gps", "no tracker", "no tracking"]):
        result["theft_tracking_device"] = False
    return result

def extract_fire_specifics(text):
    result = {"fire_source": None, "fire_brigade_called": None}
    text_l = text.lower()
    if any(p in text_l for p in ["electrical fault", "short circuit", "wiring issue"]):
        result["fire_source"] = "electrical_fault"
    elif any(p in text_l for p in ["fuel leak", "petrol leak", "fuel pipe"]):
        result["fire_source"] = "fuel_leak"
    elif any(p in text_l for p in ["engine overheat", "overheating engine"]):
        result["fire_source"] = "engine_overheating"
    elif any(p in text_l for p in ["cng", "lpg", "gas kit"]):
        result["fire_source"] = "cng_lpg_kit"
    elif any(p in text_l for p in ["arson", "deliberately set", "lit on fire"]):
        result["fire_source"] = "arson"
    if any(p in text_l for p in ["fire brigade", "fire department", "fire engine",
                                   "called fire", "fire truck"]):
        result["fire_brigade_called"] = True
    elif any(p in text_l for p in ["no fire brigade", "didn't call fire"]):
        result["fire_brigade_called"] = False
    return result

def extract_flood_specifics(text):
    result = {"flood_water_level": None, "flood_engine_cranked": None}
    text_l = text.lower()
    if any(p in text_l for p in ["fully submerged", "completely submerged",
                                   "roof level", "fully under water"]):
        result["flood_water_level"] = "fully_submerged"
    elif any(p in text_l for p in ["door level", "window level", "chest high",
                                    "up to doors", "dashboard level", "dashboard"]):
        result["flood_water_level"] = "door_level"
    elif any(p in text_l for p in ["tyre level", "knee high", "ankle",
                                    "up to tyres", "wheel level"]):
        result["flood_water_level"] = "tyre_level"
    if any(p in text_l for p in ["started engine", "cranked engine", "tried to start",
                                   "turned ignition", "cranked it", "tried starting"]):
        result["flood_engine_cranked"] = True
    elif any(p in text_l for p in ["did not start", "didn't start engine", "didn't crank",
                                    "engine wouldn't crank", "engine won't crank"]):
        result["flood_engine_cranked"] = False
    return result





CORRECTION_SIGNALS = [
    "actually", "i meant", "correction", "sorry", "mistake",
    "not exactly", "i was wrong", "let me correct", "to clarify",
    "i need to correct", "not a vehicle", "only my car",
    "just the wall", "it was a wall"
]

def detect_correction(text):
    text_l = text.lower()
    return any(sig in text_l for sig in CORRECTION_SIGNALS)





def extract_settlement_preference(text):
    text_l = text.lower()
    if any(p in text_l for p in ["cashless", "network garage", "direct to workshop"]):
        return "cashless"
    if any(p in text_l for p in ["reimbursement", "pay first", "reimburse me"]):
        return "reimbursement"
    return None

def extract_towing_required(text):
    text_l = text.lower()
    if any(p in text_l for p in ["need towing", "tow the car", "call tow", "towing required",
                                   "towed away", "was towed"]):
        return True
    if any(p in text_l for p in ["no towing", "don't need towing", "can drive it"]):
        return False
    return None





def _merge_delta(state, delta):
    new_state = deepcopy(state)
    for key, val in delta.items():
        if val is None:
            continue
        if key == "loss_location" and isinstance(val, dict):
            if not isinstance(new_state.get("loss_location"), dict):
                new_state["loss_location"] = {}
            for k, v in val.items():
                if v is not None:
                    new_state["loss_location"][k] = v
        elif key == "vehicle" and isinstance(val, dict):
            if not isinstance(new_state.get("vehicle"), dict):
                new_state["vehicle"] = {}
            for k, v in val.items():
                if v is not None:
                    new_state["vehicle"][k] = v
        else:
            new_state[key] = val
    return new_state

def _update_extracted_categories(state, delta):
    extracted = list(state.get("already_extracted_categories", []))
    field_to_category = {
        "category":               "incident_type",
        "loss_datetime":          "loss_datetime",
        "third_party_vehicle_id": "third_party_details_registration",
        "police_report_filed":    "legal_reporting_status",
        "drivable":               "drivable",
        "damage_areas":           "damage_areas",
        "damage_severity":        "damage_severity",
        "impact_direction":       "impact_direction",
        "airbags_deployed":       "airbags_deployed",
        "injury_reported":        "injury_reported",
        "witnesses_present":      "witnesses_present",
        "evidence_photos_available": "evidence_photos_available",
        "fir_number":             "fir_number",
        "fire_source":            "fire_source",
        "fire_brigade_called":    "fire_brigade_called",
        "flood_water_level":      "flood_water_level",
        "flood_engine_cranked":   "flood_engine_cranked",
        "theft_keys_available":   "theft_keys_available",
        "theft_forced_entry":     "theft_forced_entry",
        "theft_tracking_device":  "theft_tracking_device",
        "vandalism_type":         "vandalism_type",
        "settlement_preference":  "settlement_preference",
        "towing_required":        "towing_required",
    }
    for field, cat in field_to_category.items():
        val = delta.get(field)
        if val is not None and cat not in extracted:
            extracted.append(cat)
    loc = delta.get("loss_location") or {}
    if isinstance(loc, dict):
        if loc.get("city") and "loss_location_city" not in extracted:
            extracted.append("loss_location_city")
        if loc.get("road_type") and "loss_location_road_type" not in extracted:
            extracted.append("loss_location_road_type")
    vehicle = delta.get("vehicle") or {}
    if isinstance(vehicle, dict):
        if any(v is not None for v in vehicle.values()):
            if "vehicle_details" not in extracted:
                extracted.append("vehicle_details")
    return extracted





def extract_delta(user_text, current_state, context_field=None):
    """
    Parse user_text and return:
      - delta: dict of newly extracted field values
      - corrections: list of field names retracted (set to None)
    All extractors run in parallel; results merged atomically.
    """
    delta = {}
    corrections = []

    new_category = extract_incident_type(user_text)
    if new_category:
        if (new_category == "collision_wall" and
                current_state.get("third_party_involved") is True):
            corrections.append("third_party_involved")
        delta["category"] = new_category

    dt = extract_datetime(user_text)
    if dt:
        delta["loss_datetime"] = dt

    loc = extract_location(user_text)
    if loc.get("city") or loc.get("road_type"):
        delta["loss_location"] = loc

    vehicle = extract_vehicle(user_text)
    if any(v is not None for v in vehicle.values()):
        delta["vehicle"] = vehicle

    reg = extract_registration(user_text)
    if reg:
        if current_state.get("third_party_involved") is True:
            delta["third_party_vehicle_id"] = reg
        else:
            delta["vehicle_registration"] = reg

    drivable = extract_drivable(user_text)
    if drivable is not None:
        delta["drivable"] = drivable

    third_party = extract_third_party(user_text)
    if third_party is not None:
        if detect_correction(user_text) and third_party is False:
            corrections.append("third_party_vehicle_id")
            corrections.append("third_party_details_registration")
        delta["third_party_involved"] = third_party

    police = extract_police_report(user_text)
    if police is not None:
        delta["police_report_filed"] = police

    station_m = re.search(
        r'(?:at|from)\s+([A-Za-z][A-Za-z ]{2,40}?)\s+(?:police\s+)?station',
        user_text, re.IGNORECASE)
    if station_m:
        raw = station_m.group(1).strip()
        if raw.lower() not in ("the", "a", "this", "police", ""):
            delta["police_station"] = raw

    injury = extract_injury(user_text)
    if injury is not None:
        delta["injury_reported"] = injury

    airbags = extract_airbags(user_text)
    if airbags is not None:
        delta["airbags_deployed"] = airbags

    witnesses = extract_witnesses(user_text)
    if witnesses is not None:
        delta["witnesses_present"] = witnesses

    photos = extract_photos(user_text)
    if photos is not None:
        delta["evidence_photos_available"] = photos

    fir = extract_fir_number(user_text)
    if fir:
        delta["fir_number"] = fir

    direction = extract_impact_direction(user_text)
    if direction:
        delta["impact_direction"] = direction

    severity = extract_damage_severity(user_text)
    if severity:
        delta["damage_severity"] = severity

    if current_state.get("category") == "theft" or new_category == "theft":
        theft = extract_theft_specifics(user_text)
        delta.update({k: v for k, v in theft.items() if v is not None})

    if current_state.get("category") == "fire" or new_category == "fire":
        fire = extract_fire_specifics(user_text)
        delta.update({k: v for k, v in fire.items() if v is not None})

    if current_state.get("category") in ("flood", "natural_disaster") or\
            new_category in ("flood", "natural_disaster"):
        flood = extract_flood_specifics(user_text)
        delta.update({k: v for k, v in flood.items() if v is not None})

    settlement = extract_settlement_preference(user_text)
    if settlement:
        delta["settlement_preference"] = settlement

    towing = extract_towing_required(user_text)
    if towing is not None:
        delta["towing_required"] = towing


    if not delta and not corrections and context_field:
        _AFFIRM = {"yes", "yeah", "yep", "yup", "correct", "that's right",
                   "thats right", "sure", "definitely", "absolutely",
                   "of course", "obviously", "right", "true", "confirmed",
                   "it was", "it did", "i did", "we did", "i do", "it does"}
        _NEGATE = {"no", "nope", "nah", "not really", "negative",
                   "i did not", "i didn't", "we did not", "we didn't",
                   "it did not", "it didn't", "it was not", "it wasn't",
                   "there was not", "there wasn't", "none", "never",
                   "not at all", "no it did not", "no it didn't"}
        BOOLEAN_FIELDS = {
            "police_report_filed", "injury_reported", "third_party_involved",
            "hit_and_run", "witnesses_present", "evidence_photos_available",
            "evidence_video_available", "dashcam_available", "drivable",
            "vehicle_towed", "airbags_deployed", "theft_keys_available",
            "theft_forced_entry", "theft_tracking_device", "fire_brigade_called",
            "flood_engine_cranked", "policy_active", "driver_is_owner",
            "driver_license_valid", "previous_claims", "signal_compliance",
        }
        t = user_text.strip().lower().rstrip(".")
        if context_field in BOOLEAN_FIELDS:
            if t in _AFFIRM or any(t.startswith(a) for a in _AFFIRM):
                delta[context_field] = True
            elif t in _NEGATE or any(t.startswith(n) for n in _NEGATE):
                delta[context_field] = False


    STRING_CONTEXT_MAP = {
        "impact_direction": {
            "front": "front", "frontal": "front", "head on": "front",
            "rear": "rear", "back": "rear", "from behind": "rear",
            "side": "side", "t-bone": "side",
            "left": "left_side", "left side": "left_side", "driver side": "left_side",
            "right": "right_side", "right side": "right_side", "passenger side": "right_side",
            "rollover": "rollover", "rolled over": "rollover", "flipped": "rollover",
        },
        "damage_severity": {
            "minor": "minor", "small": "minor", "slight": "minor", "scratch": "minor",
            "moderate": "moderate", "medium": "moderate", "significant": "moderate",
            "severe": "severe", "major": "severe", "bad": "severe", "heavy": "severe",
            "total loss": "total_loss", "write off": "total_loss", "total": "total_loss",
            "totalled": "total_loss", "written off": "total_loss",
        },
        "vehicle_moving_status": {
            "moving": "moving", "driving": "moving", "stationary": "stationary",
            "parked": "parked", "stopped": "stationary",
        },
        "road_condition": {
            "wet": "wet", "dry": "dry", "icy": "icy", "flooded": "flooded",
            "pothole": "potholed", "smooth": "smooth", "muddy": "muddy",
        },
        "weather_condition": {
            "clear": "clear", "sunny": "clear", "rain": "rain", "raining": "rain",
            "heavy rain": "heavy_rain", "fog": "fog", "foggy": "fog",
            "dark": "night", "night": "night", "storm": "storm",
        },
    }
    if context_field and context_field in STRING_CONTEXT_MAP:
        if not delta.get(context_field):
            t_lower = user_text.strip().lower().rstrip(".!?")
            mapping = STRING_CONTEXT_MAP[context_field]
            if t_lower in mapping:
                delta[context_field] = mapping[t_lower]
            else:
                for phrase in sorted(mapping.keys(), key=len, reverse=True):
                    if phrase in t_lower:
                        delta[context_field] = mapping[phrase]
                        break

    return delta, corrections

def apply_delta(current_state, delta, corrections, answered_qid=None):
    """Apply extracted delta and corrections to current state."""
    new_state = _merge_delta(current_state, delta)

    for field in corrections:
        if field in new_state:
            new_state[field] = None
        extracted = new_state.get("already_extracted_categories", [])
        if field in extracted:
            extracted.remove(field)
        new_state["already_extracted_categories"] = extracted

    new_state["already_extracted_categories"] = _update_extracted_categories(
        current_state, delta
    )
    for corr in corrections:
        cats = new_state.get("already_extracted_categories", [])
        if corr in cats:
            cats.remove(corr)
        new_state["already_extracted_categories"] = cats

    if answered_qid:
        answered = list(new_state.get("answered_question_ids", []))
        if answered_qid not in answered:
            answered.append(answered_qid)
        new_state["answered_question_ids"] = answered

    return new_state





if __name__ == "__main__":
    test_inputs = [
        "My car had an accident and got hit from the side by a bike in Pune yesterday.",
        "Yeah it was MH12AB1234, the accident happened on March 2, 2026",
        "minor collision, we exchanged details. We did not call police",
        "Actually it was a wall, no other vehicle. I was alone.",
        "The car was stolen from outside my house in Mumbai last night.",
        "The vehicle caught fire near the highway, the engine started burning.",
        "It was a flood. The water was up to the dashboard.",
    ]
    state = {
        "category": None, "loss_datetime": None,
        "loss_location": {"city": None, "road_type": None},
        "vehicle": {"make": None, "model": None, "year": None},
        "third_party_involved": None, "third_party_vehicle_id": None,
        "police_report_filed": None, "drivable": None, "damage_severity": None,
        "injury_reported": None, "theft_keys_available": None,
        "theft_forced_entry": None, "fire_source": None,
        "fire_brigade_called": None, "flood_water_level": None,
        "flood_engine_cranked": None,
        "already_extracted_categories": [], "answered_question_ids": [],
    }
    for txt in test_inputs:
        print(f"\nInput: {txt[:60]}...")
        delta, corrections = extract_delta(txt, state)
        state = apply_delta(state, delta, corrections)
        non_null = {k: v for k, v in state.items()
                    if v is not None and v != [] and v != {"city": None, "road_type": None}
                    and v != {"make": None, "model": None, "year": None}}
        print(f"  State: {non_null}")
        if corrections:
            print(f"  Corrections: {corrections}")
