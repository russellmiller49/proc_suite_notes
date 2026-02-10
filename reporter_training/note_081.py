import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_081" 
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
    "age": [str(x) for x in range(18, 90)],
    "gender_tuple": [("female", "F"), ("male", "M")],
    "indication": [
        "dyspnea", "chronic cough", "hemoptysis", "abnormal chest imaging", 
        "persistent wheezing", "stridor"
    ],
    "anesthesia": ["General Anesthesia", "Monitored Anesthesia Care (MAC)"],
    "doctor": ["Ingraham", "Bowers", "Chen", "Smith", "Miller", "Jones", "Doe", "Patel"],
    
    # Logic Blocks: Diagnosis must match Findings and Specimen
    "clinical_scenarios": [
        {
            "diagnosis_code": "R91.8",
            "diagnosis_text": "Other nonspecific abnormal finding of lung field",
            "secondary_dx": "Subglottic scarring/stenosis",
            "findings_anatomy": "scarring at the subglottic space, the previous site of stenosis",
            "findings_narrowing": "minimal narrowing",
            "biopsy_site": "subglottic level",
            "specimen": "Subglottic endobronchial biopsies",
            "plan_action": "Subglottic lesion successfully biopsied and removed."
        },
        {
            "diagnosis_code": "J38.6",
            "diagnosis_text": "Stenosis of larynx",
            "secondary_dx": "Tracheal stenosis",
            "findings_anatomy": "circumferential narrowing at the proximal trachea",
            "findings_narrowing": "moderate narrowing (~50%)",
            "biopsy_site": "proximal trachea",
            "specimen": "Tracheal tissue biopsies",
            "plan_action": "Tracheal stenosis dilated and biopsied."
        },
        {
            "diagnosis_code": "D14.3",
            "diagnosis_text": "Benign neoplasm of bronchus and lung",
            "secondary_dx": "Endobronchial lesion RUL",
            "findings_anatomy": "a polypoid lesion within the Right Upper Lobe bronchus",
            "findings_narrowing": "partial obstruction of the RUL orifice",
            "biopsy_site": "RUL bronchus",
            "specimen": "RUL endobronchial biopsies",
            "plan_action": "RUL lesion biopsied."
        },
        {
            "diagnosis_code": "J44.9",
            "diagnosis_text": "Chronic obstructive pulmonary disease",
            "secondary_dx": "Mucous plugging",
            "findings_anatomy": "thick secretions throughout the bronchial tree",
            "findings_narrowing": "mild dynamic airway collapse",
            "biopsy_site": "distal trachea (surveillance)",
            "specimen": "Distal tracheal biopsies",
            "plan_action": "Mucous plugs cleared via aspiration."
        }
    ]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
# The note template preserves the structure of note_081.txt
note_template = """NOTE_ID: {note_id} SOURCE_FILE: {note_id}.txt

INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

INDICATION FOR OPERATION [REDACTED] is a {age}-year-old {gender_long} who presents with {indication}.
The nature, purpose, risks, benefits, and alternatives to bronchoscopy were discussed with the patient in detail.
CONSENT Obtained before the procedure.

Consent Status: The patient wished to proceed and informed consent was obtained.
Discussion: Risks, benefits, and alternatives were discussed in detail.

PREOPERATIVE DIAGNOSIS

{diagnosis_code} {diagnosis_text}.
POSTOPERATIVE DIAGNOSIS

{diagnosis_code} {diagnosis_text}.

{secondary_dx}.

PROCEDURE

Therapeutic aspiration (initial episode).

Diagnostic bronchoscopy with cell washing.
Endobronchial biopsy(s).

ANESTHESIA {anesthesia}.

MONITORING Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.
INSTRUMENTATION Disposable Bronchoscope.

ESTIMATED BLOOD LOSS None.

COMPLICATIONS None.

PROCEDURE IN DETAIL After the successful induction of anesthesia, a timeout was performed (confirming the patient's name, procedure type, and procedure location).
Initial Airway Inspection The airway was inspected. The vocal cords were normal appearing.
Lidocaine was applied to the vocal cords and the airway.
Findings: The airway anatomy was notable for {findings_anatomy}.
There was {findings_narrowing} at this site. The remainder of the airway was normal appearing to the segmental level bilaterally.
Therapeutic Aspiration Successful therapeutic aspiration was performed to clean out mucus from the following segments:

Vocal Cord

Subglottic

Trachea (Proximal 1/3, Middle 1/3, Distal 1/3)

Right Mainstem

Bronchus Intermedius

Left Mainstem

Carina

RUL Carina (RC1)

RML Carina (RC2)

LUL Lingula Carina (Lc1)

Left Carina (LC2)

Endobronchial Biopsy Endobronchial biopsy was performed at the {biopsy_site}.
The lesion was successfully removed. Samples were sent for Pathology.

Conclusion The patient tolerated the procedure well.
There were no immediate complications. At the conclusion of the operation, the patient was extubated in the operating room and transported to the recovery room in stable condition.
SPECIMEN(S)

{specimen}.

IMPRESSION/PLAN

{age}-year-old {gender_long} presented for bronchoscopy for {indication}.

Airway inspection revealed {findings_anatomy} with {findings_narrowing};
remainder of airway normal.

Therapeutic aspiration performed for mucus clearance across multiple segments.

{plan_action}
Plan: Follow-up bronchoscopic lab work.
"""

