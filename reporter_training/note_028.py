import json
import random
import os
import datetime

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_028"
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
    "age": ["24", "30", "35", "42", "49", "55", "61", "68", "74", "82"],
    "gender_tuple": [("female", "F"), ("male", "M")],
    "attending": ["Dr. Ingraham", "Dr. Bowers", "Dr. Chen", "Dr. Smith", "Dr. Patel", "Dr. Weiss"],
    "referrer": ["Dr. Miller", "Dr. Jones", "Dr. Doe", "Dr. Ubanks", "Dr. Rossi"],
    "rn_name": ["S. Johnson", "M. Davis", "L. White", "B. King", "J. Adams"],
    
    # Clinical Variables
    "side": ["Left", "Right"],
    "diagnosis": ["Complicated Effusion", "Loculated Pleural Effusion", "Empyema", "Parapneumonic Effusion"],
    "effusion_vol": ["Moderate", "Large", "Small", "Moderate-to-large"],
    "echogenicity": ["Anechoic", "Hypoechoic", "Complex septated", "Heterogeneous"],
    "loculations": [
        "Thin loculations identified", 
        "Multiple septations visualized", 
        "Thick fibrin strands present", 
        "Dense loculations noted",
        "Scattered septations identified"
    ],
    
    # Procedure Details
    # Note: CPT 32562 is for subsequent days (not initial), so we use doses > 1
    "dose_num": ["2", "3", "4", "5", "6"], 
    "tube_dwell_time": ["1 hour", "2 hours", "45 minutes"],
    "suction_time": ["2:00 PM", "3:00 PM", "4:30 PM", "11:00 AM", "1:15 PM"],
    "suction_pressure": ["-20", "-15", "-10", "-25"],
    "tube_insert_date": [
        "yesterday", "2 days ago", "12/29", "01/14", "last week", "10/05"
    ]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
# The template mirrors the structure of note_028.txt
note_template = """NOTE_ID: {note_id} SOURCE_FILE: {note_id}.txt

INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: {date_proc} CC Referred Physician: {referrer}

INDICATION FOR OPERATION {patient_desc} is a {age}-year-old {gender_long} who presents with a {diagnosis_lower}.
The nature, purpose, risks, benefits, and alternatives to Chest Ultrasound and Instillation of agents for fibrinolysis (subsequent) were discussed with the patient in detail.
CONSENT Obtained before the procedure. Its indications, potential complications, and alternatives were discussed with the patient or surrogate.
The patient or surrogate read and signed the provided consent form or provided consent over the phone.
The consent was witnessed by an assisting medical professional.

PREOPERATIVE DIAGNOSIS

{diagnosis}

POSTOPERATIVE DIAGNOSIS

{diagnosis}

PROCEDURE

Ultrasound, chest (includes mediastinum), real time with image documentation (CPT 76604)

Instillation(s), via chest tube/catheter, agent for fibrinolysis (e.g., fibrinolytic agent for break up of multiloculated effusion);
subsequent day (CPT 32562)

ATTENDING {attending}

SUPPORT STAFF RN: {rn_name}

MONITORING Pulse oximetry, heart rate, telemetry, and blood pressure were continuously monitored by an independent trained observer throughout the procedure.
COMPLICATIONS None

PROCEDURE IN DETAIL The patient was placed in the supine position.
Focused Thoracic Ultrasound Focused thoracic ultrasound was performed and images were saved.

Hemithorax: {side}.

Effusion: {volume} volume.

Echogenicity: {echogenicity}.
Loculations: {loculations}.

Lung/Pleura: Diaphragmatic motion was normal. Lung sliding was present before the procedure. The pleura appeared normal.
Intrapleural Fibrinolysis The existing {side_lower} chest tube (inserted {tube_date}) was identified.

Agent Instilled: tPA 10 mg and DNase 5 mg.
Dosing: This represents Dose #{dose_num}.

Technique: The agents were instilled via the chest tube.

The patient tolerated the procedure well.
There were no immediate complications.

IMPRESSION / PLAN

{age}-year-old {gender_long} with {diagnosis_lower} underwent chest ultrasound and instillation of fibrinolytic agents (subsequent).
Tube Management: Allow agents to dwell for {dwell_time}.

Suction: Unclamp and place back on suction {pressure} cmH2O at {suction_time}.
Disposition: Return to Nursing Unit."""

