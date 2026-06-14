import json
import itertools
import hashlib
import os
from typing import List, Dict, Any

OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "question_bank_raw.jsonl")

QUESTIONS: List[Dict[str, Any]] = []
_id_counter = [1]

def make_q(text: str, field: str, priority: int, triggers: dict, fill_fields: list, category_tag: str) -> dict:
    qid = f"Q{_id_counter[0]:04d}"
    _id_counter[0] += 1
    return {
        "id": qid,
        "text": text,
        "question_field": field,
        "priority": priority,
        "category_tag": category_tag,
        "triggers": triggers,
        "targets": {"fill_fields": fill_fields}
    }

def gen_incident_basics():
    qs = []

    time_questions = [
        ("What date and time did the incident occur?", "loss_datetime", 2,
         {"incident_type": ["collision","hit_and_run","theft","fire","flood","vandalism","self_accident","rollover","collision_wall","collision_animal","theft_attempted","natural_disaster"]},
         ["loss_datetime"]),
        ("Can you confirm the exact date the incident happened?", "loss_datetime", 2,
         {"incident_type": ["collision","hit_and_run","theft","fire","flood","vandalism","self_accident","rollover"]},
         ["loss_datetime"]),
        ("What time of day did the incident take place?", "loss_datetime", 2,
         {"incident_type": ["collision","hit_and_run","fire","flood","vandalism","self_accident","rollover","collision_wall"]},
         ["loss_datetime"]),
        ("Was the incident during the day or at night?", "loss_datetime", 3,
         {"incident_type": ["collision","hit_and_run","self_accident","rollover","collision_wall"]},
         ["loss_datetime"]),
        ("Approximately what hour did the accident occur?", "loss_datetime", 3,
         {"incident_type": ["collision","hit_and_run","self_accident","rollover"]},
         ["loss_datetime"]),
    ]
    for text, field, priority, triggers, fills in time_questions:
        qs.append(make_q(text, field, priority, triggers, fills, "incident_basics"))

    location_questions = [
        ("In which city did the incident occur?", "loss_location_city", 2,
         {"incident_type": ["collision","hit_and_run","theft","fire","flood","vandalism","self_accident","rollover","collision_wall","natural_disaster"]},
         ["loss_location"]),
        ("What is the exact location or landmark where the incident happened?", "loss_location_landmark", 2,
         {"incident_type": ["collision","hit_and_run","self_accident","rollover","collision_wall","fire","flood"]},
         ["loss_location"]),
        ("What type of road were you on — highway, urban road, or rural?", "loss_location_road_type", 2,
         {"incident_type": ["collision","hit_and_run","self_accident","rollover","collision_wall"]},
         ["loss_location"]),
        ("Was the vehicle on a flyover or expressway when the incident occurred?", "loss_location_road_type", 3,
         {"incident_type": ["collision","hit_and_run","self_accident","rollover"]},
         ["loss_location"]),
        ("Were you in a parking lot or a private property area when it happened?", "loss_location_road_type", 3,
         {"incident_type": ["collision","theft","vandalism","collision_wall"]},
         ["loss_location"]),
        ("What was the name of the road or area where the incident happened?", "loss_location_road_name", 3,
         {"incident_type": ["collision","hit_and_run","self_accident","fire","flood"]},
         ["loss_location"]),
        ("Which state did the incident occur in?", "loss_location_state", 3,
         {"incident_type": ["collision","theft","fire","flood","vandalism","natural_disaster"]},
         ["loss_location"]),
    ]
    for text, field, priority, triggers, fills in location_questions:
        qs.append(make_q(text, field, priority, triggers, fills, "incident_basics"))

    moving_questions = [
        ("Was your vehicle moving or parked at the time of the incident?", "vehicle_moving_status", 2,
         {"incident_type": ["collision","vandalism","theft","collision_wall","hit_and_run"]},
         ["vehicle_moving_status"]),
        ("Was the vehicle stationary at a traffic signal when it was hit?", "vehicle_moving_status", 3,
         {"incident_type": ["collision","hit_and_run"]},
         ["vehicle_moving_status"]),
        ("Was the vehicle parked on the roadside or in a designated parking area?", "vehicle_moving_status", 3,
         {"incident_type": ["vandalism","theft","collision"]},
         ["vehicle_moving_status"]),
        ("Was the engine running at the time of the incident?", "vehicle_moving_status", 3,
         {"incident_type": ["theft","fire","collision"]},
         ["vehicle_moving_status"]),
    ]
    for text, field, priority, triggers, fills in moving_questions:
        qs.append(make_q(text, field, priority, triggers, fills, "incident_basics"))

    weather_questions = [
        ("What were the weather conditions at the time of the incident?", "weather_condition", 3,
         {"incident_type": ["collision","hit_and_run","self_accident","rollover","flood","natural_disaster"]},
         ["weather_condition"]),
        ("Was it raining when the incident occurred?", "weather_condition", 3,
         {"incident_type": ["collision","hit_and_run","self_accident","flood"]},
         ["weather_condition"]),
        ("Was there fog or low visibility at the time of the accident?", "weather_condition", 3,
         {"incident_type": ["collision","hit_and_run","self_accident","rollover"]},
         ["weather_condition"]),
        ("How was the visibility on the road at the time of the incident?", "weather_condition", 3,
         {"incident_type": ["collision","hit_and_run","self_accident","rollover"]},
         ["weather_condition"]),
        ("Was there any dust storm or extreme weather at the time?", "weather_condition", 4,
         {"incident_type": ["collision","natural_disaster","flood"]},
         ["weather_condition"]),
    ]
    for text, field, priority, triggers, fills in weather_questions:
        qs.append(make_q(text, field, priority, triggers, fills, "incident_basics"))

    road_qs = [
        ("What was the road condition — wet, dry, or under construction?", "road_condition", 3,
         {"incident_type": ["collision","hit_and_run","self_accident","rollover","flood"]},
         ["road_condition"]),
        ("Were there any potholes or road hazards where the incident happened?", "road_condition", 4,
         {"incident_type": ["collision","self_accident","rollover"]},
         ["road_condition"]),
        ("Was the road surface slippery at the time of the incident?", "road_condition", 3,
         {"incident_type": ["collision","self_accident","rollover"]},
         ["road_condition"]),
        ("Were there any speed breakers or road dividers involved in the accident?", "road_condition", 4,
         {"incident_type": ["collision","self_accident","rollover","collision_wall"]},
         ["road_condition"]),
    ]
    for text, field, priority, triggers, fills in road_qs:
        qs.append(make_q(text, field, priority, triggers, fills, "incident_basics"))

    injury_qs = [
        ("Was anyone injured in the incident?", "injury_reported", 1,
         {"incident_type": ["collision","hit_and_run","fire","rollover","self_accident","natural_disaster"]},
         ["injury_reported"]),
        ("Were you or any passengers injured during the accident?", "injury_reported", 1,
         {"incident_type": ["collision","hit_and_run","self_accident","rollover","fire"]},
         ["injury_reported"]),
        ("Was the third party or any bystander injured?", "injury_reported", 1,
         {"incident_type": ["collision","hit_and_run"], "third_party_involved": True},
         ["injury_reported"]),
        ("Have you or any injured person received medical attention?", "injury_details", 2,
         {"incident_type": ["collision","hit_and_run","fire","rollover"], "required_fields_present": ["injury_reported"]},
         ["injury_details"]),
        ("What is the nature of the injuries sustained?", "injury_details", 2,
         {"incident_type": ["collision","hit_and_run","fire","rollover"], "required_fields_present": ["injury_reported"]},
         ["injury_details"]),
    ]
    for text, field, priority, triggers, fills in injury_qs:
        qs.append(make_q(text, field, priority, triggers, fills, "incident_basics"))

    witness_qs = [
        ("Were there any witnesses to the incident?", "witnesses_present", 3,
         {"incident_type": ["collision","hit_and_run","vandalism","fire"]},
         ["witnesses_present"]),
        ("Did any bystanders or other drivers witness the accident?", "witnesses_present", 3,
         {"incident_type": ["collision","hit_and_run","self_accident","rollover"]},
         ["witnesses_present"]),
        ("Can you provide contact details of any witnesses?", "witness_contact", 4,
         {"incident_type": ["collision","hit_and_run","vandalism"], "required_fields_present": ["witnesses_present"]},
         ["witness_contact"]),
        ("Are any witnesses willing to provide a statement?", "witness_contact", 4,
         {"incident_type": ["collision","hit_and_run"], "required_fields_present": ["witnesses_present"]},
         ["witness_contact"]),
    ]
    for text, field, priority, triggers, fills in witness_qs:
        qs.append(make_q(text, field, priority, triggers, fills, "incident_basics"))

    misc_qs = [
        ("Can you briefly describe what happened in your own words?", "category", 2,
         {"incident_type": ["collision","hit_and_run","theft","fire","flood","vandalism","self_accident","rollover"]},
         ["category"]),
        ("Was this the first time this vehicle has been involved in an incident?", "previous_claims", 2,
         {"incident_type": ["collision","theft","fire","flood","vandalism","self_accident","rollover","hit_and_run"]},
         ["previous_claims"]),
        ("Has this vehicle had any previous insurance claims filed?", "previous_claims", 2,
         {"incident_type": ["collision","theft","fire","flood","vandalism"]},
         ["previous_claims"]),
        ("How many previous claims have been filed for this vehicle in the last 3 years?", "previous_claims", 2,
         {"incident_type": ["collision","theft","fire","flood","vandalism","self_accident"]},
         ["previous_claims"]),
        ("Was this incident reported to the insurance company immediately?", "loss_datetime", 3,
         {"incident_type": ["collision","theft","fire","flood","vandalism","hit_and_run"]},
         ["loss_datetime"]),
        ("How long after the incident are you filing this claim?", "loss_datetime", 3,
         {"incident_type": ["collision","theft","fire","flood","vandalism"]},
         ["loss_datetime"]),
    ]
    for text, field, priority, triggers, fills in misc_qs:
        qs.append(make_q(text, field, priority, triggers, fills, "incident_basics"))

    return qs

