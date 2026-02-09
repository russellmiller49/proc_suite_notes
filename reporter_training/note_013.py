import json
import random
import os
import datetime

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_013" 
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
    "age": [str(x) for x in range(25, 85)],
    "gender_tuple": [("female", "F"), ("male", "M")],
    "indication_dx": [
        "Aspergilloma", "Invasive Aspergillosis", "Pulmonary Mycetoma", 
        "Fungal Ball", "Chronic Cavitary Aspergillosis"
    ],
    "sedation_time": ["65", "72", "83", "90", "105", "110"],
    "secretion_type": [
        "Moderate bloody secretions", 
        "Copious purulent secretions", 
        "Thick mucoid secretions", 
        "Tenacious fungal debris and secretions",
        "Scant hemopurulent secretions"
    ],
    "drug_name": ["Amphotericin", "Voriconazole", "Amphotericin B"],
    "drug_dose": ["50mg", "40mg", "30mg", "100mg"],
    "drug_vol": ["20cc", "10cc", "40cc"],
}

# LOGIC SYNC: Anatomy must match the side (Right vs Left)
# If we inject RUL, the blocker should be in RMSB, and segments are RB1/RB2, etc.
anatomy_logic = [
    {
        "target_lobe": "Left Upper Lobe (LUL)",
        "target_lobe_short": "LUL",
        "blocker_loc": "Left Mainstem Bronchus (LMSB)",
        "seg_1": "apico-posterior (LB1/2)",
        "seg_2": "anterior (LB3)",
        "secretion_dominance": "left greater than right",
        "carina_list": "Left Mainstem, Left Carina (LC2), LUL Lingula Carina (Lc1)"
    },
    {
        "target_lobe": "Right Upper Lobe (RUL)",
        "target_lobe_short": "RUL",
        "blocker_loc": "Right Mainstem Bronchus (RMSB)",
        "seg_1": "apical (RB1)",
        "seg_2": "posterior (RB2)",
        "secretion_dominance": "right greater than left",
        "carina_list": "Right Mainstem, Bronchus Intermedius, RUL Carina (RC1)"
    }
]

# ==========================================
# 3. TEMPLATES
# ==========================================

note_template = """NOTE_ID: {note_id}
DATE OF PROCEDURE: [Date]
INDICATION FOR OPERATION: Patient is a {age}-year-old {gender_long} who presents with respiratory failure and {indication_dx}.

The nature, purpose, risks, benefits, and alternatives to Bronchoscopy were discussed with the patient in detail.
CONSENT Obtained before the procedure. Indications, potential complications, and alternatives were discussed with the patient or surrogate.
The patient or surrogate read and signed the provided consent form or provided consent over the phone.
The consent was witnessed by an assisting medical professional.

PREOPERATIVE DIAGNOSIS
J96.90 Respiratory Failure
{indication_dx}

POSTOPERATIVE DIAGNOSIS
J96.90 Respiratory Failure
{indication_dx}

PROCEDURE
Therapeutic aspiration initial episode (CPT 31645)
Therapeutic injection(s) [eg, chemotherapy denervation agent or corticosteroid] (CPT 31573)

ANESTHESIA
Moderate Sedation: Initial 15 minutes (99152); each additional 15 minutes (99153). Total Time: {sedation_time} minutes.
Medications:
Etomidate 20 mg
Rocuronium 50 mg
Dexmedetomidine gtt 1 mcg/kg/hr
Propofol gtt 40 mcg/kg/min
Fentanyl gtt 150 mcg/hr

MONITORING Pulse oximetry, heart rate, telemetry, and blood pressure were continuously monitored by an independent trained observer throughout the procedure.
The patient was monitored continuously one-to-one throughout the entire procedure by the attending physician while anesthesia was administered.
INSTRUMENTATION Disposable Bronchoscope.

ESTIMATED BLOOD LOSS None.
COMPLICATIONS None.

PROCEDURE IN DETAIL After the successful induction of anesthesia, a timeout was performed confirming the patient's name, procedure type, and procedure location.
Patient Position: Supine

Initial Airway Inspection The bronchoscope was introduced through the tracheostomy tube.
Tracheostomy: Tube is in good position.
Upper Airway: Pharynx, Larynx, and Vocal Cords were not assessed due to introduction through tracheostomy tube.
Trachea: Distal 1/3 normal.
Carina: Sharp.
Proximal Airways: Right and Left lung proximal airways showed normal anatomic branching to the segmental level.
Mucosa: Normal.
Secretions: {secretion_type} with {secretion_dominance}.
Additional Findings: Uniblocker in place (deflated) at the {blocker_loc}.

Therapeutic Aspiration Successful therapeutic aspiration was performed to clean out mucus, blood, and blood clots from the following segments:
Trachea (Distal 1/3)
Right Mainstem, Bronchus Intermedius, RUL Carina (RC1), RML Carina (RC2)
Left Mainstem, Left Carina (LC2), LUL Lingula Carina (Lc1)

Therapeutic Injection {drug_name} {drug_dose} in {drug_vol} sterile water was instilled into the {target_lobe} as follows:
10cc into the {seg_1} subsegment
10cc into the {seg_2} subsegment

Completion The patient tolerated the procedure well.
There were no immediate complications. At the conclusion of the operation, the patient was in stable condition.

SPECIMENS None.

IMPRESSION / PLAN
{age}-year-old {gender_long} presented for bronchoscopy for instillation of {drug_name}.
{target_lobe_short} {drug_name} instillation successfully performed.
Patient tolerated the procedure well; no immediate complications.
Continued care per primary team.
Repeat instillation of {drug_name} planned.
"""

