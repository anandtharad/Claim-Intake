import json, os

BASE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "question_bank_raw.jsonl")

def get_last_id(path):
    last = 0
    with open(path) as f:
        for line in f:
            num = int(json.loads(line)["id"][1:])
            if num > last: last = num
    return last

c = [0]
def set_start(n): c[0] = n
def mk(text, field, priority, it_list, fills, cat):
    c[0] += 1
    return {"id": f"Q{c[0]:04d}", "text": text, "question_field": field,
            "priority": priority, "category_tag": cat,
            "triggers": {"incident_type": it_list},
            "targets": {"fill_fields": fills}}

ALL = ["collision","collision_wall","collision_animal","hit_and_run","theft","theft_attempted","fire","flood","vandalism","natural_disaster","self_accident","rollover"]
COL = ["collision","hit_and_run","self_accident","rollover","collision_wall","collision_animal"]
DMG = ["collision","hit_and_run","self_accident","rollover","vandalism","fire","flood","collision_wall","natural_disaster","collision_animal"]

qs = []


tp_extra = [
    ("Did the third party provide their insurance policy details?","third_party_insurer",3,["collision"],["third_party_insurer"]),
    ("Was the third-party vehicle also towed away?","vehicle_towed",4,["collision"],["vehicle_towed"]),
    ("Was a legal notice received from the third party's insurer?","third_party_insurer",3,["collision"],["third_party_insurer"]),
    ("Did you receive any payment from the third party at the scene?","third_party_contact",3,["collision"],["third_party_contact"]),
    ("Did the third party flee before details could be exchanged?","hit_and_run",2,["collision","hit_and_run"],["hit_and_run"]),
    ("Was the third-party driver a minor?","third_party_driver_name",2,["collision"],["third_party_driver_name"]),
    ("Was the third-party vehicle travelling in the wrong lane?","lane_action",3,["collision"],["lane_action"]),
    ("Did the third party call police after the accident?","police_report_filed",3,["collision"],["police_report_filed"]),
    ("Did any third party sustain head or spinal injury?","injury_reported",1,["collision","hit_and_run"],["injury_reported"]),
    ("Was the third party driving a rental or leased vehicle?","third_party_vehicle_id",3,["collision"],["third_party_vehicle_id"]),
    ("Was the third-party vehicle carrying hazardous goods?","third_party_vehicle_id",3,["collision"],["third_party_vehicle_id"]),
    ("Has the third party made a claim for bodily injury?","third_party_insurer",3,["collision"],["third_party_insurer"]),
    ("Did you obtain a no-objection certificate from the third party?","third_party_contact",4,["collision"],["third_party_contact"]),
    ("Was the third party's vehicle insured with the same insurer?","third_party_insurer",4,["collision"],["third_party_insurer"]),
    ("Did the third party have a commercial vehicle insurance policy?","third_party_insurer",4,["collision"],["third_party_insurer"]),
    ("Was the third-party vehicle displaying valid registration plates?","third_party_vehicle_id",3,["collision","hit_and_run"],["third_party_vehicle_id"]),
    ("Did you take a video of the third-party vehicle at the scene?","evidence_video_available",3,["collision"],["evidence_video_available"]),
    ("Was the third party cooperative in sharing details?","third_party_contact",4,["collision"],["third_party_contact"]),
    ("Did any police officer independently record the third party's details?","police_station",3,["collision","hit_and_run"],["police_station"]),
    ("Is the third party disputing fault for the collision?","third_party_insurer",3,["collision"],["third_party_insurer"]),
    ("Was the third-party vehicle displaying a temporary registration?","third_party_vehicle_id",4,["collision","hit_and_run"],["third_party_vehicle_id"]),
    ("Did the third party admit driving under the influence?","third_party_driver_name",2,["collision"],["third_party_driver_name"]),
    ("Was the third party driving during their work hours or duty?","third_party_driver_name",4,["collision"],["third_party_driver_name"]),
    ("Did the third party have a passenger who was also injured?","injury_reported",2,["collision"],["injury_reported"]),
    ("Did you ask the third party for their driving licence at the scene?","third_party_driver_name",3,["collision"],["third_party_driver_name"]),
    ("Is the third party willing to share CCTV or dashcam footage?","evidence_video_available",4,["collision"],["evidence_video_available"]),
    ("Was the third-party vehicle an electric vehicle?","third_party_vehicle_id",4,["collision"],["third_party_vehicle_id"]),
    ("Were any animals injured in the collision with the third party?","injury_reported",3,["collision","collision_animal"],["injury_reported"]),
    ("Was the third-party vehicle stationary or moving at impact?","vehicle_moving_status",3,["collision"],["vehicle_moving_status"]),
    ("Did you and the third party agree on a fault determination at the scene?","third_party_contact",4,["collision"],["third_party_contact"]),
]
for t,f,p,it,fills in tp_extra:
    qs.append(mk(t,f,p,it,fills,"third_party_details"))