def gen_collision_dynamics():
    qs = []

    impact_qs = [
        ("From which direction was your vehicle hit?", "impact_direction", 2,
         {"incident_type": ["collision","hit_and_run"]},
         ["impact_direction"]),
        ("Was the impact from the front, rear, or side?", "impact_direction", 2,
         {"incident_type": ["collision","hit_and_run"]},
         ["impact_direction"]),
        ("Was it a head-on collision?", "impact_direction", 2,
         {"incident_type": ["collision"]},
         ["impact_direction"]),
        ("Was the vehicle hit from the left side or the right side?", "impact_direction", 3,
         {"incident_type": ["collision","hit_and_run"]},
         ["impact_direction"]),
        ("Was the impact at the front bumper, rear bumper, or door?", "impact_direction", 3,
         {"incident_type": ["collision"]},
         ["impact_direction"]),
        ("Did the vehicle roll over during the accident?", "impact_direction", 2,
         {"incident_type": ["collision","rollover","self_accident"]},
         ["impact_direction"]),
        ("Was there a side swipe or a direct collision?", "impact_direction", 3,
         {"incident_type": ["collision"]},
         ["impact_direction"]),
        ("Were multiple impact points involved?", "impact_direction", 3,
         {"incident_type": ["collision"]},
         ["impact_direction"]),
    ]
    for text, field, priority, triggers, fills in impact_qs:
        qs.append(make_q(text, field, priority, triggers, fills, "collision_dynamics"))

    speed_qs = [
        ("At what approximate speed was your vehicle travelling at the time of impact?", "speed_estimate", 3,
         {"incident_type": ["collision","hit_and_run","self_accident","rollover"]},
         ["speed_estimate"]),
        ("Was the vehicle travelling at low speed (under 20 km/h) or higher speed?", "speed_estimate", 3,
         {"incident_type": ["collision","self_accident","rollover"]},
         ["speed_estimate"]),
        ("Would you estimate the impact speed as low, medium (20–60 km/h), or high (above 60 km/h)?", "speed_estimate", 3,
         {"incident_type": ["collision","self_accident","rollover"]},
         ["speed_estimate"]),
        ("Was the vehicle braking at the time of the collision?", "speed_estimate", 3,
         {"incident_type": ["collision","self_accident"]},
         ["speed_estimate"]),
        ("Was the vehicle accelerating when the accident occurred?", "speed_estimate", 4,
         {"incident_type": ["collision","self_accident"]},
         ["speed_estimate"]),
    ]
    for text, field, priority, triggers, fills in speed_qs:
        qs.append(make_q(text, field, priority, triggers, fills, "collision_dynamics"))

    lane_qs = [
        ("What lane were you driving in when the accident occurred?", "lane_action", 3,
         {"incident_type": ["collision","hit_and_run","self_accident"]},
         ["lane_action"]),
        ("Were you changing lanes at the time of the collision?", "lane_action", 3,
         {"incident_type": ["collision","self_accident"]},
         ["lane_action"]),
        ("Were you overtaking another vehicle when the incident happened?", "lane_action", 3,
         {"incident_type": ["collision","self_accident","rollover"]},
         ["lane_action"]),
        ("Were you turning left or right at the point of impact?", "lane_action", 3,
         {"incident_type": ["collision","hit_and_run","self_accident"]},
         ["lane_action"]),
        ("Were you driving straight or navigating a bend when the collision happened?", "lane_action", 3,
         {"incident_type": ["collision","self_accident","rollover"]},
         ["lane_action"]),
        ("Was the vehicle merging onto a highway when the accident occurred?", "lane_action", 4,
         {"incident_type": ["collision","self_accident"]},
         ["lane_action"]),
        ("Were you on a one-way road or a two-way road?", "lane_action", 4,
         {"incident_type": ["collision","hit_and_run","self_accident"]},
         ["lane_action"]),
        ("Were you in the correct lane at the time of the accident?", "lane_action", 3,
         {"incident_type": ["collision","self_accident"]},
         ["lane_action"]),
    ]
    for text, field, priority, triggers, fills in lane_qs:
        qs.append(make_q(text, field, priority, triggers, fills, "collision_dynamics"))

    signal_qs = [
        ("Was there a traffic signal at the point of impact?", "signal_compliance", 3,
         {"incident_type": ["collision","hit_and_run"]},
         ["signal_compliance"]),
        ("What was the signal status when the accident occurred — red, green, or amber?", "signal_compliance", 3,
         {"incident_type": ["collision","hit_and_run"]},
         ["signal_compliance"]),
        ("Did you have the right of way at the time of the collision?", "signal_compliance", 3,
         {"incident_type": ["collision","hit_and_run"]},
         ["signal_compliance"]),
        ("Was the other vehicle running a red light when it collided with yours?", "signal_compliance", 3,
         {"incident_type": ["collision","hit_and_run"], "third_party_involved": True},
         ["signal_compliance"]),
        ("Were there any traffic signs or road markings at the accident location?", "signal_compliance", 4,
         {"incident_type": ["collision","self_accident"]},
         ["signal_compliance"]),
        ("Did you have the signal or indicator on when the accident happened?", "signal_compliance", 4,
         {"incident_type": ["collision","self_accident"]},
         ["signal_compliance"]),
    ]
    for text, field, priority, triggers, fills in signal_qs:
        qs.append(make_q(text, field, priority, triggers, fills, "collision_dynamics"))

    collision_misc = [
        ("Was your vehicle involved in a rear-end collision?", "impact_direction", 2,
         {"incident_type": ["collision","hit_and_run"]}, ["impact_direction"]),
        ("Did your vehicle skid before the collision?", "road_condition", 3,
         {"incident_type": ["collision","self_accident","rollover"]}, ["road_condition"]),
        ("Did you apply emergency brakes before impact?", "speed_estimate", 3,
         {"incident_type": ["collision","self_accident"]}, ["speed_estimate"]),
        ("Was the collision at an intersection or mid-road?", "loss_location_road_type", 3,
         {"incident_type": ["collision","hit_and_run"]}, ["loss_location"]),
        ("Were there any traffic cones or diversions at the accident spot?", "road_condition", 4,
         {"incident_type": ["collision","self_accident"]}, ["road_condition"]),
        ("Did your vehicle hit a road divider?", "impact_direction", 3,
         {"incident_type": ["collision_wall","collision","self_accident"]}, ["impact_direction"]),
        ("Did any tyre burst contribute to the accident?", "road_condition", 3,
         {"incident_type": ["collision","rollover","self_accident"]}, ["road_condition"]),
        ("Was there any mechanical failure before the accident?", "road_condition", 3,
         {"incident_type": ["collision","rollover","self_accident","fire"]}, ["road_condition"]),
        ("Did you lose control of the vehicle before the impact?", "lane_action", 3,
         {"incident_type": ["collision","rollover","self_accident"]}, ["lane_action"]),
        ("How many vehicles were involved in the collision?", "third_party_involved", 2,
         {"incident_type": ["collision","hit_and_run"]}, ["third_party_involved"]),
        ("Was your vehicle stationary when it was hit from behind?", "vehicle_moving_status", 3,
         {"incident_type": ["collision","hit_and_run"]}, ["vehicle_moving_status"]),
        ("Was the other vehicle an automobile, motorcycle, or heavy vehicle?", "third_party_vehicle_id", 3,
         {"incident_type": ["collision","hit_and_run"], "third_party_involved": True}, ["third_party_vehicle_id"]),
        ("Was your vehicle being overtaken when the collision occurred?", "lane_action", 4,
         {"incident_type": ["collision"]}, ["lane_action"]),
        ("Were there any construction vehicles or trucks involved?", "third_party_vehicle_id", 3,
         {"incident_type": ["collision"], "third_party_involved": True}, ["third_party_vehicle_id"]),
        ("Was your vehicle parked on the road when hit?", "vehicle_moving_status", 3,
         {"incident_type": ["collision","hit_and_run"]}, ["vehicle_moving_status"]),
        ("What was the approximate speed of the other vehicle at impact?", "speed_estimate", 4,
         {"incident_type": ["collision","hit_and_run"], "third_party_involved": True}, ["speed_estimate"]),
        ("Were pedestrians involved in or near the accident?", "injury_reported", 2,
         {"incident_type": ["collision","hit_and_run"]}, ["injury_reported"]),
        ("Was the road undivided or had a central median?", "loss_location_road_type", 4,
         {"incident_type": ["collision","self_accident"]}, ["loss_location"]),
        ("Did oncoming traffic contribute to the accident?", "lane_action", 3,
         {"incident_type": ["collision","self_accident"]}, ["lane_action"]),
        ("Was there a U-turn involved in the collision?", "lane_action", 4,
         {"incident_type": ["collision","self_accident"]}, ["lane_action"]),
        ("Was the collision with a stationary vehicle?", "impact_direction", 3,
         {"incident_type": ["collision","collision_wall"]}, ["impact_direction"]),
        ("Was the collision with a moving vehicle?", "impact_direction", 3,
         {"incident_type": ["collision","hit_and_run"]}, ["impact_direction"]),
        ("Were there any animals on the road that caused the accident?", "road_condition", 3,
         {"incident_type": ["collision_animal","self_accident"]}, ["road_condition"]),
        ("Was the accident due to sudden braking by the vehicle in front?", "lane_action", 3,
         {"incident_type": ["collision"]}, ["lane_action"]),
        ("Were any traffic bollards or barriers struck?", "impact_direction", 4,
         {"incident_type": ["collision_wall","self_accident"]}, ["impact_direction"]),
        ("Was your vehicle towing anything at the time of the accident?", "vehicle_moving_status", 4,
         {"incident_type": ["collision","self_accident","rollover"]}, ["vehicle_moving_status"]),
        ("Was the highway lighting adequate at the time of the accident?", "weather_condition", 4,
         {"incident_type": ["collision","hit_and_run","self_accident"]}, ["weather_condition"]),
        ("Did the accident occur near a school zone or hospital zone?", "loss_location_road_type", 4,
         {"incident_type": ["collision","self_accident"]}, ["loss_location"]),
        ("Were you on a service road when the accident occurred?", "loss_location_road_type", 4,
         {"incident_type": ["collision","self_accident"]}, ["loss_location"]),
        ("Was the vehicle loaded beyond normal capacity?", "vehicle_moving_status", 4,
         {"incident_type": ["collision","rollover","self_accident"]}, ["vehicle_moving_status"]),
    ]
    for text, field, priority, triggers, fills in collision_misc:
        qs.append(make_q(text, field, priority, triggers, fills, "collision_dynamics"))

    return qs

