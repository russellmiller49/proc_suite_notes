import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_085"
OUTPUT_DIR = "reporter_training"
NUM_SAMPLES = 100
TRAIN_RATIO = 0.8

# Ensure output directory exists
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
    print(f"Created output directory: {OUTPUT_DIR}")

# ==========================================
# 2. DATA POOLS (Medical Variations)
# ==========================================
data_pool = {
    "age": ["62", "65", "68", "71", "74", "77", "81", "85"],
    "gender_tuple": [("female", "F"), ("male", "M")],
    "indication": [
        "hemoptysis after bronchoscopy",
        "post-biopsy bleeding",
        "persistent hemoptysis",
        "massive hemoptysis control"
    ],
    "instrumentation_blocker": [
        "7 Fr Arndt bronchial blocker",
        "9 Fr Arndt bronchial blocker",
        "EZ-Blocker",
        "Cohen bronchial blocker"
    ],
    "ett_distance": ["1.5", "2", "2.5", "3"],
    "old_blocker_loc": ["RLL", "LLL", "R Main", "L Main"],
    "aspiration_target": [
        "LLL and LMSB",
        "RLL and RMSB",
        "bilateral lower lobes",
        "distal airways"
    ],
    "inflation_vol": ["3", "4", "5", "6"],
    # Tuple: (Anatomical Position, Occlusion Result)
    "position_scenario": [
        ("distal BI", "occlusion of the BI without occlusion of the RUL"),
        ("Left Main Stem", "occlusion of the LMSB without herniation"),
        ("Right Main Stem", "occlusion of the RMSB sparing the trachea"),
        ("RLL bronchus", "isolation of the RLL sparing the RML")
    ],
    "surveillance_finding": [
        "no increase in the blood seen",
        "minor oozing but no active flow",
        "complete cessation of bleeding",
        "stable clot formation"
    ],
    "blocker_depth": ["38", "40", "42", "45"],
    "ett_depth": ["20", "21", "22", "23"],
    "next_check_time": ["1500 today", "1800 today", "0800 tomorrow", "1200 today"]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
# <--- CONVERT USER'S NOTE INTO f-string OR .format() TEMPLATE HERE --->
note_template = """INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: [Date] 
INDICATION FOR OPERATION: Patient is a {age}-year-old {gender_long} who presents with {indication}.
The nature, purpose, risks, benefits and alternatives to Bronchoscopy were discussed with the patient in detail.

PREOPERATIVE DIAGNOSIS
Hemoptysis 

POSTOPERATIVE DIAGNOSIS
Hemoptysis 

PROCEDURE
31645 Therapeutic aspiration initial episode 
31622 Dx bronchoscope/cell washing 
Bronchial blocker exchange and positioning 

ANESTHESIA: Continuous sedation 

MONITORING: Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.

INSTRUMENTATION: Disposable Bronchoscope; {blocker_name}.

ESTIMATED BLOOD LOSS: Minimum 

COMPLICATIONS: None 

PROCEDURE IN DETAIL: A timeout was performed (confirming the patient's name, procedure type, and procedure location).

Patient Position: Supine 

Initial Airway Inspection: The bronchoscope was introduced into the ETT.
The ETT is {ett_distance} cm above the main carina. The bronchial blocker was in the {old_blocker_loc} but was mostly deflated without evidence of spill over into the other segments.

Therapeutic Aspiration: Successful therapeutic aspiration was performed to clean out the {aspiration_target} from mucus.

Bronchial Blocker Exchange: The balloon was fully deflated and then removed.
Then a new {blocker_name} was replaced through the existing ETT.
The blocker was positioned in the {new_pos}. {inflation_vol} mL of air was introduced into the blocker and resulted in {occlusion_result}.

Surveillance and Completion: During exchange of the bronchial blocker there was {surveillance_finding}.
This was not aspirated due to no obvious formed clot.

The bronchoscope was removed. The patient tolerated the procedure well.
There were no immediate complications.

SPECIMEN(S): None 

IMPRESSION / PLAN: Patient is a {age}-year-old {gender_long} who presents for bronchoscopy for hemoptysis.
Blocker Management: Keep blocker in place at {blocker_depth} cm at the connective device.
Airway Management: ETT at {ett_depth} cm at the front tooth.

Medication/Follow-up: Stop paralysis; once this is not effective stop fentanyl and repeat bronchoscopy at {next_check_time}.

Communication: Family updated.
"""

# <--- CREATE 5 DISTINCT PROMPT STYLES HERE --->
prompt_styles = [
    # Style 1: Telegraphic / Handoff
    "Bronchial blocker exchange note. {age}yo {gender_short}. Indication: {indication}. Old blocker in {old_blocker_loc}, replaced with {blocker_name} to {new_pos}. Inflated {inflation_vol}cc ({occlusion_result}). {surveillance_finding}. Plan: Blocker at {blocker_depth}cm, ETT {ett_depth}cm. Re-scope {next_check_time}.",
    
    # Style 2: Dictation
    "Please write an interventional pulmonology report for a {age} year old {gender_long} with {indication}. We did a therapeutic aspiration of the {aspiration_target} and a blocker exchange. The old one was in the {old_blocker_loc}. The new {blocker_name} is in the {new_pos} inflated with {inflation_vol} mL causing {occlusion_result}. Keep blocker at {blocker_depth} cm.",
    
    # Style 3: Sloppy / Quick
    "{age} {gender_short} hemoptysis. Bronchial blocker swap. Old loc {old_blocker_loc}. New loc {new_pos}. Cleared out {aspiration_target}. ETT {ett_distance}cm above carina. No complications. Plan: repeat bronch {next_check_time}.",
    
    # Style 4: Billing Focus
    "Codes 31645, 31622. {age}y {gender_short}. Dx: Hemoptysis. Procedure: Bronchial blocker exchange using {blocker_name}. Findings: ETT {ett_distance}cm above carina. Blocker set in {new_pos} with {inflation_vol}mL air. Outcome: {occlusion_result}.",
    
    # Style 5: Structured Request
    "Generate Op Report:\nPatient: {age}/{gender_short}\nIndication: {indication}\nProcedure: Blocker Exchange & Aspiration\nFindings:\n- Old Blocker: {old_blocker_loc}\n- New Blocker: {new_pos} ({occlusion_result})\n- Airway: Cleaned {aspiration_target}\nPlan: Blocker depth {blocker_depth}cm."
]

# ==========================================
# 4. GENERATOR LOGIC
# ==========================================
def generate_dataset():
    dataset = []
    
    for _ in range(NUM_SAMPLES):
        # A. Randomly select variables
        age = random.choice(data_pool["age"])
        gender_tup = random.choice(data_pool["gender_tuple"])
        indication = random.choice(data_pool["indication"])
        blocker_name = random.choice(data_pool["instrumentation_blocker"])
        ett_distance = random.choice(data_pool["ett_distance"])
        old_blocker_loc = random.choice(data_pool["old_blocker_loc"])
        aspiration_target = random.choice(data_pool["aspiration_target"])
        inflation_vol = random.choice(data_pool["inflation_vol"])
        
        # Unpack position scenario tuple to ensure logic matches (Pos -> Result)
        pos_scenario = random.choice(data_pool["position_scenario"])
        new_pos = pos_scenario[0]
        occlusion_result = pos_scenario[1]
        
        surveillance_finding = random.choice(data_pool["surveillance_finding"])
        blocker_depth = random.choice(data_pool["blocker_depth"])
        ett_depth = random.choice(data_pool["ett_depth"])
        next_check_time = random.choice(data_pool["next_check_time"])
        
        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_tup[1], 
            gender_long=gender_tup[0],
            indication=indication,
            old_blocker_loc=old_blocker_loc,
            blocker_name=blocker_name,
            new_pos=new_pos,
            inflation_vol=inflation_vol,
            occlusion_result=occlusion_result,
            surveillance_finding=surveillance_finding,
            blocker_depth=blocker_depth,
            ett_depth=ett_depth,
            next_check_time=next_check_time,
            aspiration_target=aspiration_target,
            ett_distance=ett_distance
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            age=age, 
            gender_long=gender_tup[0],
            indication=indication,
            blocker_name=blocker_name,
            ett_distance=ett_distance,
            old_blocker_loc=old_blocker_loc,
            aspiration_target=aspiration_target,
            new_pos=new_pos,
            inflation_vol=inflation_vol,
            occlusion_result=occlusion_result,
            surveillance_finding=surveillance_finding,
            blocker_depth=blocker_depth,
            ett_depth=ett_depth,
            next_check_time=next_check_time
        )
        
        dataset.append({"prompt": prompt, "completion": completion})
    
    return dataset

# ==========================================
# 5. EXECUTION & SAVING
# ==========================================
if __name__ == "__main__":
    print(f"Generating data for {NOTE_ID}...")
    full_data = generate_dataset()
    
    # Shuffle
    random.shuffle(full_data)
    
    # Split
    split_index = int(NUM_SAMPLES * TRAIN_RATIO)
    train_data = full_data[:split_index]
    valid_data = full_data[split_index:]
    
    # Define File Paths
    train_filename = os.path.join(OUTPUT_DIR, f"{NOTE_ID}_train.jsonl")
    valid_filename = os.path.join(OUTPUT_DIR, f"{NOTE_ID}_valid.jsonl")
    
    # Save Training Data
    with open(train_filename, "w", encoding="utf-8") as f:
        for entry in train_data:
            f.write(json.dumps(entry) + "\n")
            
    # Save Validation Data
    with open(valid_filename, "w", encoding="utf-8") as f:
        for entry in valid_data:
            f.write(json.dumps(entry) + "\n")
            
    print(f"Done!")
    print(f" - Saved to: {train_filename} ({len(train_data)} examples)")
    print(f" - Saved to: {valid_filename} ({len(valid_data)} examples)")