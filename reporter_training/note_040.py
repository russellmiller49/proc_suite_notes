import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_040"
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
    "age": ["55", "62", "68", "71", "74", "79", "83", "88"],
    "gender_tuple": [("female", "F"), ("male", "M")],
    "ref_physician": [
        "Dr. Ingraham", "Dr. Bowers", "Dr. Chen", "Dr. Smith", 
        "Dr. Patel", "Dr. Rossi", "Dr. Washington"
    ],
    "indication": [
        "Recurrent Effusion", "Symptomatic Pleural Effusion", 
        "Dyspnea secondary to pleural effusion", "Increasing shortness of breath"
    ],
    "sides": ["Right", "Left"],
    "intercostal_space": ["7th", "8th", "9th"],
    "line_location": ["Posterior-axillary line", "Mid-scapular line"],
    "fluid_volume": [
        "450", "600", "750", "900", "1100", "1250", "1400"
    ],
    "fluid_appearance": [
        "Serous", "Serosanguineous", "Straw-colored", 
        "Slightly turbid", "Yellow and clear"
    ],
    "stop_reason": [
        "symptoms (coughing, complaint of dry throat)", 
        "patient started coughing", 
        "patient reported mild chest discomfort", 
        "end of therapeutic goal",
        "chest tightness"
    ],
    "us_large_desc": [
        "Large volume, anechoic echogenicity, with no loculations",
        "Moderate to large volume, anechoic fluid, simple appearance",
        "Significant volume, hypoechoic, free-flowing fluid"
    ],
    "us_small_desc": [
        "Small volume, anechoic echogenicity, with no loculations",
        "Trace to small effusion, no tappable pocket",
        "Minimal fluid observed",
        "No significant effusion"
    ],
    "lung_finding_abnormal": [
        "Consolidation/atelectasis was present",
        "Compressive atelectasis noted",
        "Lower lobe consolidation visible"
    ]
}

# ==========================================
# 3. TEMPLATES
# ==========================================

# The base template follows note_040 structure strictly.
note_template = """NOTE_ID:  {note_id} SOURCE_FILE: {note_id}.txt

INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: [Date] CC Referred Physician: {ref_physician}

INDICATION FOR OPERATION The patient is a {age}-year-old {gender_long} who presents with {indication}.

The nature, purpose, risks, benefits, and alternatives to Chest Ultrasound and Thoracentesis were discussed with the patient in detail.

CONSENT Obtained before the procedure. The patient indicated a wish to proceed with the procedure and informed consent was signed.

PREOPERATIVE DIAGNOSIS

{indication}

POSTOPERATIVE DIAGNOSIS

{indication}

PROCEDURE

Ultrasound, chest (includes mediastinum), real time with image documentation (Bilateral)

Aspirate pleura with imaging (Thoracentesis)

ANESTHESIA Local ONLY.

ESTIMATED BLOOD LOSS None (implied by complication status).

COMPLICATIONS None.

PROCEDURE IN DETAIL

Patient Position: Sitting.

Focused Thoracic Ultrasound (Pleura & Lung) Focused thoracic ultrasound was performed and images were saved and uploaded to the patient's medical record.

Left Chest Findings:

Pleural Effusion: {left_effusion_desc}.

Diaphragm: Normal motion.

Lung: Lung sliding was present before and after the procedure. {left_lung_status}.

Pleura: Normal.

Right Chest Findings:

Pleural Effusion: {right_effusion_desc}.

Diaphragm: Normal motion.

Lung: Lung sliding was present before and after the procedure. {right_lung_status}.

Pleura: Normal.

Thoracentesis Based on ultrasound evaluation, thoracentesis was determined to be feasible and proceeded as planned.

The insertion site was prepped and draped in sterile fashion. A thoracentesis kit was used.

Anesthesia: 10 mL of Lidocaine 1% was administered.

Entry Site: {target_side} {ics} Intercostal Space at the {line_loc}.

Procedure Findings:

Fluid Removed: {vol} mL.

Appearance: {appearance}.

Notes: Drainage was stopped due to {stop_reason}.

Drainage Device: Pleurovac.

Suction: No suction used.

Closure: The site was not sutured.

SPECIMENS Fluid was submitted for the following analyses:

pH

LDH

Glucose

Total Protein

Cholesterol

Cell Count

ADA

Gram Stain/Culture

AFB

Fungal Culture

Cytology

IMPRESSION / PLAN

The patient is a {age}-year-old {gender_long} who presented for Chest Ultrasound and Thoracentesis.

The patient tolerated the procedure well.

There were no immediate complications.

Post-procedure chest x-ray (CXR) ordered.

Follow up pleural studies.

Continued care per primary team.

Disposition: Nursing Unit.
"""

