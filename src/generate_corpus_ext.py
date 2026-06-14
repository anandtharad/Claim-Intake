import json
import os

BASE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "question_bank_raw.jsonl")

def get_last_id(path):
    last = 0
    if not os.path.exists(path):
        return 0
    with open(path) as f:
        for line in f:
            q = json.loads(line)
            num = int(q["id"][1:])
            if num > last:
                last = num
    return last

_counter = [0]

def set_start(n):
    _counter[0] = n

def qid():
    _counter[0] += 1
    return f"Q{_counter[0]:04d}"

def q(text, field, priority, triggers, fills, cat):
    return {
        "id": qid(),
        "text": text,
        "question_field": field,
        "priority": priority,
        "category_tag": cat,
        "triggers": triggers,
        "targets": {"fill_fields": fills}
    }

ALL_INCIDENT_TYPES = [
    "collision","collision_wall","collision_animal","hit_and_run",
    "theft","theft_attempted","fire","flood","vandalism",
    "natural_disaster","self_accident","rollover"
]
COLLISION_TYPES = ["collision","hit_and_run","self_accident","rollover","collision_wall","collision_animal"]
DAMAGE_TYPES = ["collision","hit_and_run","self_accident","rollover","vandalism","fire","flood","collision_wall","natural_disaster","collision_animal"]

DAMAGE_ZONES = [
    ("front bumper",          "damage_areas_front_bumper",    "damage_areas"),
    ("rear bumper",           "damage_areas_rear_bumper",     "damage_areas"),
    ("left front door",       "damage_areas_left_door_front", "damage_areas"),
    ("left rear door",        "damage_areas_left_door_rear",  "damage_areas"),
    ("right front door",      "damage_areas_right_door_front","damage_areas"),
    ("right rear door",       "damage_areas_right_door_rear", "damage_areas"),
    ("hood / bonnet",         "damage_areas_hood",            "damage_areas"),
    ("boot / trunk lid",      "damage_areas_boot",            "damage_areas"),
    ("roof",                  "damage_areas_roof",            "damage_areas"),
    ("front windshield",      "damage_areas_windshield_front","damage_areas"),
    ("rear windshield",       "damage_areas_windshield_rear", "damage_areas"),
    ("left headlamp",         "damage_areas_left_headlamp",   "damage_areas"),
    ("right headlamp",        "damage_areas_right_headlamp",  "damage_areas"),
    ("left tail lamp",        "damage_areas_left_tail_lamp",  "damage_areas"),
    ("right tail lamp",       "damage_areas_right_tail_lamp", "damage_areas"),
    ("left fender",           "damage_areas_left_fender",     "damage_areas"),
    ("right fender",          "damage_areas_right_fender",    "damage_areas"),
    ("underbody / chassis",   "damage_areas_underbody",       "damage_areas"),
    ("engine compartment",    "damage_areas_engine",          "damage_areas"),
    ("fuel tank",             "damage_areas_fuel_tank",       "damage_areas"),
    ("left front tyre",       "damage_areas_tyre_fl",         "damage_areas"),
    ("right front tyre",      "damage_areas_tyre_fr",         "damage_areas"),
    ("left rear tyre",        "damage_areas_tyre_rl",         "damage_areas"),
    ("right rear tyre",       "damage_areas_tyre_rr",         "damage_areas"),
    ("steering wheel assembly","damage_areas_steering",       "damage_areas"),
    ("gear box / transmission","damage_areas_gearbox",        "damage_areas"),
    ("radiator",              "damage_areas_radiator",        "damage_areas"),
    ("battery",               "damage_areas_battery",         "damage_areas"),
    ("exhaust / silencer",    "damage_areas_exhaust",         "damage_areas"),
    ("dashboard / instrument cluster","damage_areas_dashboard","damage_areas"),
    ("airbag (driver side)",  "airbags_deployed",             "airbags_deployed"),
    ("airbag (passenger side)","airbags_deployed",            "airbags_deployed"),
]

