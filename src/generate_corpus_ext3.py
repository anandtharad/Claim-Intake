import json, os

BASE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "question_bank_raw.jsonl")
last = max(int(json.loads(l)["id"][1:]) for l in open(BASE_PATH))
c = [last]
def mk(t,f,p,it,fills,cat):
    c[0]+=1
    return {"id":f"Q{c[0]:04d}","text":t,"question_field":f,"priority":p,"category_tag":cat,
            "triggers":{"incident_type":it},"targets":{"fill_fields":fills}}

ALL=["collision","collision_wall","collision_animal","hit_and_run","theft","theft_attempted","fire","flood","vandalism","natural_disaster","self_accident","rollover"]
COL=["collision","hit_and_run","self_accident","rollover","collision_wall","collision_animal"]
DMG=["collision","hit_and_run","self_accident","rollover","vandalism","fire","flood","collision_wall","natural_disaster","collision_animal"]

qs=[]

cd=[
    ("Was the road camber or banking contributing to the accident?","road_condition",4,COL,["road_condition"]),
    ("Was there a traffic island or roundabout involved?","loss_location_road_type",3,COL,["loss_location"]),
    ("Was your vehicle's ABS or ESC system active during braking?","road_condition",3,COL,["road_condition"]),
    ("Was the headrest adjusted properly at the time of rear impact?","injury_reported",4,["collision","hit_and_run"],["injury_reported"]),
    ("Was the horn sounded before the collision?","signal_compliance",4,COL,["signal_compliance"]),
    ("Were any towing or trailer hitches involved in the impact?","vehicle_moving_status",4,COL,["vehicle_moving_status"]),
    ("Was there a median break or U-turn point near the accident location?","loss_location_road_type",4,COL,["loss_location"]),
    ("Was there a school or hospital zone speed limit in effect?","speed_estimate",3,COL,["speed_estimate"]),
    ("Was the sun glare or headlight glare a contributing factor?","weather_condition",3,COL,["weather_condition"]),
    ("Was the accident at a level crossing?","loss_location_road_type",3,COL,["loss_location"]),
    ("Did a railway gate or barrier malfunction contribute to the accident?","road_condition",3,COL,["road_condition"]),
    ("Was the road freshly painted or newly marked (slippery marks)?","road_condition",4,COL,["road_condition"]),
    ("Were speed cameras active at the accident point?","speed_estimate",4,COL,["speed_estimate"]),
    ("Was the lane merging or splitting a factor in the accident?","lane_action",4,COL,["lane_action"]),
    ("Was there a broken traffic signal at the accident site?","signal_compliance",3,COL,["signal_compliance"]),
    ("Were any emergency vehicles involved or crossed paths?","third_party_vehicle_id",3,["collision","hit_and_run"],["third_party_vehicle_id"]),
    ("Was the pavement or shoulder of the road damaged?","road_condition",4,COL,["road_condition"]),
    ("Was there a narrow bridge or culvert near the accident spot?","loss_location_road_type",4,COL,["loss_location"]),
    ("Was the road flooded or waterlogged during the collision?","road_condition",3,["collision","self_accident","flood"],["road_condition"]),
    ("Were there any illegal hoardings or obstructions blocking the road view?","road_condition",4,COL,["road_condition"]),
]
for t,f,p,it,fills in cd: qs.append(mk(t,f,p,it,fills,"collision_dynamics"))