prompt_styles = [
    # Style 1: Telegraphic / Handoff
    "{age}{gender_short}, ref {ref_physician}. Recurrent effusion. US showed {target_side} large, {other_side} small. Drained {vol}mL {appearance} fluid from {target_side} {ics} ICS. Stopped due to {stop_reason_short}. No comps.",
    
    # Style 2: Dictation
    "Please generate a procedure note for a {age} year old {gender_long} referred by {ref_physician}. Indication is {indication}. Ultrasound found a large effusion on the {target_side} and insignificant on the {other_side}. We performed a thoracentesis on the {target_side} removing {vol} mL of {appearance} fluid. Patient tolerated well.",
    
    # Style 3: Sloppy / Quick
    "{age}yo {gender_short} thora. {target_side} side large effusion seen on US. {other_side} normal. {vol}cc {appearance} fluid removed. Stop d/t {stop_reason_short}. {ref_physician} case.",
    
    # Style 4: Billing / Coding Focus
    "Procedure: US Chest + Thoracentesis. Patient: {age} {gender_short}. Dx: {indication}. Site: {target_side} {ics} ICS. Output: {vol} mL {appearance}. Stopped: {stop_reason_short}.",
    
    # Style 5: Structured Request
    "Patient: {age} {gender_short}\nDoctor: {ref_physician}\nUS Findings: {target_side} Large, {other_side} Small\nProcedure: Thoracentesis ({target_side})\nVolume: {vol} mL\nAppearance: {appearance}\nNote: {stop_reason}"
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
        ref_physician = random.choice(data_pool["ref_physician"])
        indication = random.choice(data_pool["indication"])
        
        # Logic for Findings vs Procedure Side
        target_side = random.choice(data_pool["sides"]) # The side with the large effusion
        other_side = "Left" if target_side == "Right" else "Right"
        
        us_large = random.choice(data_pool["us_large_desc"])
        us_small = random.choice(data_pool["us_small_desc"])
        lung_abnormal = random.choice(data_pool["lung_finding_abnormal"])
        lung_normal = "No consolidation or atelectasis was present"
        
        # Assign text blocks based on which side is the target
        if target_side == "Left":
            left_effusion_desc = us_large
            left_lung_status = lung_abnormal
            right_effusion_desc = us_small
            right_lung_status = lung_normal
        else:
            right_effusion_desc = us_large
            right_lung_status = lung_abnormal
            left_effusion_desc = us_small
            left_lung_status = lung_normal
            
        # Procedure Details
        ics = random.choice(data_pool["intercostal_space"])
        line_loc = random.choice(data_pool["line_location"])
        vol = random.choice(data_pool["fluid_volume"])
        appearance = random.choice(data_pool["fluid_appearance"])
        stop_reason = random.choice(data_pool["stop_reason"])
        
        # Shorten stop reason for short prompts
        stop_reason_short = "cough" if "cough" in stop_reason else "symptoms"
        if "goal" in stop_reason: stop_reason_short = "therapeutic goal met"

        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, gender_short=gender_tup[1], gender_long=gender_tup[0],
            ref_physician=ref_physician, indication=indication,
            target_side=target_side, other_side=other_side,
            vol=vol, appearance=appearance, ics=ics,
            stop_reason=stop_reason, stop_reason_short=stop_reason_short
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            age=age, gender_long=gender_tup[0],
            ref_physician=ref_physician, indication=indication,
            left_effusion_desc=left_effusion_desc,
            left_lung_status=left_lung_status,
            right_effusion_desc=right_effusion_desc,
            right_lung_status=right_lung_status,
            target_side=target_side,
            ics=ics, line_loc=line_loc,
            vol=vol, appearance=appearance,
            stop_reason=stop_reason
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