# 5 Distinct Prompt Styles
prompt_styles = [
    # Style 1: Telegraphic
    "IP Note: {age}yo {gender_short}, {diagnosis}, {side} side. Dose #{dose_num} tPA/DNase. US: {volume}, {echogenicity}, {loculations_short}. Ref {referrer}.",
    
    # Style 2: Dictation
    "Please generate an operative report for a {age} year old {gender_long} patient of Dr. {referrer}. Diagnosis is {diagnosis_lower}. We performed a focused chest ultrasound on the {side} showing {volume} effusion with {loculations_short}. We then instilled tPA and DNase, dose number {dose_num}. No complications.",
    
    # Style 3: Sloppy / Quick
    "{side} chest tube lytics dose {dose_num}. {age} {gender_short}. US showed {volume} {echogenicity} fluid. Plan: suction {pressure} at {suction_time}.",
    
    # Style 4: Billing Focus
    "CPT 76604, 32562. {diagnosis}. Patient: {age} {gender_short}. Attending: {attending}. Findings: {side} hemithorax, {loculations_short}. Procedure: Instillation Dose #{dose_num}.",
    
    # Style 5: Structured
    "Patient: {age} {gender_short}\nDiagnosis: {diagnosis}\nSide: {side}\nUS Findings: {volume}, {loculations_short}\nIntervention: Fibrinolysis Dose #{dose_num}\nPlan: Unclamp at {suction_time}"
]

# ==========================================
# 4. GENERATOR LOGIC
# ==========================================
def generate_dataset():
    dataset = []
    
    today_str = datetime.date.today().strftime("%m/%d/%Y")
    
    for _ in range(NUM_SAMPLES):
        # A. Randomly select variables
        age = random.choice(data_pool["age"])
        gender_tup = random.choice(data_pool["gender_tuple"])
        attending = random.choice(data_pool["attending"])
        referrer = random.choice(data_pool["referrer"])
        rn_name = random.choice(data_pool["rn_name"])
        
        side = random.choice(data_pool["side"])
        diagnosis = random.choice(data_pool["diagnosis"])
        volume = random.choice(data_pool["effusion_vol"])
        echogenicity = random.choice(data_pool["echogenicity"])
        loculations = random.choice(data_pool["loculations"])
        
        dose_num = random.choice(data_pool["dose_num"])
        dwell_time = random.choice(data_pool["tube_dwell_time"])
        suction_time = random.choice(data_pool["suction_time"])
        pressure = random.choice(data_pool["suction_pressure"])
        tube_date = random.choice(data_pool["tube_insert_date"])
        
        # Derived variables
        loculations_short = "loculated" if "loculations" in loculations else "septated"
        # Patient descriptor logic (e.g., "[NAME] is a...") - Keeping generic for this template
        patient_desc = " The patient" 
        
        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_tup[1], 
            gender_long=gender_tup[0],
            diagnosis=diagnosis,
            diagnosis_lower=diagnosis.lower(),
            side=side,
            dose_num=dose_num,
            volume=volume,
            echogenicity=echogenicity,
            loculations_short=loculations_short,
            referrer=referrer,
            attending=attending,
            pressure=pressure,
            suction_time=suction_time
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            date_proc=today_str,
            referrer=referrer,
            patient_desc=patient_desc,
            age=age,
            gender_long=gender_tup[0],
            diagnosis=diagnosis,
            diagnosis_lower=diagnosis.lower(),
            attending=attending,
            rn_name=rn_name,
            side=side,
            side_lower=side.lower(),
            volume=volume,
            echogenicity=echogenicity,
            loculations=loculations,
            tube_date=tube_date,
            dose_num=dose_num,
            dwell_time=dwell_time,
            pressure=pressure,
            suction_time=suction_time
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