def gen_damage_assessment():
    qs = []

    zones = [
        "front bumper", "rear bumper", "left front door", "left rear door",
        "right front door", "right rear door", "hood", "boot lid", "roof",
        "front windshield", "rear windshield", "left headlamp", "right headlamp",
        "left tail lamp", "right tail lamp", "left fender", "right fender",
        "left quarter panel", "right quarter panel", "underbody", "engine bay",
        "fuel tank area"
    ]
    zone_fields = [
        "damage_areas_front_bumper", "damage_areas_rear_bumper", "damage_areas_left_door_front",
        "damage_areas_left_door_rear", "damage_areas_right_door_front", "damage_areas_right_door_rear",
        "damage_areas_hood", "damage_areas_boot", "damage_areas_roof",
        "damage_areas_windshield_front", "damage_areas_windshield_rear", "damage_areas_left_headlamp",
        "damage_areas_right_headlamp", "damage_areas_left_tail_lamp", "damage_areas_right_tail_lamp",
        "damage_areas_left_fender", "damage_areas_right_fender", "damage_areas_left_quarter",
        "damage_areas_right_quarter", "damage_areas_underbody", "damage_areas_engine",
        "damage_areas_fuel_tank"
    ]
    for zone, zf in zip(zones, zone_fields):
        qs.append(make_q(
            f"Was the {zone} damaged in the incident?",
            zf, 3,
            {"incident_type": ["collision","hit_and_run","self_accident","rollover","vandalism","fire","flood","collision_wall","collision_animal","natural_disaster"]},
            ["damage_areas"],
            "damage_assessment"
        ))
        qs.append(make_q(
            f"How severe is the damage to the {zone}? (minor / moderate / severe)",
            "damage_severity", 3,
            {"incident_type": ["collision","hit_and_run","self_accident","rollover","vandalism","fire","flood","collision_wall","natural_disaster"],
             "required_fields_present": ["damage_areas"]},
            ["damage_severity"],
            "damage_assessment"
        ))

    overall_qs = [
        ("Which parts of the vehicle are visibly damaged?", "damage_areas", 2,
         {"incident_type": ["collision","hit_and_run","self_accident","rollover","vandalism","fire","flood","collision_wall","natural_disaster"]},
         ["damage_areas"]),
        ("What is the overall extent of the damage — minor, moderate, severe, or total loss?", "damage_severity", 2,
         {"incident_type": ["collision","hit_and_run","self_accident","rollover","vandalism","fire","flood","collision_wall","natural_disaster"]},
         ["damage_severity"]),
        ("Is the vehicle still drivable after the incident?", "drivable", 2,
         {"incident_type": ["collision","hit_and_run","self_accident","rollover","fire","flood","vandalism","collision_wall","natural_disaster"]},
         ["drivable"]),
        ("Was the vehicle towed away from the accident site?", "vehicle_towed", 2,
         {"incident_type": ["collision","hit_and_run","self_accident","rollover","fire","flood","collision_wall"]},
         ["vehicle_towed"]),
        ("Were any airbags deployed during the incident?", "airbags_deployed", 2,
         {"incident_type": ["collision","hit_and_run","self_accident","rollover","collision_wall"]},
         ["airbags_deployed"]),
        ("Was the windshield cracked or shattered?", "damage_areas_windshield", 3,
         {"incident_type": ["collision","hit_and_run","vandalism","self_accident","rollover","natural_disaster"]},
         ["damage_areas"]),
        ("Was the underbody or chassis of the vehicle damaged?", "damage_areas_underbody", 3,
         {"incident_type": ["collision","self_accident","rollover","flood","collision_wall"]},
         ["damage_areas"]),
        ("Were any tyres burst or punctured?", "damage_areas_tyre", 3,
         {"incident_type": ["collision","self_accident","rollover","vandalism","natural_disaster"]},
         ["damage_areas"]),
        ("Are any door panels damaged or unable to open/close?", "damage_areas_door", 3,
         {"incident_type": ["collision","hit_and_run","vandalism","self_accident"]},
         ["damage_areas"]),
        ("Was the engine or mechanical components visibly damaged?", "damage_areas_engine", 3,
         {"incident_type": ["collision","fire","flood","rollover","self_accident"]},
         ["damage_areas"]),
        ("Can you describe all visible damage on the exterior of the vehicle?", "damage_areas", 2,
         {"incident_type": ["collision","hit_and_run","vandalism","self_accident","rollover","collision_wall","natural_disaster"]},
         ["damage_areas"]),
        ("Is there any interior damage to the vehicle?", "damage_areas", 3,
         {"incident_type": ["collision","fire","flood","vandalism","rollover"]},
         ["damage_areas"]),
        ("Were any electronic or dashboard components damaged?", "damage_areas", 4,
         {"incident_type": ["collision","fire","flood","rollover"]},
         ["damage_areas"]),
        ("Is there any damage to the suspension or steering?", "damage_areas_suspension", 3,
         {"incident_type": ["collision","self_accident","rollover","flood","collision_wall"]},
         ["damage_areas"]),
        ("Was the fuel tank damaged or leaking?", "damage_areas_fuel_tank", 3,
         {"incident_type": ["collision","fire","rollover","self_accident"]},
         ["damage_areas"]),
        ("Were the front or rear lights completely destroyed?", "damage_areas_headlamp", 3,
         {"incident_type": ["collision","hit_and_run","vandalism","collision_wall"]},
         ["damage_areas"]),
        ("Is the damage limited to one side or spread across multiple areas?", "damage_areas", 3,
         {"incident_type": ["collision","hit_and_run","vandalism","rollover"]},
         ["damage_areas"]),
        ("Was the vehicle roof crushed or deformed?", "damage_areas_roof", 3,
         {"incident_type": ["rollover","collision","natural_disaster"]},
         ["damage_areas"]),
        ("Does the vehicle require immediate repair to be legally driveable?", "drivable", 2,
         {"incident_type": ["collision","hit_and_run","self_accident","vandalism","flood","fire"]},
         ["drivable"]),
        ("Were the number plates damaged or missing after the incident?", "damage_areas", 4,
         {"incident_type": ["collision","hit_and_run","vandalism"]},
         ["damage_areas"]),
    ]
    for text, field, priority, triggers, fills in overall_qs:
        qs.append(make_q(text, field, priority, triggers, fills, "damage_assessment"))

    return qs

