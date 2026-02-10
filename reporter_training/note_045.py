import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_045"
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
    "age": ["42", "55", "61", "67", "72", "78", "84", "89", "91"],
    "gender_tuple": [("female", "F", "She"), ("male", "M", "He")],
    "ref_physician": ["Dr. Smith", "Dr. Jones", "Dr. Patel", "Dr. Hernandez", "Dr. Lee", "Dr. Ingraham"],
    "attending": ["Dr. Roberts", "Dr. Chen", "Dr. Weiss", "Dr. Al-Fayed", "Dr. Thompson"],
    "nurse": ["Sarah", "Mike", "Jessica", "David", "Emily"],
    "rt_name": ["Tom", "Lisa", "Kevin", "Rachel", "Brian"],
    "side": ["Left", "Right"],
    
    # Ultrasound Findings
    "us_volume": ["Large", "Moderate", "Massive", "Loculated"],
    "us_echo": [
        "anechoic echogenicity with thin loculations", 
        "complex septated appearance", 
        "homogenously echogenic fluid", 
        "anechoic appearance without septations"
    ],
    "diaphragm_motion": ["Diminished", "Normal", "Paradoxical"],
    
    # Thoracentesis Details
    "rib_space": ["6th", "7th", "8th", "9th"],
    "line_location": ["mid-scapular line", "posterior axillary line"],
    "lido_vol": ["5", "10", "15", "20"],
    "fluid_vol": ["150", "350", "500", "750", "1100", "1400"],
    "fluid_appearance": ["Serosanguinous", "Serous", "Straw-colored", "Turbid", "Bloody", "Milky"],
    
    # Dates (Generic relative past)
    "procedure_date": ["January 12, 2024", "February 28, 2024", "March 15, 2024", "April 02, 2024"]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
# Based on note_045.txt
note_template = """INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: {date} CC Referred Physician: {ref_physician}

INDICATION FOR OPERATION {age}-year-old {gender_long} who presents with a pleural effusion.
The nature, purpose, risks, benefits, and alternatives to Chest Ultrasound and Thoracentesis were discussed with the patient in detail.
CONSENT The patient indicated a wish to proceed with the procedure and informed consent was signed.

Obtained before the procedure.
Indications, potential complications, and alternatives were discussed with the patient.
PREOPERATIVE DIAGNOSIS

Pleural Effusion 

POSTOPERATIVE DIAGNOSIS

Pleural Effusion 

PROCEDURE

Ultrasound, chest (includes mediastinum), real time with image documentation (76604) 

Aspirate pleura with imaging (thoracentesis) (32555) 

ATTENDING {attending}

SUPPORT STAFF RN: {rn_name} RT: {rt_name}

ANESTHESIA Local Anesthesia (Lidocaine 1%) 

MONITORING Pulse oximetry, heart rate, telemetry, and blood pressure were continuously monitored by an independent trained observer throughout the procedure.
ESTIMATED BLOOD LOSS Minimal

COMPLICATIONS None 

PROCEDURE IN DETAIL

Chest Ultrasound (CPT 76604) Focused thoracic ultrasound was performed and images were saved and printed.
Hemithorax: {side} 


Pleural Effusion: {us_volume} volume, {us_echo}.


Diaphragmatic Motion: {diaphragm}.


Lung Sliding: Present before procedure.
Pleura: Normal.

Based on ultrasound evaluation, thoracentesis was determined to be feasible and proceeded as planned.
Thoracentesis (CPT 32555) The patient was positioned sitting. The insertion site was identified at the {side} {rib_space} intercostal space along the {line_loc}.
The site was prepped and draped in sterile fashion.

Local anesthesia was achieved using {lido_vol} ml of Lidocaine 1%.
A thoracentesis kit was used. A needle was inserted into the pleural space and fluid was aspirated.
Procedure Findings:


Fluid Removed: {fluid_vol} ml 


Appearance: {fluid_app} 


Drainage Device: Drainage Bag 


Suction: None 

Lung sliding was confirmed present post-procedure.
No lung consolidation or atelectasis was noted. The site was not sutured.
SPECIMENS The following studies were ordered on the pleural fluid:

LDH, Glucose, Total Protein, Cholesterol 

Cell Count 

Gram Stain/Culture, AFB, Fungal Culture 

Cytology 

IMPRESSION / PLAN

{age}-year-old {gender_long} who presents for Chest Ultrasound and Thoracentesis.
Successful ultrasound-guided thoracentesis of {side_lower} {us_volume_lower}, anechoic pleural effusion; {fluid_vol} ml of {fluid_app_lower} fluid removed.
The patient tolerated the procedure well. There were no immediate complications.

Plan:

Follow-up CXR ordered.

Follow-up studies.

Disposition: Nursing Unit.
"""