pol_extra = [
    ("Was the vehicle covered under a fleet insurance policy?","coverage_type",3,ALL,["coverage_type"]),
    ("Was a vehicle inspection done at policy inception?","policy_number",4,ALL,["policy_number"]),
    ("Was the policy renewed on time without a break?","policy_active",2,ALL,["policy_active"]),
    ("Was the premium paid by the registered owner?","driver_is_owner",3,ALL,["driver_is_owner"]),
    ("Did the policy explicitly exclude the incident category in question?","coverage_type",2,ALL,["coverage_type"]),
    ("Was the vehicle hypothecated to an NBFC?","policy_number",3,ALL,["policy_number"]),
    ("Was the vehicle used as a delivery vehicle at the time?","vehicle_usage_type",2,ALL,["vehicle_usage_type"]),
    ("Was there a voluntary deductible applied to this policy?","coverage_type",4,ALL,["coverage_type"]),
    ("Was the coverage territory India or extended internationally?","policy_active",4,ALL,["policy_active"]),
    ("Was the vehicle operated in a high-risk territory?","loss_location_city",3,ALL,["loss_location"]),
    ("Was a telematics or UBI device installed as a policy requirement?","theft_tracking_device",4,ALL,["theft_tracking_device"]),
    ("Did the driver hold a valid driving licence at the time of purchase of this policy?","driver_license_valid",3,ALL,["driver_license_valid"]),
    ("Was the key replacement add-on specifically activated?","add_ons",5,["theft","vandalism"],["add_ons"]),
    ("Was the consumables add-on activated for this claim?","add_ons",5,DMG,["add_ons"]),
    ("Was the personal accident cover for owner-driver active?","add_ons",3,["collision","rollover","self_accident","fire","flood","natural_disaster"],["add_ons"]),
    ("Did the policy include any specific exclusion for war or terrorism?","policy_active",4,ALL,["policy_active"]),
    ("Was the vehicle rated as a high-value or classic vehicle?","coverage_type",4,ALL,["coverage_type"]),
    ("Was the policy endorsed for a different address than where the incident occurred?","policy_number",4,ALL,["policy_number"]),
    ("Was there an anti-theft fitment requirement in the policy for theft cover?","theft_tracking_device",2,["theft","theft_attempted"],["theft_tracking_device"]),
    ("Was the driver listed as an excluded driver on the policy?","driver_is_owner",2,["collision","self_accident","hit_and_run","rollover","fire","flood"],["driver_is_owner"]),
    ("Was the vehicle a demo or test-drive vehicle?","vehicle_usage_type",3,ALL,["vehicle_usage_type"]),
    ("Was the policy in the name of a deceased person?","driver_is_owner",2,ALL,["driver_is_owner"]),
    ("Was there a co-insured or joint policy holder?","policy_number",4,ALL,["policy_number"]),
    ("Was the car imported or CKD assembled?","vehicle_usage_type",4,ALL,["vehicle_usage_type"]),
    ("Was there a deductible waiver add-on active?","add_ons",5,ALL,["add_ons"]),
    ("Was the vehicle used for ridesharing at time of incident?","vehicle_usage_type",2,["collision","self_accident","theft","fire","flood"],["vehicle_usage_type"]),
    ("Was the policy a multi-year policy?","policy_active",4,ALL,["policy_active"]),
    ("Was the no-claim bonus certificate submitted?","policy_number",4,ALL,["policy_number"]),
    ("Was a broker or agent involved in purchasing this policy?","policy_number",5,ALL,["policy_number"]),
    ("Was the vehicle listed in the permitted vehicle schedule of a commercial policy?","vehicle_usage_type",3,ALL,["vehicle_usage_type"]),
]
for t,f,p,it,fills in pol_extra:
    qs.append(mk(t,f,p,it,fills,"policy_eligibility"))