def gen_damage_zone_expanded():
    """
    For each damage zone, generate 5 distinct question types:
      1. repair feasibility
      2. photo evidence availability
      3. pre-existing damage check
      4. severity detail
      5. workshop assessment
    """
    qs = []
    triggers = {"incident_type": DAMAGE_TYPES, "required_fields_present": ["damage_areas"]}
    for zone_name, zone_field, fill in DAMAGE_ZONES:
        qs += [
            q(f"Can the {zone_name} be repaired, or does it need a full replacement?",
              zone_field + "_repair", 3, {"incident_type": DAMAGE_TYPES, "required_fields_present": ["damage_areas"]},
              [fill], "damage_assessment"),
            q(f"Do you have clear photographs of the damage to the {zone_name}?",
              "evidence_photos_available", 3, {"incident_type": DAMAGE_TYPES},
              ["evidence_photos_available"], "damage_assessment"),
            q(f"Was there any pre-existing damage to the {zone_name} before this incident?",
              zone_field + "_preexist", 2, {"incident_type": DAMAGE_TYPES, "required_fields_present": ["damage_areas"]},
              [fill], "fraud_consistency"),
            q(f"Has a mechanic or workshop assessed the damage to the {zone_name}?",
              zone_field + "_assessed", 4, {"incident_type": DAMAGE_TYPES, "required_fields_present": ["damage_areas"]},
              ["repair_preference"], "repair_settlement"),
            q(f"Describe the extent of damage to the {zone_name} in more detail.",
              zone_field + "_detail", 3, {"incident_type": DAMAGE_TYPES, "required_fields_present": ["damage_areas"]},
              [fill], "damage_assessment"),
        ]
    return qs

def gen_incident_timeline():
    """Generate detailed timeline / sequence-of-events questions per incident type."""
    qs = []
    scenarios = [

        (["collision","hit_and_run"],   "just before the collision"),
        (["collision","self_accident"],  "leading up to the accident"),
        (["theft"],                      "before the vehicle was noticed missing"),
        (["fire"],                       "before the fire started"),
        (["flood","natural_disaster"],   "before the flood affected the vehicle"),
        (["vandalism"],                  "before the vandalism was discovered"),
    ]
    for it_list, context in scenarios:
        triggers_base = {"incident_type": it_list}
        qs += [
            q(f"Walk us through what happened step by step {context}.",
              "loss_datetime", 2, triggers_base, ["loss_datetime"], "incident_basics"),
            q(f"What were you doing approximately 10 minutes {context}?",
              "loss_datetime", 3, triggers_base, ["loss_datetime"], "incident_basics"),
            q(f"Were there any warning signs {context}?",
              "loss_datetime", 3, triggers_base, ["loss_datetime"], "incident_basics"),
            q(f"Was the vehicle behaving normally {context}?",
              "vehicle_moving_status", 3, triggers_base, ["vehicle_moving_status"], "incident_basics"),
            q(f"Were you alone in the vehicle {context}?",
              "injury_reported", 2, triggers_base, ["injury_reported"], "incident_basics"),
            q(f"Had you recently stopped or refuelled {context}?",
              "vehicle_moving_status", 4, triggers_base, ["vehicle_moving_status"], "incident_basics"),
            q(f"Was there any unusual noise or smell from the vehicle {context}?",
              "vehicle_moving_status", 3, triggers_base, ["vehicle_moving_status"], "incident_basics"),
        ]
    return qs

def gen_documentation_checklist():
    """Per-document-type availability questions for every incident type."""
    qs = []
    doc_questions = [
        ("driving_license", "Do you have your driving licence available for submission?", 3,
         ["driver_license_valid"]),
        ("RC_copy", "Is the vehicle's Registration Certificate (RC) available?", 3,
         ["vehicle"]),
        ("insurance_policy", "Do you have the insurance policy document with you?", 2,
         ["policy_number"]),
        ("repair_estimate", "Has a repair estimate been obtained from a garage?", 4,
         ["evidence_photos_available"]),
        ("photos_vehicle", "Have photographs of the damaged vehicle been taken?", 2,
         ["evidence_photos_available"]),
        ("photos_scene", "Have photographs of the accident scene been taken?", 3,
         ["evidence_photos_available"]),
        ("video_dashcam", "Is dashcam footage available and can it be retrieved?", 3,
         ["dashcam_available"]),
        ("video_cctv", "Is CCTV footage from the area available?", 4,
         ["evidence_video_available"]),
        ("medical_report", "Is a medical report available for any injuries sustained?", 2,
         ["injury_details"]),
        ("witness_statement", "Have written statements been obtained from witnesses?", 4,
         ["witness_contact"]),
        ("towing_receipt", "Is there a receipt for towing services?", 5,
         ["towing_required"]),
    ]
    for doc_id, text, priority, fills in doc_questions:
        for it in ALL_INCIDENT_TYPES:
            qs.append(q(
                text,
                f"doc_{doc_id}_available",
                priority,
                {"incident_type": [it]},
                fills,
                "legal_reporting"
            ))
    return qs

