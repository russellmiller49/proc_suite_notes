import json
import random
import os
import datetime

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_034"
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
    "age": ["34", "41", "47", "52", "58", "64", "68", "71", "77", "83", "29", "89"],
    "gender_tuple": [("female", "F", "She"), ("male", "M", "He")],
    "ref_physician": ["Dr. Ingraham", "Dr. Bowers", "Dr. Chen", "Dr. Smith", "Dr. Miller", "Dr. Patel", "Dr. Weiss"],
    "attending": ["Dr. H. Reynolds", "Dr. J. Silva", "Dr. K. O'Malley", "Dr. T. Nguyen", "Dr. A. Gupta"],
    "nurse": ["Sarah, RN", "Mike, RN", "Jessica, RN", "David, RN", "Emily, RN"],
    
    "indication_diagnosis": [
        "pleural effusion and complicated effusion",
        "loculated pleural effusion",
        "complex parapneumonic effusion",
        "retained hemothorax",
        "empyema",
        "malignant pleural effusion with septations"
    ],
    
    "side": ["right", "left"],
    
    "dose_info": [
        {"dose_num": "1", "dose_label": "initial"},
        {"dose_num": "2", "dose_label": "second"},
        {"dose_num": "3", "dose_label": "third"},
        {"dose_num": "4", "dose_label": "fourth"},
        {"dose_num": "5", "dose_label": "fifth"},
        {"dose_num": "6", "dose_label": "final"}
    ],

    "agent_description": [
        "tPA/DNase",
        "Alteplase and Dornase alfa",
        "fibrinolytic agents (tPA and DNase)",
        "intrapleural lytic therapy"
    ],
    
    "tube_days_prior": [1, 2, 3, 4, 5], # How many days ago the tube was placed
}

# Helper to generate dates
def get_dates(days_prior):
    base_date = datetime.date(2025, random.randint(1, 12), random.randint(1, 28))
    proc_date_str = base_date.strftime("%m/%d/%y")
    
    tube_date = base_date - datetime.timedelta(days=days_prior)
    tube_date_str = tube_date.strftime("%m/%d/%y")
    return proc_date_str, tube_date_str

# ==========================================
# 3. TEMPLATES
# ==========================================
note_template = """INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: {proc_date} CC Referred Physician: {ref_physician}

INDICATION FOR OPERATION The patient is a {age}-year-old {gender_long} who presents with a {indication}.
The nature, purpose, risks, benefits, and alternatives to the instillation of agents for fibrinolysis (initial) were discussed with the patient in detail.
The patient indicated a wish to proceed with the procedure and informed consent was signed.

CONSENT Obtained before the procedure.
Indications, potential complications, and alternatives were discussed.

PREOPERATIVE DIAGNOSIS

Pleural Effusion

POSTOPERATIVE DIAGNOSIS

Pleural Effusion

PROCEDURE

Instillation of fibrinolytic agent ({agent_short}) via chest tube (CPT 32561).
ATTENDING {attending}

SUPPORT STAFF RN: {nurse}

COMPLICATIONS None

PROCEDURE IN DETAIL The patient was assessed, and the existing {side}-sided chest tube (inserted on {tube_date}) was identified and checked for patency.
Intrapleural Fibrinolysis Application A solution containing 10 mg of tPA and 5 mg of DNase was prepared.
The area surrounding the chest tube was prepped. The lytic agents were instilled through the chest tube into the pleural space.
This marked Dose #{dose_num} of the therapy regimen.

Following instillation, the tube was clamped to allow the medication to dwell according to protocol.
The patient was instructed to rotate positions to facilitate distribution of the agent.
IMPRESSION / PLAN

{age}-year-old {gender_long} successfully underwent instillation of fibrinolytic agents ({agent_short}) for {indication_short}.
The patient tolerated the procedure well.

There were no immediate complications.

Disposition: Home.
"""

# Prompt Styles
prompt_styles = [
    # Style 1: Telegraphic
    "Gen note: {age}{gender_short}, {indication_short}. {side} chest tube. Dose {dose_num} tPA/DNase. Ref {ref_physician}. No comps.",
    
    # Style 2: Dictation
    "Please generate a procedure note for {attending}. Patient is a {age} year old {gender_long} with {indication}. We instilled the {dose_label} dose of lytics into the {side} tube today. Everything went well.",
    
    # Style 3: Sloppy / Quick
    "{side} side fibrinolysis note. dose #{dose_num}. {age}yo {gender_short}. inserted tube on {tube_date}. ref by {ref_physician}.",
    
    # Style 4: Billing Focus
    "CPT 32561 Instillation of fibrinolytic agent. Dx: {indication_short}. Side: {side}. Dose: {dose_num}. Attending: {attending}.",
    
    # Style 5: Structured
    "Patient: {age} {gender_short}\nDiagnosis: {indication}\nProcedure: tPA/DNase Instillation ({side} side)\nDose: #{dose_num}\nDate: {proc_date}"
]

# ==========================================
# 4. GENERATOR LOGIC
# ==========================================
def generate_dataset():
    dataset = []
    
    for _ in range(NUM_SAMPLES):
        # A. Randomly select variables
        age = random.choice(data_pool["age"])
        gender_tup = random.choice(data_pool["gender_tuple"]) # (long, short, pronoun)
        ref_physician = random.choice(data_pool["ref_physician"])
        attending = random.choice(data_pool["attending"])
        nurse = random.choice(data_pool["nurse"])
        indication = random.choice(data_pool["indication_diagnosis"])
        side = random.choice(data_pool["side"])
        dose_data = random.choice(data_pool["dose_info"])
        agent_desc = random.choice(data_pool["agent_description"])
        
        # Date Logic
        days_prior = random.choice(data_pool["tube_days_prior"])
        proc_date, tube_date = get_dates(days_prior)

        # Derived variables
        indication_short = "complicated effusion" if "complicated" in indication else "pleural effusion"
        agent_short = "tPA/DNase" # Keep this relatively standard for the header/impression

        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_tup[1], 
            gender_long=gender_tup[0],
            indication=indication,
            indication_short=indication_short,
            side=side,
            dose_num=dose_data["dose_num"],
            dose_label=dose_data["dose_label"],
            ref_physician=ref_physician,
            attending=attending,
            tube_date=tube_date,
            proc_date=proc_date
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            # Fixed info
            note_id=NOTE_ID,
            
            # Dynamic info
            proc_date=proc_date,
            ref_physician=ref_physician,
            age=age,
            gender_long=gender_tup[0],
            indication=indication,
            indication_short=indication_short,
            agent_short=agent_short,
            attending=attending,
            nurse=nurse,
            side=side,
            tube_date=tube_date,
            dose_num=dose_data["dose_num"]
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