def gen_third_party_details():
    qs = []

    base_qs = [
        ("Was any other vehicle involved in the incident?", "third_party_involved", 2,
         {"incident_type": ["collision","hit_and_run"]}, ["third_party_involved"]),
        ("Was the other vehicle's registration number captured (photo or notes)?", "third_party_details_registration", 2,
         {"incident_type": ["collision","hit_and_run"], "third_party_involved": True}, ["third_party_vehicle_id"]),
        ("What is the registration number of the third-party vehicle?", "third_party_vehicle_id", 2,
         {"incident_type": ["collision","hit_and_run"], "third_party_involved": True}, ["third_party_vehicle_id"]),
        ("Did you exchange contact details with the other driver?", "third_party_contact", 2,
         {"incident_type": ["collision"], "third_party_involved": True}, ["third_party_contact"]),
        ("What is the other driver's name?", "third_party_driver_name", 3,
         {"incident_type": ["collision"], "third_party_involved": True}, ["third_party_driver_name"]),
        ("What is the other driver's contact number?", "third_party_contact", 3,
         {"incident_type": ["collision"], "third_party_involved": True}, ["third_party_contact"]),
        ("Do you know the insurance company of the third-party vehicle?", "third_party_insurer", 3,
         {"incident_type": ["collision"], "third_party_involved": True}, ["third_party_insurer"]),
        ("Was the third party's vehicle also damaged?", "third_party_involved", 3,
         {"incident_type": ["collision"], "third_party_involved": True}, ["third_party_involved"]),
        ("Did the other driver admit fault at the scene?", "third_party_driver_name", 3,
         {"incident_type": ["collision"], "third_party_involved": True}, ["third_party_driver_name"]),
        ("Was the third party a motorcycle, car, bus, or truck?", "third_party_vehicle_id", 3,
         {"incident_type": ["collision","hit_and_run"], "third_party_involved": True}, ["third_party_vehicle_id"]),
        ("Was it a hit-and-run — did the other vehicle flee the scene?", "hit_and_run", 2,
         {"incident_type": ["collision","hit_and_run"]}, ["hit_and_run"]),
        ("Did you manage to note down any partial registration number of the fleeing vehicle?", "third_party_vehicle_id", 3,
         {"incident_type": ["hit_and_run"]}, ["third_party_vehicle_id"]),
        ("Was there any CCTV camera near the accident spot that may have captured the other vehicle?", "evidence_video_available", 3,
         {"incident_type": ["collision","hit_and_run"], "third_party_involved": True}, ["evidence_video_available"]),
        ("Did the third party have a valid driving licence?", "third_party_driver_name", 4,
         {"incident_type": ["collision"], "third_party_involved": True}, ["third_party_driver_name"]),
        ("Was the other driver under the influence of alcohol or substances?", "third_party_driver_name", 3,
         {"incident_type": ["collision"],"third_party_involved": True}, ["third_party_driver_name"]),
        ("Was a mutually agreed settlement made at the scene without a police report?", "police_report_filed", 3,
         {"incident_type": ["collision"], "third_party_involved": True}, ["police_report_filed"]),
        ("Was the other vehicle a commercial vehicle (taxi, truck, auto-rickshaw)?", "third_party_vehicle_id", 3,
         {"incident_type": ["collision"], "third_party_involved": True}, ["third_party_vehicle_id"]),
        ("Was the third-party driver the owner of the vehicle?", "third_party_driver_name", 4,
         {"incident_type": ["collision"], "third_party_involved": True}, ["third_party_driver_name"]),
        ("Did you receive any written acknowledgement from the third party at the scene?", "third_party_contact", 4,
         {"incident_type": ["collision"], "third_party_involved": True}, ["third_party_contact"]),
        ("What make and model was the third-party vehicle?", "third_party_vehicle_id", 4,
         {"incident_type": ["collision","hit_and_run"], "third_party_involved": True}, ["third_party_vehicle_id"]),
        ("What colour was the other vehicle involved?", "third_party_vehicle_id", 4,
         {"incident_type": ["collision","hit_and_run"], "third_party_involved": True}, ["third_party_vehicle_id"]),
        ("Was the other vehicle insured at the time of the accident?", "third_party_insurer", 3,
         {"incident_type": ["collision"], "third_party_involved": True}, ["third_party_insurer"]),
        ("Do you have a photo of the other vehicle or its number plate?", "evidence_photos_available", 3,
         {"incident_type": ["collision","hit_and_run"], "third_party_involved": True}, ["evidence_photos_available"]),
        ("Was the third party's vehicle stationary when hit?", "vehicle_moving_status", 4,
         {"incident_type": ["collision"], "third_party_involved": True}, ["vehicle_moving_status"]),
        ("Has the third party filed a complaint against you?", "police_report_filed", 3,
         {"incident_type": ["collision"], "third_party_involved": True}, ["police_report_filed"]),
        ("Did the third party receive any immediate medical attention?", "injury_reported", 2,
         {"incident_type": ["collision","hit_and_run"], "third_party_involved": True}, ["injury_reported"]),
        ("Was the other vehicle also towed from the accident spot?", "vehicle_towed", 4,
         {"incident_type": ["collision"], "third_party_involved": True}, ["vehicle_towed"]),
        ("Was the third party a government vehicle or emergency service vehicle?", "third_party_vehicle_id", 4,
         {"incident_type": ["collision"], "third_party_involved": True}, ["third_party_vehicle_id"]),
        ("Did you attempt to contact the third party after the incident?", "third_party_contact", 4,
         {"incident_type": ["collision"], "third_party_involved": True}, ["third_party_contact"]),
        ("Was a spot survey or accident sketch prepared at the scene?", "evidence_photos_available", 4,
         {"incident_type": ["collision"], "third_party_involved": True}, ["evidence_photos_available"]),
        ("Did any traffic police officer visit the scene and record the details?", "police_report_filed", 3,
         {"incident_type": ["collision","hit_and_run"]}, ["police_report_filed"]),
        ("Were multiple vehicles involved in the collision (chain accident)?", "third_party_vehicle_id", 3,
         {"incident_type": ["collision"]}, ["third_party_vehicle_id"]),
        ("Is the third party likely to make a claim against you?", "third_party_insurer", 3,
         {"incident_type": ["collision"], "third_party_involved": True}, ["third_party_insurer"]),
        ("Did you or the third party call any roadside assistance?", "towing_required", 4,
         {"incident_type": ["collision"], "third_party_involved": True}, ["towing_required"]),
        ("Has the third party given you any written demand for compensation?", "third_party_contact", 4,
         {"incident_type": ["collision"], "third_party_involved": True}, ["third_party_contact"]),
    ]
    for text, field, priority, triggers, fills in base_qs:
        qs.append(make_q(text, field, priority, triggers, fills, "third_party_details"))

    return qs

def gen_legal_reporting():
    qs = []

    legal_qs = [
        ("Was a police report or FIR filed after the incident?", "police_report_filed", 2,
         {"incident_type": ["collision","hit_and_run","theft","fire","vandalism","flood","self_accident","rollover","natural_disaster"]},
         ["police_report_filed"]),
        ("What is the FIR number or case number?", "fir_number", 2,
         {"incident_type": ["collision","hit_and_run","theft","fire","vandalism"],
          "required_fields_present": ["police_report_filed"]}, ["fir_number"]),
        ("At which police station was the report filed?", "police_station", 3,
         {"incident_type": ["collision","hit_and_run","theft","fire","vandalism"],
          "required_fields_present": ["police_report_filed"]}, ["police_station"]),
        ("Was the incident handled privately without involving the police?", "police_report_filed", 3,
         {"incident_type": ["collision","vandalism"]}, ["police_report_filed"]),
        ("Was the FIR filed on the same day as the incident?", "fir_number", 3,
         {"incident_type": ["collision","hit_and_run","theft","fire","vandalism"],
          "required_fields_present": ["police_report_filed"]}, ["fir_number"]),
        ("Do you have a copy of the FIR or police report?", "fir_number", 3,
         {"incident_type": ["collision","hit_and_run","theft","fire","vandalism"],
          "required_fields_present": ["police_report_filed"]}, ["fir_number"]),
        ("Was the traffic police notified about the accident?", "police_report_filed", 3,
         {"incident_type": ["collision","hit_and_run","rollover"]}, ["police_report_filed"]),
        ("Have you received a copy of the police report?", "police_report_filed", 4,
         {"incident_type": ["collision","hit_and_run","theft","fire"],
          "required_fields_present": ["police_report_filed"]}, ["police_report_filed"]),
        ("Were any traffic challans issued at the scene?", "fir_number", 4,
         {"incident_type": ["collision","hit_and_run"]}, ["fir_number"]),
        ("Was the incident recorded by traffic cameras?", "evidence_video_available", 3,
         {"incident_type": ["collision","hit_and_run","self_accident"]}, ["evidence_video_available"]),
        ("Do you have any photographs of the accident scene?", "evidence_photos_available", 2,
         {"incident_type": ["collision","hit_and_run","self_accident","vandalism","fire","flood","rollover","collision_wall","natural_disaster"]},
         ["evidence_photos_available"]),
        ("Do you have any video footage from a dashcam?", "dashcam_available", 3,
         {"incident_type": ["collision","hit_and_run","self_accident"]}, ["dashcam_available"]),
        ("Is there CCTV footage available from the area of the incident?", "evidence_video_available", 3,
         {"incident_type": ["collision","hit_and_run","theft","vandalism"]}, ["evidence_video_available"]),
        ("Have you taken photos of all damaged parts of the vehicle?", "evidence_photos_available", 3,
         {"incident_type": ["collision","hit_and_run","fire","flood","vandalism","self_accident","rollover","natural_disaster"]},
         ["evidence_photos_available"]),
        ("Do you have a copy of the repair estimate from the workshop?", "evidence_photos_available", 4,
         {"incident_type": ["collision","hit_and_run","vandalism","fire","flood","self_accident"]},
         ["evidence_photos_available"]),
        ("Has a spot survey been conducted by any insurance representative?", "evidence_photos_available", 4,
         {"incident_type": ["collision","fire","flood","theft","vandalism","self_accident"]},
         ["evidence_photos_available"]),
        ("Were any media or news cameras present at the accident location?", "evidence_video_available", 5,
         {"incident_type": ["collision","hit_and_run","fire","flood"]}, ["evidence_video_available"]),
        ("Do you have the contact details of the investigating officer?", "police_station", 4,
         {"incident_type": ["collision","hit_and_run","theft","fire"],
          "required_fields_present": ["police_report_filed"]}, ["police_station"]),
        ("Was your vehicle impounded by the police after the accident?", "vehicle_towed", 3,
         {"incident_type": ["collision","hit_and_run","rollover"]}, ["vehicle_towed"]),
        ("Were any notices or summons received from the court related to this incident?", "fir_number", 4,
         {"incident_type": ["collision","hit_and_run"]}, ["fir_number"]),
        ("Has any legal case been filed against you in connection with this incident?", "fir_number", 3,
         {"incident_type": ["collision","hit_and_run"]}, ["fir_number"]),
        ("Were any breathalyser tests or sobriety checks conducted by police?", "police_report_filed", 3,
         {"incident_type": ["collision","hit_and_run"]}, ["police_report_filed"]),
        ("Was an independent accident reconstruction report prepared?", "evidence_photos_available", 5,
         {"incident_type": ["collision","rollover","hit_and_run"]}, ["evidence_photos_available"]),
        ("Has the police released your vehicle from custody?", "vehicle_towed", 4,
         {"incident_type": ["collision","hit_and_run","theft"]}, ["vehicle_towed"]),
        ("Was any mutual agreement or compromise signed at the police station?", "police_station", 4,
         {"incident_type": ["collision"], "third_party_involved": True}, ["police_station"]),
    ]
    for text, field, priority, triggers, fills in legal_qs:
        qs.append(make_q(text, field, priority, triggers, fills, "legal_reporting"))

    return qs