# Prompt styles mapped to variables
prompt_styles = [
    # Style 1: Telegraphic
    "Gen Bronch report. Pt: {age} {gender_short}. Indication: {indication}. Dx: {diagnosis_code}, {secondary_dx}. Findings: {findings_anatomy}, {findings_narrowing}. Bx: {biopsy_site}. No complications.",
    
    # Style 2: Dictation
    "Please draft an operative note for a {age}-year-old {gender_long} presenting with {indication}. We performed a therapeutic aspiration and diagnostic bronchoscopy. Findings included {findings_anatomy} with {findings_narrowing}. We took biopsies from the {biopsy_site}.",
    
    # Style 3: Sloppy / Quick
    "{age}yo {gender_short} with {indication}. Bronchoscopy showed {findings_anatomy}. Did aspiration and bx of {biopsy_site}. Dx: {secondary_dx}.",
    
    # Style 4: Billing Focus
    "Procedure: Diagnostic Bronchoscopy & Aspiration. Diagnosis: {diagnosis_code} ({diagnosis_text}). Secondary: {secondary_dx}. Specimen: {specimen}. Patient {age}/{gender_short}.",
    
    # Style 5: Structured
    "PATIENT: {age} {gender_short}\nINDICATION: {indication}\nPROCEDURE: Bronchoscopy w/ Biopsy\nFINDINGS: {findings_anatomy}, {findings_narrowing}\nSPECIMEN: {specimen}"
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
        indication = random.choice(data_pool["indication"])
        anesthesia = random.choice(data_pool["anesthesia"])
        
        # B. Select consistent clinical scenario (Logic Syncing)
        scenario = random.choice(data_pool["clinical_scenarios"])
        
        # C. Generate Prompt
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_tup[1], 
            gender_long=gender_tup[0],
            indication=indication,
            diagnosis_code=scenario["diagnosis_code"],
            diagnosis_text=scenario["diagnosis_text"],
            secondary_dx=scenario["secondary_dx"],
            findings_anatomy=scenario["findings_anatomy"],
            findings_narrowing=scenario["findings_narrowing"],
            biopsy_site=scenario["biopsy_site"],
            specimen=scenario["specimen"]
        )
        
        # D. Generate Completion
        completion = note_template.format(
            note_id=NOTE_ID,
            age=age, 
            gender_long=gender_tup[0],
            indication=indication,
            diagnosis_code=scenario["diagnosis_code"],
            diagnosis_text=scenario["diagnosis_text"],
            secondary_dx=scenario["secondary_dx"],
            anesthesia=anesthesia,
            findings_anatomy=scenario["findings_anatomy"],
            findings_narrowing=scenario["findings_narrowing"],
            biopsy_site=scenario["biopsy_site"],
            specimen=scenario["specimen"],
            plan_action=scenario["plan_action"]
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