def gen_driver_details():
    """Expanded driver identification and eligibility questions."""
    qs = []
    base_types = ["collision","theft","fire","flood","vandalism","hit_and_run","self_accident","rollover","natural_disaster"]
    driver_qs = [
        ("What is the full name of the person who was driving the vehicle at the time?", "driver_name", 2, ["driver_name"]),
        ("What is the age of the driver at the time of the incident?", "driver_name", 3, ["driver_name"]),
        ("What is the driver's licence number?", "driver_license_valid", 2, ["driver_license_valid"]),
        ("When was the driver's licence issued and what is its validity?", "driver_license_valid", 3, ["driver_license_valid"]),
        ("Has the driver ever had a licence suspension or penalty?", "driver_license_valid", 3, ["driver_license_valid"]),
        ("Was the driver wearing a seat belt at the time of the incident?", "injury_reported", 3, ["injury_reported"]),
        ("Were the passengers wearing seat belts?", "injury_reported", 3, ["injury_reported"]),
        ("Was the driver using a mobile phone at the time?", "signal_compliance", 2, ["signal_compliance"]),
        ("Was the driver under the influence of any medication that impairs driving?", "driver_license_valid", 2, ["driver_license_valid"]),
        ("Had the driver consumed any alcohol before the incident?", "driver_license_valid", 1, ["driver_license_valid"]),
        ("How many years of driving experience does the driver have?", "driver_license_valid", 4, ["driver_license_valid"]),
        ("Is the driver a habitual offender or has prior traffic violations?", "driver_license_valid", 3, ["driver_license_valid"]),
        ("Is the driver listed as a named driver on the insurance policy?", "driver_is_owner", 2, ["driver_is_owner"]),
        ("Is the policy holder present at the time of this claim?", "driver_is_owner", 3, ["driver_is_owner"]),
        ("Was the vehicle handed over to the driver by the owner?", "driver_is_owner", 3, ["driver_is_owner"]),
        ("Was the driver authorised by the registered owner to use the vehicle?", "driver_is_owner", 2, ["driver_is_owner"]),
        ("Did the driver have a commercial or transport driving permit?", "driver_license_valid", 4, ["driver_license_valid"]),
        ("Was the driver a first-time user of this specific vehicle model?", "driver_license_valid", 4, ["driver_license_valid"]),
        ("Was the driver a minor at the time of the incident?", "driver_license_valid", 1, ["driver_license_valid"]),
        ("Was the driver wearing prescription glasses or aids required for driving?", "driver_license_valid", 4, ["driver_license_valid"]),
    ]
    for text, field, priority, fills in driver_qs:
        qs.append(q(text, field, priority, {"incident_type": base_types}, fills, "policy_eligibility"))
    return qs

def gen_collision_scenario_matrix():
    """
    Cross-product: impact direction × vehicle type × road type
    producing scenario-specific questions.
    """
    qs = []
    directions = ["front", "rear", "left side", "right side"]
    other_vehicles = ["motorcycle", "car", "truck", "bus", "auto-rickshaw", "cycle"]
    road_types = ["highway", "urban road", "rural road", "expressway", "flyover"]

    for direction in directions:
        for vehicle in other_vehicles:
            qs.append(q(
                f"Was the impact from the {direction} caused by a {vehicle}?",
                "impact_direction",
                3,
                {"incident_type": ["collision","hit_and_run"], "third_party_involved": True},
                ["impact_direction", "third_party_vehicle_id"],
                "collision_dynamics"
            ))

    for road in road_types:
        qs += [
            q(f"Was the accident on a {road} — what was the approximate speed limit?",
              "speed_estimate", 3, {"incident_type": COLLISION_TYPES},
              ["speed_estimate"], "collision_dynamics"),
            q(f"Were there adequate streetlights on the {road} at the time of the accident?",
              "weather_condition", 4, {"incident_type": COLLISION_TYPES},
              ["weather_condition"], "collision_dynamics"),
            q(f"Was there heavy traffic on the {road} when the incident occurred?",
              "lane_action", 3, {"incident_type": COLLISION_TYPES},
              ["lane_action"], "collision_dynamics"),
        ]

    for direction in directions:
        qs += [
            q(f"Was the {direction} impact a glancing blow or full-force collision?",
              "impact_direction", 3, {"incident_type": ["collision","hit_and_run"]},
              ["impact_direction"], "collision_dynamics"),
            q(f"Were airbags deployed as a result of the {direction} impact?",
              "airbags_deployed", 2, {"incident_type": ["collision","hit_and_run","self_accident","rollover"]},
              ["airbags_deployed"], "collision_dynamics"),
            q(f"Was the {direction} damage severe enough to impair vehicle control?",
              "damage_severity", 3, {"incident_type": ["collision","hit_and_run","self_accident"]},
              ["damage_severity"], "damage_assessment"),
        ]

    return qs

