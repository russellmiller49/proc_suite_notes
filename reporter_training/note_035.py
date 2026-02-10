import json
import random
import os
import datetime

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_035"
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
    "age": [str(x) for x in range(25, 95)],
    "gender_tuple": [("female", "F", "her"), ("male", "M", "his")],
    "indication": [
        "complicated effusion",
        "multiloculated pleural effusion",
        "loculated empyema",
        "parapneumonic effusion with loculations",
        "fibrinopurulent effusion"
    ],
    "side": ["right", "left"],
    "tpa_dose": ["10 mg", "5 mg"],  # Standard is usually 10, sometimes reduced
    "dnase_dose": ["5 mg"],
    "dose_number": ["1", "2", "3", "4", "5", "6"],
    "chest_tube_days_prior": [1, 2, 3, 4, 5, 7, 10], # How many days ago tube was inserted
    "complications": ["None", "None", "None", "None", "Mild discomfort during injection", "Transient cough"]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
# Note Template matching note_035.txt structure
note_template = """INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: {proc_date} PATIENT: [REDACTED] ID: [MRN]

INDICATION FOR OPERATION The patient is a {age}-year-old {gender_long} who presents with a {indication}.
The nature, purpose, risks, benefits, and alternatives to the instillation of agents for fibrinolysis (subsequent) were discussed with the patient in detail.
The patient indicated a wish to proceed with the procedure and informed consent was signed.

CONSENT Obtained before the procedure.
Its indications, potential complications, and alternatives were discussed with the patient or surrogate.
The patient or surrogate read and signed the provided consent form (or provided consent over the phone).
The consent was witnessed by an assisting medical professional.

PREOPERATIVE DIAGNOSIS

{indication_title}

POSTOPERATIVE DIAGNOSIS

{indication_title}

PROCEDURE

Instillation of fibrinolytic agent (tPA/DNase) via chest tube, subsequent day (CPT 32562)

COMPLICATIONS {complication}

PROCEDURE IN DETAIL

The patient was positioned in the supine position.
The existing {side}-sided chest tube (inserted on {insert_date}) was identified and the dressing was inspected.
Using sterile technique, the chest tube was accessed. Intrapleural fibrinolysis was performed to address the multiloculated effusion.
Agent(s): tPA ({tpa_dose}) and DNase ({dnase_dose}).


Dose Number: {dose_num}.

The agents were successfully instilled through the chest tube.
The tube was clamped/capped to allow for the prescribed dwell time according to protocol.
IMPRESSION / PLAN

{age}-year-old {gender_long} with {indication} underwent subsequent instillation of fibrinolytic agents (Dose #{dose_num}).
The patient tolerated the procedure well.

There were no immediate complications."""

# 5 Distinct Prompt Styles
prompt_styles = [
    # Style 1: Telegraphic
    "Gen note for {age}yo {gender_short}. {indication}, {side} CT placed {insert_date}. Dose #{dose_num} tPA/DNase. No comps.",
    
    # Style 2: Dictation
    "Please record a procedure note for a {age} year old {gender_long} with a {indication}. We instilled dose number {dose_num} of lytics into the {side} chest tube which was placed on {insert_date}. Tolerance was good.",
    
    # Style 3: Sloppy / Quick
    "{side} side lysis dose {dose_num}. {age} {gender_short} with {indication}. Tube from {insert_date}. tPA {tpa_dose} used.",
    
    # Style 4: Billing Focus
    "CPT 32562 Instillation of fibrinolytic agent. Pt: {age} {gender_short}. Dx: {indication}. Side: {side}. Dose #: {dose_num}. Tube date: {insert_date}.",
    
    # Style 5: Structured
    "Patient: {age} {gender_short}\nDiagnosis: {indication}\nProcedure: Intrapleural fibrinolysis ({side})\nDose: #{dose_num}\nTube Inserted: {insert_date}"
]

# ==========================================
# 4. GENERATOR LOGIC
# ==========================================
def generate_random_date():
    """Generates a random date within the last year."""
    start_date = datetime.date.today() - datetime.timedelta(days=365)
    random_days = random.randint(0, 365)
    return start_date + datetime.timedelta(days=random_days)

def generate_dataset():
    dataset = []
    
    for _ in range(NUM_SAMPLES):
        # A. Randomly select variables
        age = random.choice(data_pool["age"])
        gender_tup = random.choice(data_pool["gender_tuple"])
        gender_long = gender_tup[0]
        gender_short = gender_tup[1]
        
        indication = random.choice(data_pool["indication"])
        side = random.choice(data_pool["side"])
        tpa_dose = random.choice(data_pool["tpa_dose"])
        dnase_dose = random.choice(data_pool["dnase_dose"])
        dose_num = random.choice(data_pool["dose_number"])
        complication = random.choice(data_pool["complications"])
        
        # Date Logic
        proc_date_obj = generate_random_date()
        days_prior = random.choice(data_pool["chest_tube_days_prior"])
        insert_date_obj = proc_date_obj - datetime.timedelta(days=days_prior)
        
        proc_date_str = proc_date_obj.strftime("%m/%d/%y")
        insert_date_str = insert_date_obj.strftime("%m/%d/%y")
        
        # Capitalize Indication for Title sections
        indication_title = indication.title()

        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_short, 
            gender_long=gender_long,
            indication=indication,
            side=side,
            dose_num=dose_num,
            insert_date=insert_date_str,
            tpa_dose=tpa_dose
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            proc_date=proc_date_str,
            age=age,
            gender_long=gender_long,
            indication=indication,
            indication_title=indication_title,
            side=side,
            insert_date=insert_date_str,
            tpa_dose=tpa_dose,
            dnase_dose=dnase_dose,
            dose_num=dose_num,
            complication=complication
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