nd_extra = [
    ("Was the vehicle under a bridge or overpass when the disaster struck?","loss_location_road_type",3,["natural_disaster"],["loss_location"]),
    ("Was the vehicle interior soaked due to hailstorm with broken windows?","damage_areas_windshield",3,["natural_disaster"],["damage_areas"]),
    ("Did hailstones dent the roof, bonnet or boot of the vehicle?","damage_areas_roof",3,["natural_disaster"],["damage_areas"]),
    ("Was snow or ice accumulation responsible for the damage?","weather_condition",3,["natural_disaster"],["weather_condition"]),
    ("Was a government weather alert issued before the incident?","loss_datetime",3,["natural_disaster"],["loss_datetime"]),
    ("Was a local authority evacuation notice in effect?","loss_location_city",3,["natural_disaster"],["loss_location"]),
    ("Did a falling tree branch land on the vehicle roof?","damage_areas_roof",2,["natural_disaster"],["damage_areas"]),
    ("Was the vehicle struck by lightning?","fire_source",2,["natural_disaster","fire"],["fire_source"]),
    ("Was the vehicle buried under debris or mud?","flood_water_level",2,["natural_disaster"],["flood_water_level"]),
    ("Was the vehicle in a designated shelter zone?","loss_location_road_type",4,["natural_disaster"],["loss_location"]),
    ("Was there a power outage in the area at the time of the disaster?","loss_datetime",4,["natural_disaster"],["loss_datetime"]),
    ("Was the vehicle damage covered under the natural calamity add-on?","add_ons",3,["natural_disaster"],["add_ons"]),
    ("Did authorities declare a curfew in the affected area?","police_report_filed",4,["natural_disaster"],["police_report_filed"]),
    ("Were rescue services involved in retrieving the vehicle?","fire_brigade_called",4,["natural_disaster"],["fire_brigade_called"]),
    ("Was the incident recorded in the disaster management authority's report?","evidence_photos_available",4,["natural_disaster"],["evidence_photos_available"]),
    ("Was any government relief or compensation provided for the vehicle damage?","loss_location_city",4,["natural_disaster"],["loss_location"]),
    ("Were satellite or aerial images available of the disaster zone?","evidence_photos_available",5,["natural_disaster"],["evidence_photos_available"]),
    ("Was the vehicle in a riverbed or drainage channel during the disaster?","loss_location_road_type",3,["natural_disaster","flood"],["loss_location"]),
    ("Did the vehicle suffer structural frame damage from the natural event?","damage_areas_underbody",3,["natural_disaster"],["damage_areas"]),
    ("Was the natural disaster preceded by any industrial accident?","fire_source",3,["natural_disaster","fire"],["fire_source"]),
]
for t,f,p,it,fills in nd_extra:
    qs.append(mk(t,f,p,it,fills,"natural_disaster_specific"))