def gen_fraud_expanded():
    """Additional fraud and consistency verification questions."""
    qs = []
    fraud_extra = [
        ("Was the vehicle recently put up for sale before this claim?", "previous_claims", 2,
         ALL_INCIDENT_TYPES, ["previous_claims"]),
        ("Is the vehicle currently under any dispute of ownership?", "driver_is_owner", 2,
         ALL_INCIDENT_TYPES, ["driver_is_owner"]),
        ("Has any part of the damage been repaired before this claim was filed?", "damage_severity", 1,
         DAMAGE_TYPES, ["damage_severity"]),
        ("Were any repair receipts submitted that predate the incident?", "evidence_photos_available", 1,
         DAMAGE_TYPES, ["evidence_photos_available"]),
        ("Have multiple policies been claimed for the same incident?", "policy_number", 1,
         ALL_INCIDENT_TYPES, ["policy_number"]),
        ("Was the vehicle insured for more than its market value?", "coverage_type", 2,
         ALL_INCIDENT_TYPES, ["coverage_type"]),
        ("Were the damage descriptions consistent across all statements given?", "damage_severity", 1,
         DAMAGE_TYPES, ["damage_severity"]),
        ("Did the incident happen in a location inconsistent with the vehicle's usage pattern?", "loss_location_road_type", 2,
         ALL_INCIDENT_TYPES, ["loss_location"]),
        ("Were there any social media posts contradicting the claimed incident details?", "previous_claims", 2,
         ALL_INCIDENT_TYPES, ["previous_claims"]),
        ("Was the vehicle in good working condition just before the incident?", "damage_severity", 2,
         DAMAGE_TYPES, ["damage_severity"]),
        ("Has the vehicle been involved in a total loss claim in the past 2 years?", "previous_claims", 1,
         ALL_INCIDENT_TYPES, ["previous_claims"]),
        ("Is the claimed incident location consistent with GPS or toll records?", "loss_location_city", 2,
         COLLISION_TYPES + ["theft","fire","flood","vandalism","natural_disaster"],
         ["loss_location"]),
        ("Were there any inconsistencies between the verbal account and written FIR?", "fir_number", 1,
         ["collision","hit_and_run","theft","fire","vandalism"],
         ["fir_number"]),
        ("Was the vehicle serviced at an unusual workshop before the claim?", "repair_preference", 3,
         DAMAGE_TYPES, ["repair_preference"]),
        ("Has there been a pattern of small claims followed by a major claim?", "previous_claims", 2,
         ALL_INCIDENT_TYPES, ["previous_claims"]),
        ("Were any aftermarket parts or accessories listed that were not factory-fitted?", "damage_areas", 3,
         DAMAGE_TYPES, ["damage_areas"]),
        ("Was the vehicle involved in any racing or stunt activity before the incident?", "vehicle_usage_type", 2,
         COLLISION_TYPES, ["vehicle_usage_type"]),
        ("Is the claimant a first-time policy holder with this insurer?", "policy_number", 3,
         ALL_INCIDENT_TYPES, ["policy_number"]),
        ("Were there any unpaid premiums before this claim was filed?", "policy_active", 1,
         ALL_INCIDENT_TYPES, ["policy_active"]),
        ("Was the claim filed through an intermediary or agent rather than directly?", "policy_number", 4,
         ALL_INCIDENT_TYPES, ["policy_number"]),
    ]
    for text, field, priority, it_list, fills in fraud_extra:
        qs.append(q(text, field, priority, {"incident_type": it_list}, fills, "fraud_consistency"))
    return qs