def gen_policy_eligibility():
    qs = []

    policy_qs = [
        ("Is your vehicle insurance policy currently active?", "policy_active", 1,
         {"incident_type": ["collision","theft","fire","flood","vandalism","hit_and_run","self_accident","rollover","natural_disaster","collision_wall","collision_animal"]},
         ["policy_active"]),
        ("What is your insurance policy number?", "policy_number", 2,
         {"incident_type": ["collision","theft","fire","flood","vandalism","hit_and_run","self_accident","rollover","natural_disaster"]},
         ["policy_number"]),
        ("What type of insurance cover do you have — third party only or comprehensive?", "coverage_type", 2,
         {"incident_type": ["collision","theft","fire","flood","vandalism","hit_and_run","self_accident","rollover","natural_disaster"]},
         ["coverage_type"]),
        ("Is the person driving the vehicle the policy holder?", "driver_is_owner", 2,
         {"incident_type": ["collision","theft","fire","flood","vandalism","hit_and_run","self_accident","rollover"]},
         ["driver_is_owner"]),
        ("What is the driver's relationship to the vehicle owner?", "driver_relationship", 3,
         {"incident_type": ["collision","theft","fire","vandalism","hit_and_run","self_accident"],
          "required_fields_present": ["driver_is_owner"]}, ["driver_relationship"]),
        ("Does the driver have a valid driving licence?", "driver_license_valid", 2,
         {"incident_type": ["collision","theft","fire","vandalism","hit_and_run","self_accident","rollover"]},
         ["driver_license_valid"]),
        ("What is the vehicle's usage type — personal or commercial?", "vehicle_usage_type", 2,
         {"incident_type": ["collision","theft","fire","flood","vandalism","self_accident","rollover","natural_disaster"]},
         ["vehicle_usage_type"]),
        ("Is the vehicle registered as a commercial taxi or cab?", "vehicle_usage_type", 2,
         {"incident_type": ["collision","theft","fire","vandalism","self_accident"]},
         ["vehicle_usage_type"]),
        ("When does your current insurance policy expire?", "policy_active", 3,
         {"incident_type": ["collision","theft","fire","flood","vandalism","natural_disaster"]},
         ["policy_active"]),
        ("Do you have a zero-depreciation add-on cover?", "add_ons", 4,
         {"incident_type": ["collision","vandalism","fire","flood","natural_disaster","self_accident"]},
         ["add_ons"]),
        ("Do you have a roadside assistance add-on?", "add_ons", 5,
         {"incident_type": ["collision","self_accident","flood","natural_disaster"]},
         ["add_ons"]),
        ("Do you have an engine protection add-on?", "add_ons", 4,
         {"incident_type": ["flood","fire","self_accident","collision"]},
         ["add_ons"]),
        ("Do you have an invoice cover add-on?", "add_ons", 5,
         {"incident_type": ["theft","collision","fire","flood","natural_disaster"]},
         ["add_ons"]),
        ("Were you driving the vehicle with the owner's permission?", "driver_is_owner", 2,
         {"incident_type": ["collision","theft","fire","vandalism","self_accident"]},
         ["driver_is_owner"]),
        ("Is the vehicle being used within the geographical limits of the policy?", "policy_active", 3,
         {"incident_type": ["collision","theft","fire","flood","vandalism","natural_disaster"]},
         ["policy_active"]),
        ("Did the policy exclude any specific exclusions that may apply?", "coverage_type", 3,
         {"incident_type": ["collision","theft","fire","flood","vandalism","natural_disaster"]},
         ["coverage_type"]),
        ("Is the vehicle's RC (Registration Certificate) valid?", "driver_license_valid", 3,
         {"incident_type": ["collision","theft","fire","flood","vandalism","self_accident","rollover"]},
         ["driver_license_valid"]),
        ("Does the policy cover damages in this specific incident category?", "coverage_type", 3,
         {"incident_type": ["collision","theft","fire","flood","vandalism","natural_disaster"]},
         ["coverage_type"]),
        ("Was the vehicle being used for hire or reward at the time?", "vehicle_usage_type", 3,
         {"incident_type": ["collision","theft","vandalism","self_accident"]},
         ["vehicle_usage_type"]),
        ("Was the policy transferred from a previous owner?", "policy_number", 4,
         {"incident_type": ["collision","theft","fire","flood","vandalism","natural_disaster"]},
         ["policy_number"]),
        ("Is there any No Claim Bonus (NCB) on your current policy?", "policy_number", 4,
         {"incident_type": ["collision","theft","fire","flood","vandalism","natural_disaster"]},
         ["policy_number"]),
        ("Is this vehicle registered as a school bus or education institution vehicle?", "vehicle_usage_type", 4,
         {"incident_type": ["collision","vandalism","theft","fire"]},
         ["vehicle_usage_type"]),
        ("Was the vehicle being driven by a learner with a valid learner's licence?", "driver_license_valid", 3,
         {"incident_type": ["collision","self_accident","rollover"]},
         ["driver_license_valid"]),
        ("Is the vehicle registered under an individual name or a company?", "driver_is_owner", 4,
         {"incident_type": ["collision","theft","fire","flood","vandalism","natural_disaster"]},
         ["driver_is_owner"]),
        ("Were any modifications made to the vehicle that could affect insurance coverage?", "vehicle_usage_type", 3,
         {"incident_type": ["collision","theft","fire","flood","vandalism","self_accident","rollover"]},
         ["vehicle_usage_type"]),
        ("Is the NCB protect add-on active on this policy?", "add_ons", 5,
         {"incident_type": ["collision","theft","fire","flood","vandalism","natural_disaster"]},
         ["add_ons"]),
        ("Was the tyre protection add-on active at the time of the incident?", "add_ons", 5,
         {"incident_type": ["collision","self_accident","rollover","vandalism"]},
         ["add_ons"]),
        ("Is the key replacement add-on active?", "add_ons", 5,
         {"incident_type": ["theft","vandalism"]},
         ["add_ons"]),
    ]
    for text, field, priority, triggers, fills in policy_qs:
        qs.append(make_q(text, field, priority, triggers, fills, "policy_eligibility"))

    return qs

def gen_fraud_consistency():
    qs = []

    fraud_qs = [
        ("Is the timeline of events you've described consistent with the date stated?", "previous_claims", 1,
         {"incident_type": ["collision","theft","fire","flood","vandalism","hit_and_run","self_accident","rollover","natural_disaster"]},
         ["previous_claims"]),
        ("Have there been any claims filed for this vehicle in the past 12 months?", "previous_claims", 1,
         {"incident_type": ["collision","theft","fire","flood","vandalism","self_accident","rollover","natural_disaster"]},
         ["previous_claims"]),
        ("Has this vehicle been reported stolen and recovered before?", "previous_claims", 1,
         {"incident_type": ["theft","theft_attempted"]},
         ["previous_claims"]),
        ("Was any part of the damage pre-existing before this incident?", "damage_severity", 2,
         {"incident_type": ["collision","vandalism","fire","flood","natural_disaster","self_accident","rollover"]},
         ["damage_severity"]),
        ("Is the damage consistent with the type of incident you described?", "damage_severity", 2,
         {"incident_type": ["collision","vandalism","fire","flood","natural_disaster","self_accident"]},
         ["damage_severity"]),
        ("Was there a total loss claim filed for this vehicle previously?", "previous_claims", 1,
         {"incident_type": ["collision","theft","fire","flood","natural_disaster","rollover"]},
         ["previous_claims"]),
        ("Are the damages declared consistent with the reported collision direction?", "impact_direction", 2,
         {"incident_type": ["collision","hit_and_run"], "required_fields_present": ["damage_areas"]},
         ["impact_direction"]),
        ("Was the vehicle recently purchased before this incident?", "previous_claims", 2,
         {"incident_type": ["theft","fire","flood","vandalism","natural_disaster"]},
         ["previous_claims"]),
        ("Has the vehicle been involved in more than one accident in this policy year?", "previous_claims", 1,
         {"incident_type": ["collision","hit_and_run","self_accident","rollover"]},
         ["previous_claims"]),
        ("Is the vehicle under a loan or hypothecation?", "policy_number", 3,
         {"incident_type": ["theft","collision","fire","flood","natural_disaster"]},
         ["policy_number"]),
        ("Were any modifications or alterations made to the vehicle recently?", "vehicle_usage_type", 2,
         {"incident_type": ["collision","theft","fire","flood","vandalism","natural_disaster","self_accident","rollover"]},
         ["vehicle_usage_type"]),
        ("Is the estimated repair cost significantly higher than the vehicle's market value?", "damage_severity", 2,
         {"incident_type": ["collision","fire","flood","natural_disaster","self_accident","rollover"]},
         ["damage_severity"]),
        ("Were the keys in the vehicle at the time it was reported stolen?", "theft_keys_available", 1,
         {"incident_type": ["theft"]}, ["theft_keys_available"]),
        ("Was the vehicle fitted with any anti-theft device?", "theft_tracking_device", 2,
         {"incident_type": ["theft","theft_attempted"]}, ["theft_tracking_device"]),
        ("Is the claimed loss amount consistent with the vehicle's current market value?", "damage_severity", 2,
         {"incident_type": ["collision","theft","fire","flood","natural_disaster"]},
         ["damage_severity"]),
        ("Have you recently increased the insurance cover or add-ons before this claim?", "add_ons", 2,
         {"incident_type": ["theft","fire","flood","collision","natural_disaster","vandalism"]},
         ["add_ons"]),
        ("Were there any disputes about vehicle ownership in the past?", "driver_is_owner", 2,
         {"incident_type": ["theft","collision","fire","flood","vandalism","natural_disaster"]},
         ["driver_is_owner"]),
        ("Does the FIR timeline match the reported incident time?", "fir_number", 1,
         {"incident_type": ["collision","hit_and_run","theft","fire","vandalism"],
          "required_fields_present": ["police_report_filed"]}, ["fir_number"]),
        ("Are the photos of damage consistent with the location and type of incident described?", "evidence_photos_available", 2,
         {"incident_type": ["collision","vandalism","fire","flood","natural_disaster"]},
         ["evidence_photos_available"]),
        ("Was the vehicle insured continuously without any lapse in the past 3 years?", "policy_active", 2,
         {"incident_type": ["collision","theft","fire","flood","vandalism","natural_disaster"]},
         ["policy_active"]),
        ("Were there any recent financial difficulties reported by the policy holder?", "previous_claims", 2,
         {"incident_type": ["theft","fire","flood","collision","vandalism","natural_disaster"]},
         ["previous_claims"]),
        ("Was the incident reported significantly later than it occurred?", "loss_datetime", 1,
         {"incident_type": ["collision","theft","fire","flood","vandalism","natural_disaster","self_accident","rollover","hit_and_run"]},
         ["loss_datetime"]),
        ("Is the accident location in an unusual or remote area?", "loss_location_road_type", 2,
         {"incident_type": ["collision","theft","fire","vandalism","self_accident"]},
         ["loss_location"]),
        ("Were there any discrepancies in the information provided across multiple calls?", "previous_claims", 1,
         {"incident_type": ["collision","theft","fire","flood","vandalism","natural_disaster","self_accident","rollover"]},
         ["previous_claims"]),
        ("Was the vehicle serviced or repaired recently before the incident?", "damage_severity", 3,
         {"incident_type": ["collision","fire","flood","self_accident","rollover"]},
         ["damage_severity"]),
    ]
    for text, field, priority, triggers, fills in fraud_qs:
        qs.append(make_q(text, field, priority, triggers, fills, "fraud_consistency"))

    return qs

