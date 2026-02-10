import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_043" 
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
    "age": ["45", "52", "58", "61", "64", "67", "72", "75", "81", "88"],
    "gender_tuple": [("female", "F"), ("male", "M")],
    "doctor": ["Dr. Ingraham", "Dr. Bowers", "Dr. Chen", "Dr. Smith", "Dr. Miller", "Dr. Jones", "Dr. Weiss", "Dr. Patel"],
    "date_proc": ["01/10/2026", "03/15/2026", "12/22/2025", "11/05/2025", "06/20/2026"],
    "side": ["left", "right"],
    "diagnosis": ["Complicated Effusion", "Loculated Pleural Effusion", "Empyema", "Parapneumonic Effusion"],
    "us_volume": ["Small volume", "Moderate volume", "Large volume", "Decreased volume"],
    "us_echo": ["anechoic echogenicity", "complex septated echogenicity", "heterogeneous echogenicity", "swirling debris"],
    "loculations": ["Thin", "Thick", "Multiloculated", "Dense septations"],
    "diaphragm": ["Normal", "Paradoxical motion", "Elevated hemidiaphragm"],
    "lung_sliding": ["absent", "present"],
    "lung_consolidation": ["Lung consolidation/atelectasis was present", "Trapped lung physiology noted", "Significant atelectasis noted"],
    "pleura_desc": ["Thick", "Nodular", "Smooth", "Irregular"],
    "meds_combo": [("tPA / DNase", "5 mg tPA / 5 mg DNase"), ("Alteplase / Dornase", "10 mg Alteplase / 5 mg Dornase"), ("tPA / DNase", "10 mg tPA / 5 mg DNase")],
    "dose_num": ["2", "3", "4", "5", "6"],
    "unclamp_time": ["1 hour", "45 minutes", "2 hours", "90 minutes"],
    "complications": ["None", "None", "None", "None", "None", "Minor pain at site"] # Weighted heavily towards None
}

# ==========================================
# 3. TEMPLATES
# ==========================================
# Use {placeholders} for dynamic data.
note_template = """NOTE_ID:  {note_id} SOURCE_FILE: {note_id}.txt

INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT


DATE OF PROCEDURE: {date_proc} 

INDICATION FOR OPERATION The patient is a {age}-year-old {gender_long} who presents with a {diagnosis}.
The nature, purpose, risks, benefits, and alternatives to Chest Ultrasound and Instillation of agents for fibrinolysis (subsequent) were discussed with the patient in detail.
The patient indicated a wish to proceed with the procedure and informed consent was signed.
PREOPERATIVE DIAGNOSIS {diagnosis} 

POSTOPERATIVE DIAGNOSIS {diagnosis} 

PROCEDURE

Ultrasound, chest (includes mediastinum), real time with image documentation (CPT 76604) 

Instillation(s), via chest tube/catheter, agent for fibrinolysis (eg, fibrinolytic agent for break up of multiloculated effusion);
subsequent day (CPT 32562) 

COMPLICATIONS {complications} 

PROCEDURE IN DETAIL

Chest Ultrasound Bedside chest ultrasound was performed on the {side} hemithorax.
Images were saved and uploaded to the patient's medical record.


Pleural Effusion: {us_volume}, {us_echo}.


Loculations: {loculations}.
Diaphragmatic Motion: {diaphragm}.

Lung: Lung sliding was {lung_sliding} before and after the procedure. {lung_consolidation}.


Pleura: {pleura_desc}.
Fibrinolytic Instillation The patient's identity and the correct side ({side}) were verified.
Via the existing chest tube inserted on {date_insert}:


Medication: {med_name} 


Dose: {med_dose} 


Dose Number: {dose_num} 

The patient tolerated the procedure well.
There were no immediate complications.

IMPRESSION / PLAN {age}-year-old {gender_long} who presents for Chest Ultrasound and Instillation of agents for fibrinolysis (subsequent).
Unclamp chest tube in {unclamp_time}.

Continue strict I/O.

Continue daily CXR while chest tube in place.
Continue nursing chest tube flushing protocol.


Disposition: Nursing Unit.
"""

# <--- CREATE 5 DISTINCT PROMPT STYLES HERE --->
prompt_styles = [
    # Style 1: Telegraphic
    "Generate IP note. {age}{gender_short}, {diagnosis}. {side} side. US: {us_volume}, {loculations}. Dose #{dose_num} of {med_name}. Unclamp {unclamp_time}.",
    
    # Style 2: Dictation
    "Please write a procedure note for a {age} year old {gender_long} with a {diagnosis}. We performed a bedside ultrasound and subsequent fibrinolytic instillation on the {side}. Ultrasound showed {us_volume} with {loculations} loculations. We gave dose number {dose_num} of {med_name}.",
    
    # Style 3: Sloppy / Quick
    "{side} side lytics dose {dose_num}. {age}yo {gender_short}. US showed {us_echo}, {pleura_desc} pleura. Plan unclamp {unclamp_time}.",
    
    # Style 4: Billing Focus
    "Procedure codes 76604 and 32562. {age} year old {gender_long}. Dx: {diagnosis}. {side} hemithorax US findings: {us_volume}. Meds: {med_dose}. Comps: {complications}.",
    
    # Style 5: Structured
    "Patient: {age} {gender_short}\nDiagnosis: {diagnosis}\nProcedure: Chest US + Subsequent Instillation\nSide: {side}\nUS Findings: {us_volume}, {us_echo}\nDose: #{dose_num} ({med_name})\nPlan: Unclamp in {unclamp_time}"
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
        date_proc = random.choice(data_pool["date_proc"])
        # Logic: Insert date is same as proc date for simplicity in this template, 
        # or we could make it a fixed string, but let's re-use date_proc to simulate recent placement
        date_insert = date_proc 
        
        side = random.choice(data_pool["side"])
        diagnosis = random.choice(data_pool["diagnosis"])
        
        us_volume = random.choice(data_pool["us_volume"])
        us_echo = random.choice(data_pool["us_echo"])
        loculations = random.choice(data_pool["loculations"])
        diaphragm = random.choice(data_pool["diaphragm"])
        lung_sliding = random.choice(data_pool["lung_sliding"])
        lung_consolidation = random.choice(data_pool["lung_consolidation"])
        pleura_desc = random.choice(data_pool["pleura_desc"])
        
        med_tup = random.choice(data_pool["meds_combo"])
        med_name = med_tup[0]
        med_dose = med_tup[1]
        
        dose_num = random.choice(data_pool["dose_num"])
        unclamp_time = random.choice(data_pool["unclamp_time"])
        complications = random.choice(data_pool["complications"])
        
        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, gender_short=gender_short, gender_long=gender_long,
            diagnosis=diagnosis, side=side, us_volume=us_volume, 
            loculations=loculations, dose_num=dose_num, med_name=med_name,
            unclamp_time=unclamp_time, us_echo=us_echo, pleura_desc=pleura_desc,
            med_dose=med_dose, complications=complications
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            date_proc=date_proc,
            age=age,
            gender_long=gender_long,
            diagnosis=diagnosis,
            complications=complications,
            side=side,
            us_volume=us_volume,
            us_echo=us_echo,
            loculations=loculations,
            diaphragm=diaphragm,
            lung_sliding=lung_sliding,
            lung_consolidation=lung_consolidation,
            pleura_desc=pleura_desc,
            date_insert=date_insert,
            med_name=med_name,
            med_dose=med_dose,
            dose_num=dose_num,
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