def gen_settlement_expanded():
    """Expanded repair and settlement questions."""
    qs = []
    settlement_extra = [
        ("Have you visited the nearest network garage to get an initial assessment?",
         "repair_preference", 4, ALL_INCIDENT_TYPES, ["repair_preference"]),
        ("Was the vehicle taken to the garage within 48 hours of the incident?",
         "repair_preference", 4, DAMAGE_TYPES, ["repair_preference"]),
        ("Did the workshop provide a written job card or estimate?",
         "evidence_photos_available", 4, DAMAGE_TYPES, ["evidence_photos_available"]),
        ("Are you expecting a full replacement or a repair for the damaged parts?",
         "damage_severity", 4, DAMAGE_TYPES, ["damage_severity"]),
        ("Is the vehicle currently at the accident spot, your residence, or a garage?",
         "loss_location_city", 3, DAMAGE_TYPES + ["theft"], ["loss_location"]),
        ("Has the surveyor been arranged for a vehicle inspection?",
         "repair_preference", 3, ALL_INCIDENT_TYPES, ["repair_preference"]),
        ("Will you need emergency accommodation or assistance due to this incident?",
         "add_ons", 4, ["collision","fire","flood","rollover","natural_disaster"], ["add_ons"]),
        ("Has the towing bill been shared with the insurer?",
         "towing_required", 5, DAMAGE_TYPES, ["towing_required"]),
        ("Is the repair at a network garage already authorised by the insurer?",
         "repair_preference", 4, DAMAGE_TYPES, ["repair_preference"]),
        ("Do you want partial payment for immediate repairs while the survey is pending?",
         "settlement_preference", 4, DAMAGE_TYPES, ["settlement_preference"]),
        ("Will you be claiming for accessories or modifications separately?",
         "add_ons", 4, DAMAGE_TYPES, ["add_ons"]),
        ("Have you filed a salvage or scrap application for a total loss vehicle?",
         "damage_severity", 3, DAMAGE_TYPES, ["damage_severity"]),
        ("Does the workshop have cashless approval from the insurer?",
         "repair_preference", 4, DAMAGE_TYPES, ["repair_preference"]),
        ("Are there any hidden or latent damages found after the initial inspection?",
         "damage_areas", 4, DAMAGE_TYPES, ["damage_areas"]),
        ("Do you consent to the insurer conducting an independent vehicle inspection?",
         "repair_preference", 3, ALL_INCIDENT_TYPES, ["repair_preference"]),
    ]
    for text, field, priority, it_list, fills in settlement_extra:
        qs.append(q(text, field, priority, {"incident_type": it_list}, fills, "repair_settlement"))
    return qs

def gen_theft_expanded():
    """More theft-specific scenario questions."""
    qs = []
    theft_extra = [
        ("Was your vehicle parked in a basement or covered parking when stolen?",
         "loss_location_road_type", 3, ["theft"], ["loss_location"]),
        ("Did any valet or parking attendant have access to the vehicle?",
         "theft_forced_entry", 2, ["theft"], ["theft_forced_entry"]),
        ("Was the vehicle's OBD port or ECU tampered with?",
         "theft_forced_entry", 2, ["theft"], ["theft_forced_entry"]),
        ("Was the key fob signal cloned or jammed?",
         "theft_forced_entry", 2, ["theft"], ["theft_forced_entry"]),
        ("Were any duplicate keys made without the owner's knowledge?",
         "theft_keys_available", 2, ["theft"], ["theft_keys_available"]),
        ("Did the vehicle have a manual immobiliser?",
         "theft_tracking_device", 3, ["theft","theft_attempted"], ["theft_tracking_device"]),
        ("Was the vehicle in a busy market or mall area when stolen?",
         "loss_location_road_type", 3, ["theft"], ["loss_location"]),
        ("Was the theft reported to the Regional Transport Office (RTO)?",
         "police_report_filed", 2, ["theft"], ["police_report_filed"]),
        ("Did you submit a Non-Traceable Certificate from the police?",
         "fir_number", 3, ["theft"], ["fir_number"]),
        ("How long was the vehicle at the location before the theft was noticed?",
         "loss_datetime", 3, ["theft"], ["loss_datetime"]),
        ("Were any valuables inside the vehicle when it was stolen?",
         "theft_forced_entry", 3, ["theft"], ["theft_forced_entry"]),
        ("Was the vehicle tracked using a fleet management system?",
         "theft_tracking_device", 3, ["theft"], ["theft_tracking_device"]),
        ("Was the vehicle recovered in another city or state?",
         "loss_location_city", 3, ["theft"], ["loss_location"]),
        ("Was the vehicle's number plate changed after theft?",
         "theft_forced_entry", 3, ["theft"], ["theft_forced_entry"]),
        ("Was there any ransom demand after the vehicle was stolen?",
         "theft_forced_entry", 2, ["theft"], ["theft_forced_entry"]),
        ("Did the police file a panchnama for the recovered vehicle?",
         "fir_number", 3, ["theft"], ["fir_number"]),
        ("Was the theft covered by the comprehensive section of your policy?",
         "coverage_type", 2, ["theft"], ["coverage_type"]),
        ("Did you have a Homologation certificate for any accessories?",
         "add_ons", 5, ["theft"], ["add_ons"]),
        ("Is the stolen vehicle hypothecated to a bank?",
         "policy_number", 3, ["theft"], ["policy_number"]),
        ("Was the vehicle at a service centre when reported stolen?",
         "loss_location_road_type", 3, ["theft"], ["loss_location"]),
    ]
    for text, field, priority, it_list, fills in theft_extra:
        qs.append(q(text, field, priority, {"incident_type": it_list}, fills, "theft_specific"))
    return qs