def gen_repair_settlement():
    qs = []

    repair_qs = [
        ("Do you prefer cashless repair at a network garage or reimbursement?", "settlement_preference", 4,
         {"incident_type": ["collision","hit_and_run","vandalism","fire","flood","self_accident","rollover","collision_wall","natural_disaster"]},
         ["settlement_preference"]),
        ("Which workshop or garage do you want to take the vehicle to?", "repair_preference", 4,
         {"incident_type": ["collision","hit_and_run","vandalism","fire","flood","self_accident","rollover","collision_wall","natural_disaster"]},
         ["repair_preference"]),
        ("Is there a preferred network garage near you?", "repair_preference", 5,
         {"incident_type": ["collision","hit_and_run","vandalism","fire","flood","self_accident","rollover","collision_wall","natural_disaster"]},
         ["repair_preference"]),
        ("Do you need towing assistance to move the vehicle to the workshop?", "towing_required", 3,
         {"incident_type": ["collision","hit_and_run","fire","flood","self_accident","rollover","natural_disaster"]},
         ["towing_required"]),
        ("Has the vehicle already been moved to a workshop?", "repair_preference", 4,
         {"incident_type": ["collision","vandalism","fire","flood","self_accident","rollover","natural_disaster"]},
         ["repair_preference"]),
        ("Have you received a repair estimate from the workshop?", "evidence_photos_available", 4,
         {"incident_type": ["collision","vandalism","fire","flood","self_accident","rollover","natural_disaster"]},
         ["evidence_photos_available"]),
        ("Would you like us to arrange a cashless garage near your current location?", "repair_preference", 5,
         {"incident_type": ["collision","hit_and_run","vandalism","fire","flood","self_accident","rollover"]},
         ["repair_preference"]),
        ("Has any repair work been started on the vehicle?", "repair_preference", 4,
         {"incident_type": ["collision","vandalism","fire","flood","self_accident","rollover","natural_disaster"]},
         ["repair_preference"]),
        ("Was the towing done by a roadside assistance provider?", "towing_required", 4,
         {"incident_type": ["collision","fire","flood","self_accident","rollover","natural_disaster"]},
         ["towing_required"]),
        ("Do you have a towing receipt or bill?", "towing_required", 5,
         {"incident_type": ["collision","fire","flood","self_accident","rollover","natural_disaster"]},
         ["towing_required"]),
        ("Would you prefer an authorised dealership for repairs?", "repair_preference", 5,
         {"incident_type": ["collision","vandalism","fire","flood","self_accident","rollover","natural_disaster"]},
         ["repair_preference"]),
        ("Are you willing to have an insurance surveyor inspect the vehicle before repair?", "repair_preference", 3,
         {"incident_type": ["collision","vandalism","fire","flood","self_accident","rollover","natural_disaster","hit_and_run"]},
         ["repair_preference"]),
        ("Can you share the location of the damaged vehicle for survey scheduling?", "loss_location_city", 3,
         {"incident_type": ["collision","fire","flood","vandalism","self_accident","rollover","natural_disaster"]},
         ["loss_location"]),
        ("Do you want the consumables covered under your add-on plan?", "add_ons", 5,
         {"incident_type": ["collision","vandalism","fire","flood","self_accident","rollover","natural_disaster"]},
         ["add_ons"]),
        ("Do you want to use your zero-depreciation add-on for this claim?", "add_ons", 4,
         {"incident_type": ["collision","vandalism","fire","flood","self_accident","rollover","natural_disaster"]},
         ["add_ons"]),
        ("When would you be available for a vehicle inspection?", "repair_preference", 5,
         {"incident_type": ["collision","vandalism","fire","flood","self_accident","rollover","natural_disaster","hit_and_run"]},
         ["repair_preference"]),
        ("Has the workshop given you an estimated number of days for repair completion?", "repair_preference", 5,
         {"incident_type": ["collision","vandalism","fire","flood","self_accident","rollover","natural_disaster"]},
         ["repair_preference"]),
        ("Would you like a rental vehicle while yours is being repaired?", "add_ons", 5,
         {"incident_type": ["collision","fire","flood","self_accident","rollover","natural_disaster","hit_and_run"]},
         ["add_ons"]),
        ("Is the workshop requesting a payment upfront before starting repairs?", "repair_preference", 4,
         {"incident_type": ["collision","vandalism","fire","flood","self_accident","rollover","natural_disaster"]},
         ["repair_preference"]),
        ("Have you already paid for any repairs out of pocket?", "settlement_preference", 4,
         {"incident_type": ["collision","vandalism","fire","flood","self_accident","rollover","natural_disaster"]},
         ["settlement_preference"]),
        ("Do you want to raise an emergency towing request right now?", "towing_required", 3,
         {"incident_type": ["collision","fire","flood","self_accident","rollover","natural_disaster"]},
         ["towing_required"]),
        ("Is engine protection add-on applicable for this claim?", "add_ons", 4,
         {"incident_type": ["flood","fire","self_accident","collision"]},
         ["add_ons"]),
        ("Do you have an active roadside assistance add-on we can activate?", "add_ons", 4,
         {"incident_type": ["collision","fire","flood","self_accident","rollover","natural_disaster"]},
         ["add_ons"]),
        ("Is there a No Claim Bonus at risk with this claim?", "policy_number", 4,
         {"incident_type": ["collision","theft","fire","flood","vandalism","natural_disaster","self_accident","rollover"]},
         ["policy_number"]),
        ("Would you like to protect your NCB by opting for a voluntary deductible?", "add_ons", 5,
         {"incident_type": ["collision","theft","fire","flood","vandalism","natural_disaster","self_accident","rollover"]},
         ["add_ons"]),
    ]
    for text, field, priority, triggers, fills in repair_qs:
        qs.append(make_q(text, field, priority, triggers, fills, "repair_settlement"))

    return qs

def gen_theft_specific():
    qs = []

    theft_qs = [
        ("When did you first notice that the vehicle was missing?", "loss_datetime", 2,
         {"incident_type": ["theft","theft_attempted"]}, ["loss_datetime"]),
        ("Where was the vehicle parked when it was stolen?", "loss_location_city", 2,
         {"incident_type": ["theft"]}, ["loss_location"]),
        ("Were the keys left inside the vehicle when it was stolen?", "theft_keys_available", 1,
         {"incident_type": ["theft"]}, ["theft_keys_available"]),
        ("Do you have all sets of keys for the vehicle?", "theft_keys_available", 2,
         {"incident_type": ["theft"]}, ["theft_keys_available"]),
        ("How many sets of keys does this vehicle have, and where are they?", "theft_keys_available", 2,
         {"incident_type": ["theft"]}, ["theft_keys_available"]),
        ("Was there any forced entry on the vehicle (broken windows, tampered locks)?", "theft_forced_entry", 2,
         {"incident_type": ["theft","theft_attempted"]}, ["theft_forced_entry"]),
        ("Was the steering lock active when the vehicle was parked?", "theft_forced_entry", 3,
         {"incident_type": ["theft"]}, ["theft_forced_entry"]),
        ("Was a vehicle tracking device or GPS installed?", "theft_tracking_device", 2,
         {"incident_type": ["theft"]}, ["theft_tracking_device"]),
        ("Has the tracking device triggered any alerts?", "theft_tracking_device", 2,
         {"incident_type": ["theft"], "required_fields_present": ["theft_tracking_device"]},
         ["theft_tracking_device"]),
        ("Was the vehicle parked in a guarded or unguarded area?", "loss_location_road_type", 3,
         {"incident_type": ["theft"]}, ["loss_location"]),
        ("Was there a security camera at the parking location?", "evidence_video_available", 3,
         {"incident_type": ["theft"]}, ["evidence_video_available"]),
        ("Did you report the theft to the police within 24 hours?", "police_report_filed", 1,
         {"incident_type": ["theft"]}, ["police_report_filed"]),
        ("Has the vehicle been recovered since the theft was reported?", "drivable", 2,
         {"incident_type": ["theft"]}, ["drivable"]),
        ("Was the vehicle recovered in a damaged condition?", "damage_severity", 2,
         {"incident_type": ["theft"], "required_fields_present": ["drivable"]}, ["damage_severity"]),
        ("Were any personal belongings stolen from the vehicle along with it?", "theft_forced_entry", 4,
         {"incident_type": ["theft"]}, ["theft_forced_entry"]),
        ("Was an anti-theft alarm system installed in the vehicle?", "theft_tracking_device", 3,
         {"incident_type": ["theft","theft_attempted"]}, ["theft_tracking_device"]),
        ("Were the windows of the vehicle closed and doors locked before theft?", "theft_forced_entry", 3,
         {"incident_type": ["theft"]}, ["theft_forced_entry"]),
        ("Did any neighbour or security guard witness the theft?", "witnesses_present", 3,
         {"incident_type": ["theft"]}, ["witnesses_present"]),
        ("Was the vehicle stolen from your residential address?", "loss_location_city", 3,
         {"incident_type": ["theft"]}, ["loss_location"]),
        ("Was the RC book or any document left inside the stolen vehicle?", "theft_forced_entry", 4,
         {"incident_type": ["theft"]}, ["theft_forced_entry"]),
        ("Was the theft from a public parking lot or a commercial area?", "loss_location_road_type", 3,
         {"incident_type": ["theft"]}, ["loss_location"]),
        ("Was the vehicle stolen during the day or night?", "loss_datetime", 3,
         {"incident_type": ["theft"]}, ["loss_datetime"]),
        ("Was the vehicle on a loan at the time of theft?", "policy_number", 3,
         {"incident_type": ["theft"]}, ["policy_number"]),
        ("Have you submitted the keys and RC book to the police?", "theft_keys_available", 3,
         {"incident_type": ["theft"], "required_fields_present": ["police_report_filed"]}, ["theft_keys_available"]),
        ("Was there any additional cover for accessories or electronics in the vehicle?", "add_ons", 4,
         {"incident_type": ["theft"]}, ["add_ons"]),
        ("Was the vehicle marked with any anti-theft identifiers?", "theft_tracking_device", 4,
         {"incident_type": ["theft","theft_attempted"]}, ["theft_tracking_device"]),
        ("Did anyone contact you offering to return the vehicle for a fee?", "theft_forced_entry", 2,
         {"incident_type": ["theft"]}, ["theft_forced_entry"]),
        ("Has the police found any leads or CCTV footage related to the theft?", "evidence_video_available", 4,
         {"incident_type": ["theft"]}, ["evidence_video_available"]),
    ]
    for text, field, priority, triggers, fills in theft_qs:
        qs.append(make_q(text, field, priority, triggers, fills, "theft_specific"))

    return qs

