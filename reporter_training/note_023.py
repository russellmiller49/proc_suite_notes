import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_023"
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
    "age": ["62", "65", "68", "71", "74", "77", "81", "85", "89"],
    "gender_tuple": [("female", "F", "She", "Her"), ("male", "M", "He", "His")],
    "doctor": ["Ingraham", "Bowers", "Chen", "Smith", "Miller", "Jones", "Patel", "Weiss"],
    "indication": [
        "hemoptysis after bronchoscopy",
        "post-procedural bleeding",
        "persistent hemoptysis",
        "desaturation and bloody secretions"
    ],
    "old_blocker_loc": [
        "right lower lobe (RLL)",
        "left lower lobe (LLL)",
        "right mainstem bronchus",
        "left mainstem bronchus"
    ],
    "aspiration_target": [
        "left lower lobe (LLL) and left mainstem bronchus (LMSB)",
        "right lower lobe (RLL) and right mainstem bronchus (RMSB)",
        "bilateral mainstem bronchi",
        "left upper lobe (LUL) and lingula"
    ],
    "aspiration_substance": ["mucus", "blood clots", "thick secretions", "copious secretions"],
    "blocker_type": ["Arndt", "Cohen", "Univent", "EZ-Blocker"],
    "blocker_size": ["5 Fr", "7 Fr", "9 Fr"],
    "new_blocker_loc": [
        "distal bronchus intermedius (BI)",
        "left mainstem bronchus (LMSB)",
        "right mainstem bronchus (RMSB)",
        "proximal left lower lobe (LLL)"
    ],
    "inflation_vol": ["3 mL", "4 mL", "5 mL", "2.5 mL", "6 mL"],
    "spared_area": [
        "right upper lobe (RUL)",
        "left upper lobe (LUL)",
        "contralateral lung",
        "trachea"
    ],
    "check_bleeding_loc": [
        "RLL lateral segment",
        "LLL posterior segment",
        "RUL apical segment",
        "LUL anterior segment"
    ],
    "blocker_depth": ["38", "40", "42", "44", "45"],
    "ett_depth": ["20", "21", "22", "23", "24"],
    "rescope_time": ["15:00", "16:30", "18:00", "14:00", "08:00 tomorrow"]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
note_template = """NOTE_ID: {note_id} SOURCE_FILE: {note_id}.txt

INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

INDICATION FOR OPERATION [REDACTED] is a {age}-year-old {gender_long} who presents with {indication}.
The nature, purpose, risks, benefits, and alternatives to bronchoscopy were discussed with the patient in detail.

PREOPERATIVE DIAGNOSIS
Hemoptysis

POSTOPERATIVE DIAGNOSIS
Hemoptysis

PROCEDURE
Therapeutic aspiration initial episode (CPT 31645)
Diagnostic bronchoscopy/cell washing (CPT 31622)
Bronchial blocker exchange and placement

ANESTHESIA Continuous sedation

MONITORING Pulse oximetry, heart rate, telemetry, and blood pressure were continuously monitored by an independent trained observer throughout the procedure.

INSTRUMENTATION Disposable Bronchoscope

ESTIMATED BLOOD LOSS Minimal

COMPLICATIONS None

PROCEDURE IN DETAIL After the successful induction of anesthesia, a timeout was performed confirming the patient's name, procedure type, and procedure location.

Patient Position: Supine.

Initial Airway Inspection The bronchoscope was introduced into the endotracheal tube (ETT).
The ETT was positioned 2 cm above the main carina.
The existing bronchial blocker was identified in the {old_blocker_loc} but was mostly deflated without evidence of spillover into the other segments.

Therapeutic Aspiration Successful therapeutic aspiration was performed to clean out the {aspiration_target} from {aspiration_substance}.

Bronchial Blocker Exchange The existing balloon was fully deflated and then removed.
A new {blocker_size} {blocker_type} bronchial blocker was placed through the existing ETT.
The blocker was positioned in the {new_blocker_loc}.
The balloon was inflated with {inflation_vol} of air, resulting in occlusion of the target airway without occlusion of the {spared_area}.
During the exchange of the bronchial blocker, there was no increase in blood seen in the {check_bleeding_loc}.
This area was not aspirated due to the lack of obvious formed clot.

The bronchoscope was removed.
The patient tolerated the procedure well. There were no immediate complications.

SPECIMENS
None

IMPRESSION / PLAN [REDACTED] is a {age}-year-old {gender_long} who presents for bronchoscopy for hemoptysis.

Keep bronchial blocker in place;
secured at {blocker_depth} cm at the connective device.

Maintain ETT at {ett_depth} cm at the front tooth.

Stop paralysis.
Once paralysis is not effective, stop fentanyl and repeat bronchoscopy at {rescope_time}.

Family updated.
"""