def gen_fire_expanded():
    """More fire-specific questions."""
    qs = []
    fire_extra = [
        ("Was the fire due to a catalytic converter overheating?",
         "fire_source", 3, ["fire"], ["fire_source"]),
        ("Was the vehicle near any industrial or chemical area when it caught fire?",
         "loss_location_city", 3, ["fire"], ["loss_location"]),
        ("Was a fuel pipe leaking before the fire broke out?",
         "fire_source", 3, ["fire"], ["fire_source"]),
        ("Did the fire start from the exhaust or muffler region?",
         "fire_source", 3, ["fire"], ["fire_source"]),
        ("Was there an explosion or bang heard before the fire?",
         "fire_source", 2, ["fire"], ["fire_source"]),
        ("Was the vehicle's bonnet released or open before the fire?",
         "vehicle_moving_status", 3, ["fire"], ["vehicle_moving_status"]),
        ("Was the fire suppressed using a hand-held fire extinguisher?",
         "fire_brigade_called", 3, ["fire"], ["fire_brigade_called"]),
        ("Were tyres melted or wheels damaged in the fire?",
         "damage_areas", 3, ["fire"], ["damage_areas"]),
        ("Was the parking brake or gear engaged during the fire?",
         "vehicle_moving_status", 4, ["fire"], ["vehicle_moving_status"]),
        ("Were any toxic or hazardous materials in the vehicle that worsened the fire?",
         "fire_source", 3, ["fire"], ["fire_source"]),
        ("Did the vehicle's alarm activate before the fire?",
         "theft_tracking_device", 4, ["fire"], ["theft_tracking_device"]),
        ("Were other vehicles in proximity also damaged by the fire?",
         "third_party_involved", 3, ["fire"], ["third_party_involved"]),
        ("Was the vehicle previously reported to have electrical issues?",
         "fire_source", 3, ["fire"], ["fire_source"]),
        ("Was the CNG cylinder within its validity period?",
         "fire_source", 2, ["fire"], ["fire_source"]),
        ("Was the vehicle engine recently replaced or rebuilt?",
         "fire_source", 4, ["fire"], ["fire_source"]),
        ("Was any welding or repair work done under the bonnet recently?",
         "fire_source", 3, ["fire"], ["fire_source"]),
        ("Was the vehicle caught in a wildfire or a burning building?",
         "loss_location_city", 2, ["fire","natural_disaster"], ["loss_location"]),
        ("Was the fire triggered by a short circuit in an accessory?",
         "fire_source", 3, ["fire"], ["fire_source"]),
        ("Did the fire brigade issue a fire cause certificate?",
         "fire_brigade_called", 3, ["fire"], ["fire_brigade_called"]),
        ("Was the vehicle battery a lithium-ion or AGM type?",
         "fire_source", 4, ["fire"], ["fire_source"]),
    ]
    for text, field, priority, it_list, fills in fire_extra:
        qs.append(q(text, field, priority, {"incident_type": it_list}, fills, "fire_specific"))
    return qs