def gen_fire_specific():
    qs = []

    fire_qs = [
        ("What was the source or cause of the fire?", "fire_source", 2,
         {"incident_type": ["fire"]}, ["fire_source"]),
        ("Was the fire caused by an electrical fault or engine overheating?", "fire_source", 2,
         {"incident_type": ["fire"]}, ["fire_source"]),
        ("Did the fire start inside or outside the vehicle?", "fire_source", 2,
         {"incident_type": ["fire"]}, ["fire_source"]),
        ("Was the fire brigade called to the scene?", "fire_brigade_called", 2,
         {"incident_type": ["fire"]}, ["fire_brigade_called"]),
        ("Do you have the fire brigade report or call record?", "fire_brigade_called", 3,
         {"incident_type": ["fire"], "required_fields_present": ["fire_brigade_called"]}, ["fire_brigade_called"]),
        ("Was the vehicle completely gutted in the fire?", "damage_severity", 2,
         {"incident_type": ["fire"]}, ["damage_severity"]),
        ("What percentage of the vehicle is estimated to be damaged by fire?", "damage_severity", 2,
         {"incident_type": ["fire"]}, ["damage_severity"]),
        ("Was fuel leakage a reason for the fire?", "fire_source", 3,
         {"incident_type": ["fire"]}, ["fire_source"]),
        ("Was the vehicle engine running when the fire started?", "vehicle_moving_status", 3,
         {"incident_type": ["fire"]}, ["vehicle_moving_status"]),
        ("Was the fire caused by an external source (arson, nearby burning material)?", "fire_source", 2,
         {"incident_type": ["fire","vandalism"]}, ["fire_source"]),
        ("Were any flammable materials stored in the vehicle?", "fire_source", 3,
         {"incident_type": ["fire"]}, ["fire_source"]),
        ("Were any people inside the vehicle when the fire broke out?", "injury_reported", 1,
         {"incident_type": ["fire"]}, ["injury_reported"]),
        ("Was a short circuit or wiring issue the cause of the fire?", "fire_source", 3,
         {"incident_type": ["fire"]}, ["fire_source"]),
        ("Did the fire spread to the fuel tank?", "damage_areas_fuel_tank", 3,
         {"incident_type": ["fire"]}, ["damage_areas"]),
        ("Was the CNG or LPG kit in the vehicle a contributing factor?", "fire_source", 3,
         {"incident_type": ["fire"]}, ["fire_source"]),
        ("Was the fire an intentional act (arson)?", "fire_source", 1,
         {"incident_type": ["fire"]}, ["fire_source"]),
        ("Was the vehicle modified to run on alternative fuel before the fire?", "vehicle_usage_type", 3,
         {"incident_type": ["fire"]}, ["vehicle_usage_type"]),
        ("Were neighbours or bystanders injured in the fire?", "injury_reported", 1,
         {"incident_type": ["fire"]}, ["injury_reported"]),
        ("Did any explosion occur during the fire?", "damage_severity", 2,
         {"incident_type": ["fire"]}, ["damage_severity"]),
        ("Was the fire reported to the local authorities?", "police_report_filed", 2,
         {"incident_type": ["fire"]}, ["police_report_filed"]),
        ("Were the airbags deployed during the fire?", "airbags_deployed", 3,
         {"incident_type": ["fire"]}, ["airbags_deployed"]),
        ("Was the vehicle fitted with a fire extinguisher?", "fire_source", 4,
         {"incident_type": ["fire"]}, ["fire_source"]),
        ("Was the fire extinguished naturally or by external help?", "fire_brigade_called", 3,
         {"incident_type": ["fire"]}, ["fire_brigade_called"]),
        ("Were any recent electrical modifications done on the vehicle?", "fire_source", 3,
         {"incident_type": ["fire"]}, ["fire_source"]),
        ("Was the engine recently serviced before the fire incident?", "fire_source", 4,
         {"incident_type": ["fire"]}, ["fire_source"]),
        ("Was the fire covered under the comprehensive insurance policy?", "coverage_type", 3,
         {"incident_type": ["fire"]}, ["coverage_type"]),
        ("Is an engine protection cover active for this claim?", "add_ons", 3,
         {"incident_type": ["fire"]}, ["add_ons"]),
        ("Was the fire a result of a collision?", "category", 2,
         {"incident_type": ["fire"]}, ["category"]),
    ]
    for text, field, priority, triggers, fills in fire_qs:
        qs.append(make_q(text, field, priority, triggers, fills, "fire_specific"))

    return qs

def gen_flood_specific():
    qs = []

    flood_qs = [
        ("Was the vehicle submerged or partially flooded?", "flood_water_level", 2,
         {"incident_type": ["flood","natural_disaster"]}, ["flood_water_level"]),
        ("How high was the water level — above tyre level, door level, or fully submerged?", "flood_water_level", 2,
         {"incident_type": ["flood","natural_disaster"]}, ["flood_water_level"]),
        ("Was the engine cranked or started after the flood exposure?", "flood_engine_cranked", 1,
         {"incident_type": ["flood","natural_disaster"]}, ["flood_engine_cranked"]),
        ("Was the water inside the vehicle cabin?", "flood_water_level", 2,
         {"incident_type": ["flood","natural_disaster"]}, ["flood_water_level"]),
        ("Did the flood water reach the engine compartment?", "flood_water_level", 2,
         {"incident_type": ["flood","natural_disaster"]}, ["flood_water_level"]),
        ("Was the vehicle parked in a flood-prone area?", "loss_location_road_type", 3,
         {"incident_type": ["flood","natural_disaster"]}, ["loss_location"]),
        ("Was the flooding caused by heavy rainfall or an overflowing water body?", "flood_water_level", 3,
         {"incident_type": ["flood","natural_disaster"]}, ["flood_water_level"]),
        ("How long was the vehicle submerged in water?", "flood_water_level", 3,
         {"incident_type": ["flood","natural_disaster"]}, ["flood_water_level"]),
        ("Was the vehicle driven into a flooded road before it got stuck?", "vehicle_moving_status", 2,
         {"incident_type": ["flood","natural_disaster"]}, ["vehicle_moving_status"]),
        ("Was this a government-declared flood area?", "loss_location_city", 3,
         {"incident_type": ["flood","natural_disaster"]}, ["loss_location"]),
        ("Were any interior electronics or dashboard systems damaged by the water?", "damage_areas", 3,
         {"incident_type": ["flood","natural_disaster"]}, ["damage_areas"]),
        ("Was the air intake of the engine exposed to flood water?", "flood_engine_cranked", 2,
         {"incident_type": ["flood","natural_disaster"]}, ["flood_engine_cranked"]),
        ("Was the vehicle recovered and towed after the flood?", "vehicle_towed", 3,
         {"incident_type": ["flood","natural_disaster"]}, ["vehicle_towed"]),
        ("Do you have any authority certificate or flood zone notification?", "evidence_photos_available", 4,
         {"incident_type": ["flood","natural_disaster"]}, ["evidence_photos_available"]),
        ("Was the underbody and exhaust system damaged due to the flood?", "damage_areas_underbody", 3,
         {"incident_type": ["flood","natural_disaster"]}, ["damage_areas"]),
        ("Was silt or debris deposited inside the engine or cabin?", "flood_water_level", 3,
         {"incident_type": ["flood","natural_disaster"]}, ["flood_water_level"]),
        ("Was the transmission affected by the flood water?", "damage_areas_engine", 3,
         {"incident_type": ["flood","natural_disaster"]}, ["damage_areas"]),
        ("Were the electrical systems completely non-functional after the flood?", "damage_areas", 3,
         {"incident_type": ["flood","natural_disaster"]}, ["damage_areas"]),
        ("Did you attempt to start the vehicle after the water receded?", "flood_engine_cranked", 2,
         {"incident_type": ["flood","natural_disaster"]}, ["flood_engine_cranked"]),
        ("Was an engine protection add-on active at the time of this flood incident?", "add_ons", 3,
         {"incident_type": ["flood","natural_disaster"]}, ["add_ons"]),
        ("Was the vehicle brought in from another location during the flood?", "loss_location_city", 4,
         {"incident_type": ["flood","natural_disaster"]}, ["loss_location"]),
        ("Is the flood a one-time occurrence or a recurring event in the area?", "loss_location_city", 4,
         {"incident_type": ["flood","natural_disaster"]}, ["loss_location"]),
        ("Were any other vehicles in your vicinity also damaged by the flood?", "witnesses_present", 4,
         {"incident_type": ["flood","natural_disaster"]}, ["witnesses_present"]),
        ("Was the fuel tank contaminated with flood water?", "damage_areas_fuel_tank", 3,
         {"incident_type": ["flood","natural_disaster"]}, ["damage_areas"]),
        ("Was there any damage to the brake system due to flood exposure?", "damage_areas_suspension", 3,
         {"incident_type": ["flood","natural_disaster"]}, ["damage_areas"]),
        ("Were tyres or rims damaged due to being submerged?", "damage_areas", 4,
         {"incident_type": ["flood","natural_disaster"]}, ["damage_areas"]),
        ("Were any structural components rusted or warped due to flood exposure?", "damage_areas", 4,
         {"incident_type": ["flood","natural_disaster"]}, ["damage_areas"]),
    ]
    for text, field, priority, triggers, fills in flood_qs:
        qs.append(make_q(text, field, priority, triggers, fills, "flood_specific"))

    return qs

