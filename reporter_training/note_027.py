import json
import random
import os
import datetime

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_027" 
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
    "age": ["22", "30", "34", "45", "52", "58", "64", "68", "71", "77", "83"],
    "gender_tuple": [("female", "F", "her"), ("male", "M", "his")],
    "side": ["Left", "Right"],
    "effusion_volume": ["Small", "Moderate", "Large", "Loculated"],
    "echogenicity": ["Anechoic", "Complex non-septated", "Complex septated", "Homogeneous"],
    "loculations": ["Thin", "Thick", "Multiple", "Few", "None"],
    "dose_number": ["1", "2", "3", "4", "5", "6"],
    "tube_date": ["12/29", "01/15", "03/10", "11/05", "05/20", "two days prior", "yesterday"],
    "unclamp_time": ["1:00 PM", "2:30 PM", "3:00 PM", "4:15 PM", "11:00 AM", "12:30 PM"],
    "dwell_time": ["1 hour", "2 hours", "90 minutes"],
    "suction_level": ["-20cm H2O", "-10cm H2O", "-40cm H2O", "water seal"],
    "attending": ["Dr. Smith", "Dr. Chen", "Dr. Rodriguez", "Dr. Kumar", "Dr. White"],
    "pre_dx": ["Complicated Effusion", "Loculated Pleural Effusion", "Empyema", "Parapneumonic Effusion"],
}

# ==========================================
# 3. TEMPLATES
# ==========================================
# The Note Template matches the structure of note_027.txt exactly, substituting dynamic variables.
note_template = """NOTE_ID:  {note_id} SOURCE_FILE: {note_id}.txt

INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT
INDICATION FOR OPERATION The patient is a {age}-year-old {gender_long} who presents with a {dx_lower}.
The nature, purpose, risks, benefits, and alternatives to Chest Ultrasound and Instillation of agents for fibrinolysis (subsequent) were discussed with the patient in detail.
The patient indicated a wish to proceed with the procedure and informed consent was signed.

CONSENT Obtained before the procedure.
Its indications, potential complications, and alternatives were discussed with the patient or surrogate.
The patient or surrogate read and signed the provided consent form (or provided consent over the phone).
The consent was witnessed by an assisting medical professional.

PREOPERATIVE DIAGNOSIS

{dx_proper} 

POSTOPERATIVE DIAGNOSIS

{dx_proper} 

PROCEDURE


76604: Ultrasound, chest (includes mediastinum), real time with image documentation 


32562: Instillation(s), via chest tube/catheter, agent for fibrinolysis (e.g., fibrinolytic agent for break up of multiloculated effusion);
subsequent day 

MONITORING Pulse oximetry, heart rate, telemetry, and blood pressure were continuously monitored by an independent trained observer that was present throughout the entire procedure.
PROCEDURE IN DETAIL
Focused Thoracic Ultrasound Relevant procedural images were saved to the medical record.
Patient Position: Supine 


Hemithorax: {side} 


Pleural Effusion Volume: {volume} 


Echogenicity: {echogenicity} 


Loculations: {loculations} 


Diaphragmatic Motion: Normal 


Lung Sliding: Present before procedure 


Pleura: Normal 

Intrapleural Fibrinolysis Administration The existing chest tube (inserted {tube_date}) on the {side_lower} side was identified.
Agent Instilled: 10 mg tPA / 5 mg DNase 


Dose Number: {dose_num} 

COMPLICATIONS None 

IMPRESSION / PLAN
The patient is a {age}-year-old {gender_long} who presents for Chest Ultrasound and Instillation of agents for fibrinolysis (subsequent).
The patient tolerated the procedure well; there were no immediate complications.
Plan: Allow agents to dwell for {dwell_time}, then unclamp and place back on suction {suction} at {unclamp_time}.
Disposition: Nursing Unit.
"""

# 5 Distinct Prompt Styles
prompt_styles = [
    # Style 1: Telegraphic
    "Write IP op note. {age}yo {gender_short}, {dx_lower}. {side} side US: {volume}, {echogenicity}, {loculations} loculations. Given dose #{dose_num} tPA/DNase. Plan: dwell {dwell_time}, open at {unclamp_time}.",
    
    # Style 2: Dictation
    "Generate a procedure note for a {age} year old {gender_long} with {dx_lower}. We performed a subsequent fibrinolysis instillation. Ultrasound on the {side_lower} showed {volume} {echogenicity} fluid with {loculations} loculations. This was dose number {dose_num}. Tube from {tube_date}. Plan is to unclamp at {unclamp_time} to {suction}.",
    
    # Style 3: Sloppy / Quick
    "{side} chest tube instillation dose {dose_num}. {age} {gender_short}. US: {volume} {echogenicity}. No complications. Unclamp {unclamp_time}. Dx: {dx_proper}.",
    
    # Style 4: Billing Focus
    "CPT 76604, 32562. {age}y {gender_short}. Indication: {dx_proper}. US Findings: {side} hemithorax, {volume}, {echogenicity}. Instilled tPA/DNase dose {dose_num}. Monitoring standard.",
    
    # Style 5: Structured
    "Patient: {age} {gender_short}\nProcedure: US & Fibrinolysis Instillation (Subsequent)\nSide: {side}\nUS Findings: {volume}, {echogenicity}, {loculations} loculations\nDose: #{dose_num}\nPlan: Unclamp @ {unclamp_time}"
]

# ==========================================
# 4. GENERATOR LOGIC
# ==========================================
def generate_dataset():
    dataset = []
    
    for _ in range(NUM_SAMPLES):
        # A. Randomly select variables
        age = random.choice(data_pool["age"])
        gender_tup = random.choice(data_pool["gender_tuple"]) # (long, short, possessive)
        gender_long = gender_tup[0]
        gender_short = gender_tup[1]
        
        side = random.choice(data_pool["side"])
        volume = random.choice(data_pool["effusion_volume"])
        echogenicity = random.choice(data_pool["echogenicity"])
        loculations = random.choice(data_pool["loculations"])
        dose_num = random.choice(data_pool["dose_number"])
        tube_date = random.choice(data_pool["tube_date"])
        unclamp_time = random.choice(data_pool["unclamp_time"])
        dwell_time = random.choice(data_pool["dwell_time"])
        suction = random.choice(data_pool["suction_level"])
        pre_dx = random.choice(data_pool["pre_dx"])
        
        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_short, 
            gender_long=gender_long,
            side=side,
            side_lower=side.lower(),
            volume=volume,
            echogenicity=echogenicity,
            loculations=loculations,
            dose_num=dose_num,
            tube_date=tube_date,
            unclamp_time=unclamp_time,
            dwell_time=dwell_time,
            suction=suction,
            dx_lower=pre_dx.lower(),
            dx_proper=pre_dx
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            age=age, 
            gender_long=gender_long,
            dx_lower=pre_dx.lower(),
            dx_proper=pre_dx,
            side=side,
            side_lower=side.lower(),
            volume=volume,
            echogenicity=echogenicity,
            loculations=loculations,
            tube_date=tube_date,
            dose_num=dose_num,
            dwell_time=dwell_time,
            suction=suction,
            unclamp_time=unclamp_time
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