def gen_flood_expanded():
    """More flood-specific questions."""
    qs = []
    flood_extra = [
        ("Was the vehicle in a basement parking when flooded?",
         "loss_location_road_type", 3, ["flood","natural_disaster"], ["loss_location"]),
        ("Was the vehicle completely non-functional after flood exposure?",
         "drivable", 2, ["flood","natural_disaster"], ["drivable"]),
        ("Was the catalytic converter damaged due to flood water?",
         "damage_areas_engine", 3, ["flood","natural_disaster"], ["damage_areas"]),
        ("Was the engine replaced or rebuilt before the flood?",
         "flood_engine_cranked", 4, ["flood","natural_disaster"], ["flood_engine_cranked"]),
        ("Was the flood a result of a broken pipeline or dam release?",
         "flood_water_level", 3, ["flood","natural_disaster"], ["flood_water_level"]),
        ("Were the car seats and interior fabric waterlogged?",
         "damage_areas", 3, ["flood","natural_disaster"], ["damage_areas"]),
        ("Was there mould or rust developing inside the vehicle post-flood?",
         "damage_areas", 3, ["flood","natural_disaster"], ["damage_areas"]),
        ("Was the flood covered under a declared natural calamity zone?",
         "loss_location_city", 3, ["flood","natural_disaster"], ["loss_location"]),
        ("Did the insurer receive government notification of the flood zone?",
         "evidence_photos_available", 4, ["flood","natural_disaster"], ["evidence_photos_available"]),
        ("Was the power windows or sunroof mechanism affected?",
         "damage_areas", 3, ["flood","natural_disaster"], ["damage_areas"]),
        ("Was the ABS or traction control system damaged?",
         "damage_areas_suspension", 3, ["flood","natural_disaster"], ["damage_areas"]),
        ("Was the vehicle on or near a river bank when it got flooded?",
         "loss_location_city", 3, ["flood","natural_disaster"], ["loss_location"]),
        ("Were airbags or seatbelt pretensioners affected by water?",
         "airbags_deployed", 3, ["flood","natural_disaster"], ["airbags_deployed"]),
        ("Did you drive the vehicle into the flooded road knowingly?",
         "vehicle_moving_status", 2, ["flood"], ["vehicle_moving_status"]),
        ("Was the vehicle parked near a storm drain that overflowed?",
         "loss_location_city", 3, ["flood","natural_disaster"], ["loss_location"]),
        ("Was the carburettor or fuel injector hydrolocked?",
         "flood_engine_cranked", 3, ["flood","natural_disaster"], ["flood_engine_cranked"]),
        ("Were the speedometer and odometer affected by water ingress?",
         "damage_areas_dashboard", 3, ["flood","natural_disaster"], ["damage_areas"]),
        ("Was an advance flood warning in effect when the vehicle was left at the location?",
         "loss_datetime", 3, ["flood","natural_disaster"], ["loss_datetime"]),
    ]
    for text, field, priority, it_list, fills in flood_extra:
        qs.append(q(text, field, priority, {"incident_type": it_list}, fills, "flood_specific"))
    return qs

def gen_vandalism_expanded():
    """More vandalism-specific questions."""
    qs = []
    vandalism_extra = [
        ("Were the side view mirrors broken or stolen?",
         "damage_areas", 3, ["vandalism"], ["damage_areas"]),
        ("Was the catalytic converter stolen from under the vehicle?",
         "vandalism_type", 3, ["vandalism"], ["vandalism_type"]),
        ("Were the spare tyre or tools from the boot stolen?",
         "vandalism_type", 3, ["vandalism"], ["vandalism_type"]),
        ("Were the door handles or hinges damaged?",
         "damage_areas", 3, ["vandalism"], ["damage_areas"]),
        ("Was offensive content sprayed on the vehicle?",
         "vandalism_type", 4, ["vandalism"], ["vandalism_type"]),
        ("Was the fuel cap sealed with glue or damaged?",
         "vandalism_type", 3, ["vandalism"], ["vandalism_type"]),
        ("Were any aftermarket accessories stripped from the vehicle?",
         "vandalism_type", 3, ["vandalism"], ["vandalism_type"]),
        ("Was the windscreen wiper motor or assembly stolen?",
         "damage_areas", 4, ["vandalism"], ["damage_areas"]),
        ("Were the vehicle's headlamps or fog lamps specifically targeted?",
         "damage_areas_headlamp", 3, ["vandalism"], ["damage_areas"]),
        ("Was the vandalism localised to one side of the vehicle?",
         "vandalism_type", 3, ["vandalism"], ["vandalism_type"]),
        ("Was this a targeted attack or random vandalism?",
         "vandalism_type", 3, ["vandalism"], ["vandalism_type"]),
        ("Were there any threatening notes or messages left on the vehicle?",
         "vandalism_type", 3, ["vandalism"], ["vandalism_type"]),
        ("Were any body kits or spoilers removed or damaged?",
         "damage_areas", 4, ["vandalism"], ["damage_areas"]),
        ("Was the vehicle registered in the name of the victim of the vandalism?",
         "driver_is_owner", 4, ["vandalism"], ["driver_is_owner"]),
        ("Was the vandalism reported to the residential welfare association or security?",
         "police_report_filed", 3, ["vandalism"], ["police_report_filed"]),
    ]
    for text, field, priority, it_list, fills in vandalism_extra:
        qs.append(q(text, field, priority, {"incident_type": it_list}, fills, "vandalism_specific"))
    return qs