def gen_vandalism_specific():
    qs = []

    vandalism_qs = [
        ("What type of vandalism was done to the vehicle?", "vandalism_type", 2,
         {"incident_type": ["vandalism"]}, ["vandalism_type"]),
        ("Were any windows broken or windshield smashed?", "damage_areas_windshield", 2,
         {"incident_type": ["vandalism"]}, ["damage_areas"]),
        ("Were the tyres slashed or deflated?", "damage_areas_tyre", 2,
         {"incident_type": ["vandalism"]}, ["damage_areas"]),
        ("Were scratches or dents deliberately made on the body?", "vandalism_type", 2,
         {"incident_type": ["vandalism"]}, ["vandalism_type"]),
        ("Was the vehicle set on fire as an act of vandalism?", "fire_source", 2,
         {"incident_type": ["vandalism","fire"]}, ["fire_source"]),
        ("Were any accessories or parts stolen from the vehicle?", "theft_forced_entry", 2,
         {"incident_type": ["vandalism"]}, ["theft_forced_entry"]),
        ("Was the vehicle keyed or scratched with a sharp object?", "vandalism_type", 3,
         {"incident_type": ["vandalism"]}, ["vandalism_type"]),
        ("Were the headlamps or tail lamps broken?", "damage_areas_headlamp", 3,
         {"incident_type": ["vandalism"]}, ["damage_areas"]),
        ("Was the side mirror damaged or removed?", "damage_areas", 3,
         {"incident_type": ["vandalism"]}, ["damage_areas"]),
        ("Were any interior components damaged?", "damage_areas", 3,
         {"incident_type": ["vandalism"]}, ["damage_areas"]),
        ("Was the fuel cap removed or fuel stolen?", "vandalism_type", 3,
         {"incident_type": ["vandalism"]}, ["vandalism_type"]),
        ("Was the vehicle spray painted or had graffiti applied?", "vandalism_type", 3,
         {"incident_type": ["vandalism"]}, ["vandalism_type"]),
        ("Was the hood left open or engine tampered with?", "vandalism_type", 3,
         {"incident_type": ["vandalism"]}, ["vandalism_type"]),
        ("Was the vehicle targeted specifically or was it a random act?", "vandalism_type", 4,
         {"incident_type": ["vandalism"]}, ["vandalism_type"]),
        ("Was there any political or social unrest in the area on the day of vandalism?", "loss_location_city", 3,
         {"incident_type": ["vandalism"]}, ["loss_location"]),
        ("Were multiple vehicles in the area damaged at the same time?", "witnesses_present", 3,
         {"incident_type": ["vandalism"]}, ["witnesses_present"]),
        ("Was the vehicle under surveillance or in a monitored area?", "evidence_video_available", 3,
         {"incident_type": ["vandalism"]}, ["evidence_video_available"]),
        ("Do you suspect a known person of the vandalism?", "vandalism_type", 3,
         {"incident_type": ["vandalism"]}, ["vandalism_type"]),
        ("Was the vandalism done in broad daylight or during the night?", "loss_datetime", 3,
         {"incident_type": ["vandalism"]}, ["loss_datetime"]),
        ("Were any anti-vandalism stickers or markings on the vehicle?", "vandalism_type", 5,
         {"incident_type": ["vandalism"]}, ["vandalism_type"]),
        ("Was the number plate tampered with or removed?", "vandalism_type", 3,
         {"incident_type": ["vandalism"]}, ["vandalism_type"]),
        ("Was the wiper or antenna removed?", "damage_areas", 4,
         {"incident_type": ["vandalism"]}, ["damage_areas"]),
        ("Were wheel covers or hub caps stolen?", "damage_areas_tyre", 4,
         {"incident_type": ["vandalism"]}, ["damage_areas"]),
        ("Was the vehicle locked when the vandalism occurred?", "vehicle_moving_status", 3,
         {"incident_type": ["vandalism"]}, ["vehicle_moving_status"]),
        ("Was the stereo system or in-dash electronics stolen?", "vandalism_type", 3,
         {"incident_type": ["vandalism"]}, ["vandalism_type"]),
        ("Were seats or upholstery slashed inside the vehicle?", "damage_areas", 4,
         {"incident_type": ["vandalism"]}, ["damage_areas"]),
        ("Was the chassis number tampered with?", "vandalism_type", 3,
         {"incident_type": ["vandalism"]}, ["vandalism_type"]),
    ]
    for text, field, priority, triggers, fills in vandalism_qs:
        qs.append(make_q(text, field, priority, triggers, fills, "vandalism_specific"))

    return qs

def gen_vehicle_details():
    qs = []
    vehicle_qs = [
        ("What is the make and model of your vehicle?", "vehicle_details", 2,
         {"incident_type": ["collision","theft","fire","flood","vandalism","hit_and_run","self_accident","rollover","natural_disaster","collision_wall","collision_animal","theft_attempted"]},
         ["vehicle"]),
        ("What is the manufacturing year of your vehicle?", "vehicle_year", 3,
         {"incident_type": ["collision","theft","fire","flood","vandalism","hit_and_run","self_accident","rollover","natural_disaster","collision_wall"]},
         ["vehicle"]),
        ("What is the registration number of your vehicle?", "vehicle_registration", 2,
         {"incident_type": ["collision","theft","fire","flood","vandalism","hit_and_run","self_accident","rollover","natural_disaster","collision_wall","collision_animal"]},
         ["vehicle"]),
        ("What fuel type does your vehicle use — petrol, diesel, CNG, or electric?", "vehicle_fuel_type", 3,
         {"incident_type": ["collision","fire","flood","self_accident","rollover","natural_disaster"]},
         ["vehicle"]),
        ("What is the colour of your vehicle?", "vehicle_colour", 4,
         {"incident_type": ["collision","theft","vandalism","hit_and_run","self_accident"]},
         ["vehicle"]),
        ("Was the vehicle recently purchased (less than 1 year old)?", "vehicle_year", 3,
         {"incident_type": ["collision","theft","fire","flood","vandalism","natural_disaster"]},
         ["vehicle"]),
        ("What is the approximate current market value of the vehicle?", "damage_severity", 3,
         {"incident_type": ["collision","theft","fire","flood","vandalism","natural_disaster","self_accident","rollover"]},
         ["damage_severity"]),
        ("Is the vehicle an automatic or manual transmission?", "vehicle_details", 5,
         {"incident_type": ["collision","self_accident","rollover","fire","flood"]},
         ["vehicle"]),
        ("Was the vehicle fitted with a factory-fitted CNG or LPG kit?", "vehicle_fuel_type", 4,
         {"incident_type": ["fire","collision","flood"]},
         ["vehicle"]),
        ("Was the vehicle a high-end or luxury model?", "vehicle_details", 4,
         {"incident_type": ["theft","collision","fire","vandalism","natural_disaster"]},
         ["vehicle"]),
    ]
    for text, field, priority, triggers, fills in vehicle_qs:
        qs.append(make_q(text, field, priority, triggers, fills, "incident_basics"))
    return qs

def generate_all():
    all_questions = []
    generators = [
        gen_incident_basics,
        gen_collision_dynamics,
        gen_damage_assessment,
        gen_third_party_details,
        gen_legal_reporting,
        gen_policy_eligibility,
        gen_fraud_consistency,
        gen_repair_settlement,
        gen_theft_specific,
        gen_fire_specific,
        gen_flood_specific,
        gen_vandalism_specific,
        gen_vehicle_details,
    ]
    for gen in generators:
        qs = gen()
        all_questions.extend(qs)
        print(f"  [{gen.__name__}] generated {len(qs)} questions")
    return all_questions

def write_jsonl(questions, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for q in questions:
            f.write(json.dumps(q, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    print("Generating question corpus...")
    questions = generate_all()
    print(f"\nTotal questions generated: {len(questions)}")

    from collections import Counter
    cat_counts = Counter(q["category_tag"] for q in questions)
    print("\nCategory breakdown:")
    for cat, count in sorted(cat_counts.items()):
        print(f"  {cat}: {count}")

    write_jsonl(questions, OUT_PATH)
    print(f"\nWritten to: {OUT_PATH}")