prompt_styles = [
    # Style 1: Telegraphic / Handoff
    "IP Bronch note for {age}y {gender_short}. {indication}. Old blocker in {old_blocker_loc} removed. Suctioned {aspiration_substance} from {aspiration_target}. Placed new {blocker_size} {blocker_type} in {new_blocker_loc}, inflated {inflation_vol}. No active bleed in {check_bleeding_loc}. Secure blocker at {blocker_depth}cm, ETT at {ett_depth}cm.",
    
    # Style 2: Dictation
    "Please generate an operative report for a {age} year old {gender_long} presenting with {indication}. We started by identifying the old blocker in the {old_blocker_loc}. We performed therapeutic aspiration of the {aspiration_target}. We then exchanged the device for a {blocker_size} {blocker_type} placed in the {new_blocker_loc}. Inflated with {inflation_vol}. Plan is to keep ETT at {ett_depth} cm and re-scope at {rescope_time}.",
    
    # Style 3: Sloppy / Quick
    "{age}yo {gender_short} hemoptysis. swapped blocker. old one was in {old_blocker_loc}. cleaned out {aspiration_target}. new {blocker_type} ({blocker_size}) put in {new_blocker_loc}. {inflation_vol} air used. no fresh blood in {check_bleeding_loc}. keep blocker deep at {blocker_depth}cm.",
    
    # Style 4: Billing Focus
    "Procedures: 31645, 31622. Blocker exchange. Pt: {age} {gender_short}. Indication: {indication}. Findings: Aspiration of {aspiration_target}. Placement of {blocker_size} {blocker_type} in {new_blocker_loc} (occlusion with {inflation_vol}). Securement: Blocker {blocker_depth}cm, ETT {ett_depth}cm.",
    
    # Style 5: Structured
    "Patient: {age} {gender_short}\nIndication: {indication}\nAction: Bronchial Blocker Exchange + Aspiration\nAspiration Site: {aspiration_target}\nNew Blocker: {blocker_size} {blocker_type} in {new_blocker_loc}\nSettings: Inflate {inflation_vol}, Secure {blocker_depth}cm\nRescope Plan: {rescope_time}"
]

# ==========================================
# 4. GENERATOR LOGIC
# ==========================================
def generate_dataset():
    dataset = []
    
    for _ in range(NUM_SAMPLES):
        # A. Randomly select variables
        age = random.choice(data_pool["age"])
        gender_tup = random.choice(data_pool["gender_tuple"]) # (long, short, He/She, His/Her)
        gender_long = gender_tup[0]
        gender_short = gender_tup[1]
        
        indication = random.choice(data_pool["indication"])
        old_blocker_loc = random.choice(data_pool["old_blocker_loc"])
        aspiration_target = random.choice(data_pool["aspiration_target"])
        aspiration_substance = random.choice(data_pool["aspiration_substance"])
        
        blocker_type = random.choice(data_pool["blocker_type"])
        blocker_size = random.choice(data_pool["blocker_size"])
        new_blocker_loc = random.choice(data_pool["new_blocker_loc"])
        inflation_vol = random.choice(data_pool["inflation_vol"])
        spared_area = random.choice(data_pool["spared_area"])
        check_bleeding_loc = random.choice(data_pool["check_bleeding_loc"])
        
        blocker_depth = random.choice(data_pool["blocker_depth"])
        ett_depth = random.choice(data_pool["ett_depth"])
        rescope_time = random.choice(data_pool["rescope_time"])
        
        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_short, 
            gender_long=gender_long,
            indication=indication,
            old_blocker_loc=old_blocker_loc,
            aspiration_target=aspiration_target,
            aspiration_substance=aspiration_substance,
            blocker_size=blocker_size,
            blocker_type=blocker_type,
            new_blocker_loc=new_blocker_loc,
            inflation_vol=inflation_vol,
            check_bleeding_loc=check_bleeding_loc,
            blocker_depth=blocker_depth,
            ett_depth=ett_depth,
            rescope_time=rescope_time
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            age=age,
            gender_long=gender_long,
            indication=indication,
            old_blocker_loc=old_blocker_loc,
            aspiration_target=aspiration_target,
            aspiration_substance=aspiration_substance,
            blocker_size=blocker_size,
            blocker_type=blocker_type,
            new_blocker_loc=new_blocker_loc,
            inflation_vol=inflation_vol,
            spared_area=spared_area,
            check_bleeding_loc=check_bleeding_loc,
            blocker_depth=blocker_depth,
            ett_depth=ett_depth,
            rescope_time=rescope_time
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