fr=[
    ("Was the accident report filed by a public authority or only by the claimant?","police_report_filed",2,ALL,["police_report_filed"]),
    ("Were the location metadata on photos consistent with the claimed accident site?","evidence_photos_available",1,DMG,["evidence_photos_available"]),
    ("Were the damage photographs taken before or after any repair was started?","evidence_photos_available",1,DMG,["evidence_photos_available"]),
    ("Was the accident scene visited by a loss assessor within 24 hours?","repair_preference",3,DMG,["repair_preference"]),
    ("Was a duplicate FIR filed at any other police station?","fir_number",1,["collision","theft","fire","vandalism","hit_and_run"],["fir_number"]),
    ("Was the claim amount rounded off to an unusual exact figure?","damage_severity",2,ALL,["damage_severity"]),
    ("Was the third-party vehicle also insured by the same company?","third_party_insurer",2,["collision"],["third_party_insurer"]),
    ("Did both parties in the collision know each other personally?","third_party_driver_name",2,["collision"],["third_party_driver_name"]),
    ("Were the mileage or odometer readings consistent with the declared usage?","vehicle_usage_type",2,ALL,["vehicle_usage_type"]),
    ("Was the claim filed just before the policy expiry date?","policy_active",2,ALL,["policy_active"]),
    ("Was the surveyor unable to reach the accident location?","repair_preference",3,DMG,["repair_preference"]),
    ("Was there a delay between the FIR date and the date stated in the claim form?","fir_number",1,["collision","theft","fire","vandalism"],["fir_number"]),
    ("Were contact details of the witness verified independently?","witness_contact",2,["collision","vandalism","fire"],["witness_contact"]),
    ("Was the repair bill issued by an unlicensed or informal workshop?","repair_preference",2,DMG,["repair_preference"]),
    ("Were any replacement parts in the repair estimate used or salvage items?","damage_severity",3,DMG,["damage_severity"]),
]
for t,f,p,it,fills in fr: qs.append(mk(t,f,p,it,fills,"fraud_consistency"))

rs=[
    ("Was the vehicle inspection performed by an IRDA-certified surveyor?","repair_preference",3,ALL,["repair_preference"]),
    ("Was the workshop's repair estimate itemised by labour and parts?","evidence_photos_available",4,DMG,["evidence_photos_available"]),
    ("Was the vehicle cleaned before inspection?","repair_preference",4,DMG,["repair_preference"]),
    ("Was the repair authorisation given within 48 hours of claim filing?","repair_preference",3,DMG,["repair_preference"]),
    ("Was a reinspection required after partial repairs?","repair_preference",4,DMG,["repair_preference"]),
    ("Was the final repair bill higher than the initial estimate?","damage_severity",4,DMG,["damage_severity"]),
    ("Was any genuine OEM part unavailable and substituted?","repair_preference",4,DMG,["repair_preference"]),
    ("Was the cashless limit exceeded at the network garage?","settlement_preference",4,DMG,["settlement_preference"]),
    ("Was the vehicle delivered after repair without proper inspection?","repair_preference",4,DMG,["repair_preference"]),
    ("Were any hidden damages discovered during the final repair process?","damage_areas",4,DMG,["damage_areas"]),
]
for t,f,p,it,fills in rs: qs.append(mk(t,f,p,it,fills,"repair_settlement"))

sa=[
    ("Did the vehicle leave the road during the accident?","lane_action",2,["self_accident","rollover"],["lane_action"]),
    ("Did the vehicle roll over completely or partially?","impact_direction",2,["rollover"],["impact_direction"]),
    ("Was the vehicle inverted (roof touching ground) after the rollover?","impact_direction",2,["rollover"],["impact_direction"]),
    ("Was anyone trapped inside after the rollover?","injury_reported",1,["rollover"],["injury_reported"]),
    ("Was the vehicle door jammed after the self-accident?","drivable",2,["self_accident","rollover"],["drivable"]),
    ("Was the fuel leaking after the self-accident?","fire_source",2,["self_accident","rollover"],["fire_source"]),
    ("Were all occupants able to exit the vehicle after the rollover?","injury_reported",1,["rollover"],["injury_reported"]),
    ("Was the vehicle driven on an off-road or unpaved surface?","road_condition",3,["self_accident","rollover"],["road_condition"]),
    ("Was the accident caused by overloading or unbalanced load?","vehicle_moving_status",3,["self_accident","rollover"],["vehicle_moving_status"]),
    ("Was the vehicle righted or recovered from the rollover position?","vehicle_towed",3,["rollover"],["vehicle_towed"]),
    ("Did the self-accident involve hitting a road divider?","impact_direction",2,["self_accident","collision_wall"],["impact_direction"]),
    ("Was the accident caused by a sudden swerve to avoid another vehicle?","lane_action",2,["self_accident","rollover"],["lane_action"]),
    ("Was a tyre blow-out the primary cause of the self-accident?","road_condition",2,["self_accident","rollover"],["road_condition"]),
    ("Was the driver distracted by something inside the vehicle?","signal_compliance",2,["self_accident"],["signal_compliance"]),
    ("Were the brakes functioning properly before the accident?","road_condition",2,["self_accident","rollover"],["road_condition"]),
]
for t,f,p,it,fills in sa: qs.append(mk(t,f,p,it,fills,"collision_dynamics"))