prompt_styles = [
    # Style 1: Telegraphic / Handoff
    "Generate note: {age}{gender_short}, ref {ref_physician}. {side} effusion ({us_volume}). Tap done {rib_space} ICS. {fluid_vol}ml {fluid_app_lower} removed. No comps.",
    
    # Style 2: Dictation
    "Please write an operative report for Dr. {attending}. Patient is a {age} year old {gender_long} referred by {ref_physician}. We did a bedside ultrasound showing a {us_volume_lower} {side_lower} effusion. We proceeded with thoracentesis at the {rib_space} intercostal space, removing {fluid_vol} ml of {fluid_app_lower} fluid. Patient tolerated well.",
    
    # Style 3: Sloppy / Quick Input
    "thoracentesis note {side} side {age}yo {gender_short}. us showed {us_echo}. drained {fluid_vol}cc {fluid_app_lower}. lido {lido_vol}ml used. rn {rn_name}.",
    
    # Style 4: Billing / CPT Focus
    "Procedure 32555 and 76604. Diagnosis: Pleural Effusion. Side: {side}. Findings: {fluid_vol} ml {fluid_app_lower} fluid. Local anesthesia {lido_vol}ml. Attending {attending}.",
    
    # Style 5: Structured Request
    "PATIENT: {age} {gender_short}\nPROCEDURE: US & Thoracentesis\nSIDE: {side}\nULTRASOUND: {us_volume}, {us_echo}\nFLUID: {fluid_vol}ml, {fluid_app}\nSTAFF: {rn_name} (RN)"
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
        rn_name = random.choice(data_pool["nurse"])
        rt_name = random.choice(data_pool["rt_name"])
        side = random.choice(data_pool["side"])
        us_volume = random.choice(data_pool["us_volume"])
        us_echo = random.choice(data_pool["us_echo"])
        diaphragm = random.choice(data_pool["diaphragm_motion"])
        rib_space = random.choice(data_pool["rib_space"])
        line_loc = random.choice(data_pool["line_location"])
        lido_vol = random.choice(data_pool["lido_vol"])
        fluid_vol = random.choice(data_pool["fluid_vol"])
        fluid_app = random.choice(data_pool["fluid_appearance"])
        date = random.choice(data_pool["procedure_date"])

        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_tup[1], 
            gender_long=gender_tup[0],
            ref_physician=ref_physician,
            attending=attending,
            rn_name=rn_name,
            side=side,
            side_lower=side.lower(),
            us_volume=us_volume,
            us_volume_lower=us_volume.lower(),
            us_echo=us_echo,
            rib_space=rib_space,
            fluid_vol=fluid_vol,
            fluid_app=fluid_app,
            fluid_app_lower=fluid_app.lower(),
            lido_vol=lido_vol
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            date=date,
            ref_physician=ref_physician,
            age=age,
            gender_long=gender_tup[0],
            attending=attending,
            rn_name=rn_name,
            rt_name=rt_name,
            side=side,
            side_lower=side.lower(),
            us_volume=us_volume,
            us_volume_lower=us_volume.lower(),
            us_echo=us_echo,
            diaphragm=diaphragm,
            rib_space=rib_space,
            line_loc=line_loc,
            lido_vol=lido_vol,
            fluid_vol=fluid_vol,
            fluid_app=fluid_app,
            fluid_app_lower=fluid_app.lower()
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