# <--- CREATE 5 DISTINCT PROMPT STYLES HERE --->
prompt_styles = [
    # Style 1: Telegraphic / Handoff
    "Interventional Pulm Note. Pt: {age} {gender_short}. Dx: {indication_dx}. Procedure: Bronch with {drug_name} injection to {target_lobe_short}. Findings: {secretion_type}. Trach access.",
    
    # Style 2: Dictation Style
    "Generate an operative report for a {age} year old {gender_long} with {indication_dx}. We performed therapeutic aspiration and injection of {drug_name} {drug_dose} into the {target_lobe_short}. Note the use of a uniblocker in the {blocker_loc}.",
    
    # Style 3: Sloppy / Quick
    "{age}yo {gender_short} with {indication_dx}, bronch done through trach. {secretion_type} seen. {drug_name} injected {target_lobe_short} ({seg_1}, {seg_2}). no complications.",
    
    # Style 4: Billing / Coding Focus
    "CPT 31645, 31573. Diagnosis J96.90 and {indication_dx}. Procedure: Instillation of {drug_name} to {target_lobe_short} via Trach. Anesthesia time {sedation_time} min.",
    
    # Style 5: Structured Request
    "PROCEDURE: Bronchoscopy with Therapeutic Injection\nPATIENT: {age} {gender_short}\nINDICATION: {indication_dx}\nTARGET: {target_lobe_short}\nDRUG: {drug_name}\nFINDINGS: {secretion_type}"
]

# ==========================================
# 4. GENERATOR LOGIC
# ==========================================

def generate_dataset():
    dataset = []
    
    for _ in range(NUM_SAMPLES):
        # A. Randomly select independent variables
        age = random.choice(data_pool["age"])
        gender_tup = random.choice(data_pool["gender_tuple"])
        indication_dx = random.choice(data_pool["indication_dx"])
        sedation_time = random.choice(data_pool["sedation_time"])
        secretion_type = random.choice(data_pool["secretion_type"])
        drug_name = random.choice(data_pool["drug_name"])
        drug_dose = random.choice(data_pool["drug_dose"])
        drug_vol = random.choice(data_pool["drug_vol"])
        
        # B. Select Anatomy Logic (ensures side consistency)
        anatomy = random.choice(anatomy_logic)
        
        # C. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_tup[1], 
            gender_long=gender_tup[0],
            indication_dx=indication_dx,
            target_lobe_short=anatomy["target_lobe_short"],
            drug_name=drug_name,
            secretion_type=secretion_type,
            blocker_loc=anatomy["blocker_loc"],
            seg_1=anatomy["seg_1"],
            seg_2=anatomy["seg_2"],
            sedation_time=sedation_time
        )
        
        # D. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            age=age, 
            gender_long=gender_tup[0],
            indication_dx=indication_dx,
            sedation_time=sedation_time,
            secretion_type=secretion_type,
            secretion_dominance=anatomy["secretion_dominance"],
            blocker_loc=anatomy["blocker_loc"],
            drug_name=drug_name,
            drug_dose=drug_dose,
            drug_vol=drug_vol,
            target_lobe=anatomy["target_lobe"],
            target_lobe_short=anatomy["target_lobe_short"],
            seg_1=anatomy["seg_1"],
            seg_2=anatomy["seg_2"]
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