import json
import random
import os
import datetime

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_033"
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
    "age": ["34", "42", "47", "55", "61", "68", "72", "79", "84"],
    "gender_tuple": [("female", "F"), ("male", "M")],
    "doctor": ["Ingraham", "Bowers", "Chen", "Smith", "Miller", "Jones", "Doe", "Patel", "Weiss"],
    "diagnosis": [
        "Pleural Effusion\n\nComplicated Effusion",
        "Loculated Pleural Effusion\n\nComplicated Effusion",
        "Empyema\n\nComplicated Effusion",
        "Parapneumonic Effusion\n\nComplicated Effusion"
    ],
    "indication_text": [
        "presents with a pleural effusion and complicated effusion",
        "presents with a loculated effusion requiring drainage",
        "presents with a complex septated pleural effusion",
        "presents with findings consistent with empyema"
    ],
    "side": ["right-sided", "left-sided"],
    "agents": [
        "10 mg tPA and 5 mg DNase",
        "10 mg alteplase and 5 mg dornase alfa",
        "tPA (10 mg) and DNase (5 mg)",
        "Alteplase 10 mg and Dornase 5 mg"
    ],
    "cpt_code": ["32561"], # Specific to Initial Day
    "complications": ["None.", "None observed.", "No immediate complications noted.", "Nil."],
    "disposition": ["Home.", "Transferred to floor.", "Remains inpatient.", "Return to ward."]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
# Note Template matching note_033.txt structure
note_template = """INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: {proc_date}

INDICATION FOR OPERATION The patient is a {age}-year-old {gender_long} who {indication_text}.

The nature, purpose, risks, benefits, and alternatives to the instillation of agents for fibrinolysis (initial) were discussed with the patient in detail.

CONSENT The patient indicated a wish to proceed with the procedure and informed consent was signed.

PREOPERATIVE DIAGNOSIS

{diagnosis}

POSTOPERATIVE DIAGNOSIS

{diagnosis}

PROCEDURE

Instillation of agents for fibrinolysis (initial day) via chest tube

CPT: {cpt_code}

MONITORING Pulse oximetry, heart rate, telemetry, and blood pressure were continuously monitored by an independent trained observer throughout the entire procedure.

PROCEDURE IN DETAIL The patient was assessed and the existing {side} chest tube (inserted on {tube_date}) was identified.

The following fibrinolytic agents were instilled via the chest tube:

Agents: {agents}

Dosing: Dose #1

The medication was instilled without difficulty.

COMPLICATIONS {complications}

IMPRESSION / PLAN

{age}-year-old {gender_long} who presents for instillation of agents for fibrinolysis (initial).

The patient tolerated the procedure well.

There were no immediate complications.

Disposition: {disposition}
"""

# 5 Distinct Prompt Styles
prompt_styles = [
    # Style 1: Telegraphic
    "Gen note: {age}{gender_short}, {side} chest tube. Instill {agents} (Dose 1). Dx: {short_dx}. No comps.",
    
    # Style 2: Dictation
    "Please write a procedure note for a {age} year old {gender_long}. We are doing the initial fibrinolysis instillation via the {side} chest tube. Agents used were {agents}. Patient tolerated well.",
    
    # Style 3: Sloppy / Quick
    "{age}yo {gender_short} w/ {short_dx}. {side} tube. gave tpa/dnase initial dose. code {cpt_code}. no issues.",
    
    # Style 4: Billing Focus
    "Procedure CPT {cpt_code}. Service: Instillation of fibrinolysis agents. Pt: {age} {gender_short}. Site: {side}. Agents: {agents}.",
    
    # Style 5: Structured
    "Patient: {age} {gender_short}\nIndication: {short_dx}\nProcedure: Fibrinolysis Instillation (Initial)\nSide: {side}\nDetails: {agents} administered."
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
        gender_long = gender_tup[0]
        gender_short = gender_tup[1]
        
        doctor = random.choice(data_pool["doctor"])
        diagnosis_full = random.choice(data_pool["diagnosis"])
        indication_text = random.choice(data_pool["indication_text"])
        
        # Simplify diagnosis for prompt usage
        short_dx = "complicated effusion"
        if "Empyema" in diagnosis_full:
            short_dx = "empyema"
        
        side = random.choice(data_pool["side"])
        agents = random.choice(data_pool["agents"])
        cpt_code = random.choice(data_pool["cpt_code"])
        complications = random.choice(data_pool["complications"])
        disposition = random.choice(data_pool["disposition"])

        # Date Logic: Procedure date and Chest Tube date (usually same day or previous day)
        year = 2025
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        proc_date_obj = datetime.date(year, month, day)
        proc_date_str = proc_date_obj.strftime("%m/%d/%Y")
        
        # Tube date same as procedure for this scenario (per source context) or 1 day prior
        tube_date_str = proc_date_str 

        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_short, 
            gender_long=gender_long,
            doctor=doctor, 
            side=side,
            agents=agents,
            short_dx=short_dx,
            cpt_code=cpt_code
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            proc_date=proc_date_str,
            age=age, 
            gender_long=gender_long, 
            indication_text=indication_text,
            diagnosis=diagnosis_full,
            cpt_code=cpt_code,
            side=side,
            tube_date=tube_date_str,
            agents=agents,
            complications=complications,
            disposition=disposition
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