def gen_natural_disaster_specific():
    """Questions specific to natural disaster events."""
    qs = []
    nd_qs = [
        ("Was the vehicle damaged in a hailstorm?",
         "weather_condition", 2, ["natural_disaster"], ["weather_condition"]),
        ("Was the vehicle damaged by falling debris or a tree?",
         "damage_areas", 2, ["natural_disaster"], ["damage_areas"]),
        ("Was there an earthquake that caused the vehicle damage?",
         "loss_location_city", 2, ["natural_disaster"], ["loss_location"]),
        ("Was the damage caused by a landslide or rockfall?",
         "damage_areas", 2, ["natural_disaster"], ["damage_areas"]),
        ("Was a cyclone or tornado responsible for the vehicle damage?",
         "weather_condition", 2, ["natural_disaster"], ["weather_condition"]),
        ("Was the vehicle damage covered under a government-notified calamity scheme?",
         "loss_location_city", 3, ["natural_disaster"], ["loss_location"]),
        ("Were multiple vehicles damaged by the same natural disaster event?",
         "witnesses_present", 3, ["natural_disaster"], ["witnesses_present"]),
        ("Was the vehicle in transit when the natural disaster occurred?",
         "vehicle_moving_status", 3, ["natural_disaster"], ["vehicle_moving_status"]),
        ("Was any advance warning issued before the natural disaster?",
         "loss_datetime", 3, ["natural_disaster"], ["loss_datetime"]),
        ("Were public authorities involved in the rescue of the vehicle?",
         "fire_brigade_called", 4, ["natural_disaster"], ["fire_brigade_called"]),
        ("Was an act of God declaration issued for the area?",
         "loss_location_city", 3, ["natural_disaster"], ["loss_location"]),
        ("Was the vehicle parked in a safe zone during the natural disaster?",
         "loss_location_road_type", 3, ["natural_disaster"], ["loss_location"]),
        ("Was the roof of the parking structure damaged and fell on the vehicle?",
         "damage_areas_roof", 3, ["natural_disaster"], ["damage_areas"]),
        ("Were any agricultural fields or farm equipment involved in the damage?",
         "vehicle_usage_type", 4, ["natural_disaster"], ["vehicle_usage_type"]),
        ("Was the vehicle evacuated to a safe location before the disaster?",
         "vehicle_moving_status", 4, ["natural_disaster"], ["vehicle_moving_status"]),
        ("Were photographs taken of the natural disaster scene and vehicle?",
         "evidence_photos_available", 3, ["natural_disaster"], ["evidence_photos_available"]),
        ("Is the area still inaccessible due to the natural disaster?",
         "loss_location_city", 4, ["natural_disaster"], ["loss_location"]),
    ]
    for text, field, priority, it_list, fills in nd_qs:
        qs.append(q(text, field, priority, {"incident_type": it_list}, fills, "natural_disaster_specific"))
    return qs

def generate_all_extended():
    qs = []
    generators = [
        ("damage_zone_expanded",        gen_damage_zone_expanded),
        ("incident_timeline",           gen_incident_timeline),
        ("documentation_checklist",     gen_documentation_checklist),
        ("driver_details",              gen_driver_details),
        ("collision_scenario_matrix",   gen_collision_scenario_matrix),
        ("fraud_expanded",              gen_fraud_expanded),
        ("settlement_expanded",         gen_settlement_expanded),
        ("theft_expanded",              gen_theft_expanded),
        ("fire_expanded",               gen_fire_expanded),
        ("flood_expanded",              gen_flood_expanded),
        ("vandalism_expanded",          gen_vandalism_expanded),
        ("natural_disaster_specific",   gen_natural_disaster_specific),
    ]
    for name, gen in generators:
        batch = gen()
        qs.extend(batch)
        print(f"  [{name}] generated {len(batch)} questions")
    return qs

if __name__ == "__main__":
    last_id = get_last_id(BASE_PATH)
    set_start(last_id)
    print(f"Starting IDs from Q{last_id+1:04d}")

    print("Generating extension questions...")
    ext_qs = generate_all_extended()
    print(f"\nExtension questions: {len(ext_qs)}")

    with open(BASE_PATH, "a", encoding="utf-8") as f:
        for q_obj in ext_qs:
            f.write(json.dumps(q_obj, ensure_ascii=False) + "\n")

    total = 0
    with open(BASE_PATH) as f:
        for _ in f:
            total += 1
    print(f"Total questions in bank: {total}")

    from collections import Counter
    cats = Counter()
    with open(BASE_PATH) as f:
        for line in f:
            obj = json.loads(line)
            cats[obj["category_tag"]] += 1
    print("\nFinal category breakdown:")
    for cat, count in sorted(cats.items()):
        print(f"  {cat}: {count}")