print(f"Extra questions: {len(qs)}")
with open(BASE_PATH,"a") as f:
    for q in qs: f.write(json.dumps(q)+"\n")
total = sum(1 for _ in open(BASE_PATH))
print(f"Grand total: {total}")

last = max(int(json.loads(l)["id"][1:]) for l in open(BASE_PATH))
c[0] = last
qs2=[]
misc=[
    ("Was any animal struck by the vehicle during the accident?","impact_direction",2,["collision_animal"],["impact_direction"]),
    ("What type of animal was involved in the collision?","impact_direction",3,["collision_animal"],["impact_direction"]),
    ("Was the animal a stray or owned livestock?","impact_direction",3,["collision_animal"],["impact_direction"]),
    ("Was the animal carcass removed from the road after the incident?","road_condition",4,["collision_animal"],["road_condition"]),
    ("Were any forest department or municipal authorities notified?","police_report_filed",4,["collision_animal"],["police_report_filed"]),
    ("Was the vehicle's undercarriage damaged by the animal impact?","damage_areas_underbody",3,["collision_animal"],["damage_areas"]),
    ("Was there wildlife warning signage on that road?","road_condition",4,["collision_animal"],["road_condition"]),
    ("Was the attempted theft interrupted by a passerby?","theft_forced_entry",3,["theft_attempted"],["theft_forced_entry"]),
    ("Was any part of the vehicle damaged during the theft attempt?","damage_areas",2,["theft_attempted"],["damage_areas"]),
    ("Was the attempted theft detected by the vehicle alarm?","theft_tracking_device",3,["theft_attempted"],["theft_tracking_device"]),
    ("Was the attempted thief caught or identified?","theft_forced_entry",3,["theft_attempted"],["theft_forced_entry"]),
    ("Was the lock or ignition tampered with during the theft attempt?","theft_forced_entry",2,["theft_attempted"],["theft_forced_entry"]),
    ("Was a police report filed for the attempted theft?","police_report_filed",2,["theft_attempted"],["police_report_filed"]),
    ("Was any CCTV footage recovered showing the attempted theft?","evidence_video_available",3,["theft_attempted"],["evidence_video_available"]),
    ("Was the window broken to gain access during the attempted theft?","theft_forced_entry",2,["theft_attempted"],["theft_forced_entry"]),
    ("Was the vehicle impounded as evidence in the theft case?","vehicle_towed",4,["theft","theft_attempted"],["vehicle_towed"]),
    ("Was there forensic evidence collected by the police at the scene?","evidence_photos_available",3,["theft","vandalism","fire"],["evidence_photos_available"]),
    ("Was the collision wall a boundary wall or a road structure?","impact_direction",3,["collision_wall"],["impact_direction"]),
    ("Was the wall or structure damaged in the collision?","third_party_involved",3,["collision_wall"],["third_party_involved"]),
    ("Was the wall privately owned or government property?","third_party_involved",4,["collision_wall"],["third_party_involved"]),
    ("Was a demand for repair of the wall received?","third_party_contact",4,["collision_wall"],["third_party_contact"]),
    ("Was the driver able to brake before hitting the wall?","speed_estimate",3,["collision_wall"],["speed_estimate"]),
    ("Was any third-party property other than a vehicle damaged?","third_party_involved",3,["collision_wall","self_accident"],["third_party_involved"]),
    ("Was a government road barrier or crash barrier involved?","impact_direction",3,["collision_wall","self_accident","rollover"],["impact_direction"]),
    ("Was a survey conducted to assess damage to the wall?","evidence_photos_available",4,["collision_wall"],["evidence_photos_available"]),
    ("Was any public property damaged during the incident?","third_party_involved",3,["collision_wall","collision","self_accident"],["third_party_involved"]),
    ("Was the vehicle going at very low speed when it hit the wall?","speed_estimate",3,["collision_wall"],["speed_estimate"]),
    ("Was the wall damage covered under third-party liability?","coverage_type",3,["collision_wall"],["coverage_type"]),
    ("Were any electrical poles or wires involved in the accident?","third_party_involved",3,["collision_wall","self_accident","rollover"],["third_party_involved"]),
    ("Was there damage to signboards or public infrastructure?","third_party_involved",4,["collision_wall","self_accident"],["third_party_involved"]),
    ("Were traffic bollards or road markings part of the accident?","road_condition",4,["collision_wall","self_accident"],["road_condition"]),
    ("Was the vehicle submerged in a ditch or canal?","flood_water_level",2,["flood","self_accident","natural_disaster"],["flood_water_level"]),
    ("Was the vehicle roof compromised from hailstone impact?","damage_areas_roof",3,["natural_disaster"],["damage_areas"]),
    ("Was roadside vegetation damage reported as evidence?","evidence_photos_available",5,["self_accident","collision_animal"],["evidence_photos_available"]),
    ("Was any nearby structure like a wall, gate, or post damaged?","third_party_involved",4,["collision_wall","collision","self_accident"],["third_party_involved"]),
    ("Was the windshield cracked from a stone or debris on the road?","damage_areas_windshield_front",3,["collision","self_accident","natural_disaster"],["damage_areas"]),
    ("Was there any bird or flying debris that impacted the windshield?","damage_areas_windshield_front",4,["collision","natural_disaster"],["damage_areas"]),
    ("Was the vehicle door opened into oncoming traffic?","lane_action",3,["collision","hit_and_run"],["lane_action"]),
    ("Was any loose load on another vehicle responsible for the damage?","impact_direction",3,["collision"],["impact_direction"]),
    ("Were any construction materials from a nearby site involved?","road_condition",4,["collision","vandalism"],["road_condition"]),
    ("Was a pothole or road crater the primary cause of the accident?","road_condition",3,["self_accident","collision"],["road_condition"]),
    ("Was any oil spill or diesel spill on the road a contributing factor?","road_condition",3,["collision","self_accident"],["road_condition"]),
    ("Were there any iron rod or rebar projections that damaged the vehicle?","damage_areas",3,["collision","collision_wall","self_accident"],["damage_areas"]),
    ("Was a bridge railing or side barrier struck?","impact_direction",3,["collision_wall","self_accident","rollover"],["impact_direction"]),
    ("Was the crash on a one-way road going the wrong direction?","lane_action",2,["collision","hit_and_run","self_accident"],["lane_action"]),
    ("Were any traffic cones from a construction site hit?","road_condition",4,["collision","self_accident"],["road_condition"]),
    ("Were any temporary road markings or diversions involved?","road_condition",4,["collision","self_accident"],["road_condition"]),
    ("Was a parked vehicle without hazard lights hit?","impact_direction",3,["collision","hit_and_run"],["impact_direction"]),
    ("Was the accident caused by reversing into another vehicle?","impact_direction",2,["collision","collision_wall","self_accident"],["impact_direction"]),
    ("Was the accident caused by a sudden vehicle breakdown ahead?","lane_action",3,["collision","self_accident"],["lane_action"]),
    ("Was an improperly parked vehicle blocking the view responsible?","road_condition",3,["collision","self_accident"],["road_condition"]),
    ("Was there a defect in the vehicle's steering or suspension prior to the accident?","road_condition",3,["self_accident","rollover","collision"],["road_condition"]),
    ("Was the vehicle wheel alignment faulty before the accident?","road_condition",4,["self_accident","collision","rollover"],["road_condition"]),
    ("Was the vehicle brake fluid low or faulty?","road_condition",3,["self_accident","collision","rollover"],["road_condition"]),
    ("Was an animal on the road the reason the driver swerved?","lane_action",3,["self_accident","rollover","collision"],["lane_action"]),
    ("Was a road sign missing that led to the driver taking a wrong turn?","road_condition",4,["self_accident","collision"],["road_condition"]),
    ("Was the GPS navigation system directing onto a road that was closed?","road_condition",4,["self_accident","collision"],["road_condition"]),
    ("Was the vehicle reversing without rear camera or mirrors?","impact_direction",3,["collision","collision_wall","self_accident"],["impact_direction"]),
    ("Was the vehicle's tyre pressure incorrect before the accident?","road_condition",4,["self_accident","rollover","collision"],["road_condition"]),
    ("Was the accident caused by overtaking on a blind curve?","lane_action",2,["collision","self_accident","rollover"],["lane_action"]),
    ("Was the vehicle weaving or zigzagging before the collision?","lane_action",3,["collision","hit_and_run"],["lane_action"]),
    ("Was the engine stalling a reason for the accident?","vehicle_moving_status",3,["self_accident","collision"],["vehicle_moving_status"]),
    ("Did the driver attempt to avoid a pothole and swerve?","lane_action",3,["self_accident","collision"],["lane_action"]),
    ("Was the road free of traffic when the accident occurred?","lane_action",4,["self_accident","rollover"],["lane_action"]),
    ("Was a wrong-side overtaking vehicle the cause?","lane_action",2,["collision","hit_and_run"],["lane_action"]),
    ("Was the vehicle in cruise control mode at the time?","speed_estimate",4,["collision","self_accident","rollover"],["speed_estimate"]),
    ("Was there any problem with the vehicle's wiper or defroster impairing vision?","weather_condition",3,["collision","self_accident"],["weather_condition"]),
    ("Was the driver under stress or fatigue at the time of the accident?","signal_compliance",3,["collision","self_accident","rollover"],["signal_compliance"]),
    ("Was the driver momentarily blinded by headlights of an oncoming vehicle?","weather_condition",3,["collision","self_accident","hit_and_run"],["weather_condition"]),
    ("Was the driver known to have any medical condition affecting driving?","driver_license_valid",2,["collision","self_accident","rollover"],["driver_license_valid"]),
    ("Was the fuel gauge faulty causing the vehicle to stall?","vehicle_moving_status",4,["self_accident","collision"],["vehicle_moving_status"]),
    ("Was the accident in a no-vehicle zone or restricted zone?","loss_location_road_type",4,["collision","self_accident"],["loss_location"]),
    ("Was there a car-jacking or forced accident?","theft_forced_entry",1,["collision","theft"],["theft_forced_entry"]),
    ("Were any acts of road rage involved in the incident?","third_party_driver_name",2,["collision","hit_and_run","vandalism"],["third_party_driver_name"]),
    ("Was the vehicle deliberately rammed?","impact_direction",1,["collision"],["impact_direction"]),
    ("Was the third party part of an organised fraud ring?","third_party_driver_name",1,["collision"],["third_party_driver_name"]),
]
for t,f,p,it,fills in misc: qs2.append(mk(t,f,p,it,fills,"collision_dynamics" if it[0] in ["collision","collision_wall","collision_animal","hit_and_run","self_accident","rollover"] else "incident_basics"))
print(f"Misc batch: {len(qs2)}")
with open(BASE_PATH,"a") as f:
    for q in qs2: f.write(json.dumps(q)+"\n")
total = sum(1 for _ in open(BASE_PATH))
print(f"Grand total now: {total}")