ib_extra = [
    ("Was this the first insurance claim you have ever filed?","previous_claims",2,ALL,["previous_claims"]),
    ("Was the vehicle being driven by you personally at the time?","driver_is_owner",2,ALL,["driver_is_owner"]),
    ("Were you returning from or going to work when the incident occurred?","loss_datetime",3,COL,["loss_datetime"]),
    ("Were any passengers in the vehicle when the incident occurred?","injury_reported",2,COL+["fire","flood","natural_disaster"],["injury_reported"]),
    ("Were children present in the vehicle during the incident?","injury_reported",1,COL+["fire","flood","natural_disaster"],["injury_reported"]),
    ("Were any pets in the vehicle at the time of the incident?","injury_reported",3,COL+["fire","flood","vandalism"],["injury_reported"]),
    ("Was the vehicle dash camera recording at the time of the incident?","dashcam_available",3,COL,["dashcam_available"]),
    ("Was the vehicle rented from a car rental company?","vehicle_usage_type",2,ALL,["vehicle_usage_type"]),
    ("Was the vehicle being driven after midnight?","loss_datetime",3,COL+["theft","vandalism"],["loss_datetime"]),
    ("Was the incident on a public road or a gated community road?","loss_location_road_type",3,ALL,["loss_location"]),
    ("Was the vehicle brand new (less than 1 month old) at the time of the incident?","vehicle_year",3,ALL,["vehicle"]),
    ("Was the incident on a toll road and is there a toll record available?","evidence_video_available",4,COL,["evidence_video_available"]),
    ("Was the vehicle stationary for more than an hour before the incident?","vehicle_moving_status",4,["theft","vandalism","fire"],["vehicle_moving_status"]),
    ("Was the incident discovered by a third party rather than the driver?","loss_datetime",4,["theft","vandalism","fire","natural_disaster"],["loss_datetime"]),
    ("Were you returning from an event or gathering when the incident happened?","loss_datetime",3,COL,["loss_datetime"]),
    ("Was the vehicle on a city flyover when the incident happened?","loss_location_road_type",3,COL,["loss_location"]),
    ("Was the vehicle involved in any previous incident at the same location?","previous_claims",3,ALL,["previous_claims"]),
    ("Had you recently changed the vehicle's insurance provider?","policy_number",3,ALL,["policy_number"]),
    ("Was the vehicle garaged overnight or parked outdoors?","vehicle_moving_status",4,["theft","vandalism","fire","natural_disaster","flood"],["vehicle_moving_status"]),
    ("Was there any road closure or diversion that contributed to the incident?","road_condition",3,COL,["road_condition"]),
    ("Were there any traffic police present near the scene at the time?","police_report_filed",3,COL,["police_report_filed"]),
    ("Was the incident on a busy shopping or market street?","loss_location_road_type",4,ALL,["loss_location"]),
    ("Was the incident during a festival or peak traffic period?","loss_datetime",4,COL,["loss_datetime"]),
    ("Was the vehicle a part of a convoy at the time?","vehicle_moving_status",4,COL+["flood","natural_disaster"],["vehicle_moving_status"]),
    ("Was the vehicle recently returned from a long trip?","vehicle_moving_status",4,ALL,["vehicle_moving_status"]),
    ("Were you distracted at the time the incident occurred?","signal_compliance",2,COL,["signal_compliance"]),
    ("Was there any construction or scaffolding near where the incident happened?","road_condition",3,ALL,["loss_location"]),
    ("Were emergency lights or hazard lights activated after the incident?","drivable",3,COL+["fire","flood"],["drivable"]),
    ("Was the vehicle recovered by a private towing service?","towing_required",4,DMG,["towing_required"]),
    ("Was the vehicle last seen at a specific petrol station or landmark?","loss_location_city",4,["theft"],["loss_location"]),
    ("Were there bystanders who helped at the scene after the incident?","witnesses_present",4,COL+["fire","flood"],["witnesses_present"]),
    ("Was the incident caused by an animal crossing the road?","impact_direction",2,["collision_animal","self_accident"],["impact_direction"]),
    ("Were the vehicle lights properly functioning at the time?","weather_condition",3,COL,["weather_condition"]),
    ("Was the vehicle on a one-lane road when the incident occurred?","loss_location_road_type",3,COL,["loss_location"]),
    ("Was a blood sample or breathalyser test requested by police?","police_report_filed",2,COL,["police_report_filed"]),
    ("Were any agricultural vehicles or tractors involved?","third_party_vehicle_id",3,["collision","collision_animal","hit_and_run"],["third_party_vehicle_id"]),
    ("Was the vehicle carrying any cargo or load at the time?","vehicle_usage_type",3,COL+["theft"],["vehicle_usage_type"]),
    ("Was the incident during a rainy season monsoon?","weather_condition",3,COL+["flood","natural_disaster"],["weather_condition"]),
    ("Were you using a navigation or mapping app when the incident occurred?","signal_compliance",4,COL,["signal_compliance"]),
    ("Was the incident at a known accident-prone spot or black spot?","loss_location_road_type",3,COL,["loss_location"]),
]
for t,f,p,it,fills in ib_extra:
    qs.append(mk(t,f,p,it,fills,"incident_basics"))

print(f"Generated {len(qs)} extra questions")
last_id = get_last_id(BASE_PATH)
set_start(last_id)
with open(BASE_PATH, "a", encoding="utf-8") as f:
    for q_obj in qs:
        q_obj["id"] = f"Q{c[0]:04d}"
        f.write(json.dumps(q_obj, ensure_ascii=False) + "\n")

total = sum(1 for _ in open(BASE_PATH))
print(f"Total in bank: {total}")
