import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_016" 
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
    "age": ["28", "33", "45", "52", "61", "67", "74", "81"],
    "gender_tuple": [("female", "F", "She", "Her"), ("male", "M", "He", "His")],
    "doctor": ["Hudson", "Patel", "Weiss", "Gomez", "Alvarez", "Smith"],
    "diagnosis_tuple": [
        ("J96.90", "Respiratory Failure"),
        ("J96.00", "Acute Respiratory Failure"),
        ("J96.01", "Acute Respiratory Failure with Hypoxia"),
        ("J96.21", "Acute on Chronic Respiratory Failure")
    ],
    "surrogate_tuple": [
        ("mother", "Yvette Sese"),
        ("spouse", "John Doe"),
        ("daughter", "Sarah Jenkins"),
        ("son", "Michael Chang"),
        ("sister", "Maria Garcia")
    ],
    "sedation_meds": [
        "Versed: 4 mg\nDilaudid: 6 mg\nEtomidate: 20 mg\nRocuronium: 63 mg x 2\nPropofol: 60 mcg/kg/min",
        "Versed: 2 mg\nFentanyl: 100 mcg\nPropofol: 80 mcg/kg/min",
        "Midazolam: 5 mg\nFentanyl: 150 mcg\nRocuronium: 50 mg\nPropofol: 50 mcg/kg/min"
    ],
    "us_findings": [
        "No significant vessels or masses were noted overlying the tracheostomy site on examination from the laryngeal prominence to the sternal notch.",
        "A high-riding innominate artery was noted just superior to the sternal notch.",
        "A small thyroid nodule was noted near the suprasternal notch, avoiding the midline.",
        "Minor vasculature noted, easily avoidable with standard technique."
    ],
    "secretion_type": [
        "Copious thick and thin, light yellow",
        "Moderate amount of thick white",
        "Scant blood-tinged",
        "Copious purulent green",
        "Tenacious tan-colored"
    ],
    "segments_cleared": [
        "Trachea (Distal 1/3)\nRight Mainstem\nBronchus Intermedius\nLeft Mainstem\nCarina\nRUL Carina (RC1)\nRML Carina (RC2)\nLUL Lingula Carina (Lc1)\nLeft Carina (LC2)",
        "Trachea and bilateral mainstems only",
        "Right lower lobe segments and Left lower lobe segments",
        "Diffuse suctioning of all visualized segments"
    ],
    "trach_plan": ["7", "10", "14"]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
note_template = """NOTE_ID: {note_id}
SOURCE_FILE: {note_id}.txt

INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: [Date]
CC Referred Physician: Dr. {doctor}
INDICATION FOR OPERATION
The patient is a {age}-year-old {gender_long} who presents with {dx_name} ({dx_code}).
The nature, purpose, risks, benefits, and alternatives to Bronchoscopy and Tracheostomy were discussed with the patient's surrogate ({surrogate_rel}, {surrogate_name}) in detail.
The patient was unable to participate in the discussion due to sedation and intubation.

CONSENT
Obtained before the procedure. Its indications, potential complications, and alternatives were discussed with the patient or surrogate. The patient's surrogate indicated a wish to proceed, and informed consent was signed. The consent was witnessed by an assisting medical professional.

PREOPERATIVE DIAGNOSIS
{dx_code} {dx_name}

POSTOPERATIVE DIAGNOSIS
{dx_code} {dx_name}

PROCEDURE
31645 Therapeutic aspiration, initial episode
76536 Ultrasound of Neck

ANESTHESIA
Moderate Sedation (CPT 99152, 99153):
Start Time: 1543
Stop Time: 1822
Total Time: 159 minutes

Medications Administered:
{sedation_block}

Sedation was administered by the ICU RN. The patient was monitored continuously one-to-one throughout the entire procedure by the attending physician while anesthesia was administered.

MONITORING
Pulse oximetry, heart rate, telemetry, and blood pressure were continuously monitored by an independent trained observer throughout the procedure.

INSTRUMENTATION
Flexible Therapeutic Bronchoscope; Ultrasound.

ESTIMATED BLOOD LOSS
Minimal

COMPLICATIONS
None

PROCEDURE IN DETAIL
After the successful induction of anesthesia, a timeout was performed confirming the patient's name, procedure type, and procedure location.
Patient Position: Supine

Neck Ultrasound
A neck ultrasound was performed to evaluate for any abnormal vessels, masses, or structures at the site of the planned percutaneous tracheostomy.
Findings: {us_finding_text}

Bronchoscopy and Airway Inspection
The bronchoscope was introduced through the endotracheal tube (ETT).

ETT: Good position.
Pharynx/Larynx/Vocal Cords: Not assessed due to introduction via ETT.
Trachea: Distal 1/3 normal.
Main Carina: Sharp.
Right Lung: Proximal airways demonstrated normal anatomic branching to the segmental level. No evidence of mass, lesions, or bleeding.
Left Lung: Proximal airways demonstrated normal anatomic branching to the segmental level. No evidence of mass, lesions, or bleeding.
Mucosa: Normal.
Secretions: {secretion_desc} secretions/mucus noted throughout.

Therapeutic Intervention
Successful therapeutic aspiration was performed to clear mucus from the following segments:
{segments_list}

Conclusion
The patient tolerated the procedure well. There were no immediate complications. At the conclusion of the operation, the patient's endotracheal tube was removed (following tracheostomy placement by surgery), and the patient was in stable condition.

SPECIMENS
None

IMPRESSION / PLAN
{age}-year-old {gender_long} with {dx_name}, underwent bronchoscopy and tracheostomy placement.
Note: See separate documentation from Dr. {doctor} for the modified open tracheostomy.
Patient tolerated the procedure well; no complications.
Obtain post-procedure Chest X-Ray.
Anticipate suture removal in ~7 days.
Anticipate trach exchange in ~{trach_days} days.
"""

prompt_styles = [
    # Style 1: Telegraphic / Brief
    "Pt {age} {gender_short}, ref {doctor}. Dx: {dx_code}. Proc: Bronch tx aspiration + Neck US. Findings: {us_short_summary}. Secretions: {secretion_short}. Plan: trach exchange ~{trach_days} days.",
    
    # Style 2: Dictation style
    "Please generate an operative report for a {age} year old {gender_long} referred by Dr. {doctor} for {dx_name}. We performed a therapeutic bronchoscopy and neck ultrasound. Ultrasound showed {us_short_summary}. We cleared {secretion_short} secretions. No complications.",
    
    # Style 3: Sloppy / Quick Handoff
    "{age}yo {gender_short} {dx_code}. bronch and US done. US found {us_short_summary}. suctioned {secretion_short} mucus. pt stable. ref doctor {doctor}.",
    
    # Style 4: Billing / Coding focus
    "Codes 31645, 76536. Diagnosis {dx_code}. {age} {gender_short}. US Neck: {us_short_summary}. Bronch: Aspiration of {secretion_short} secretions. Sedation used.",
    
    # Style 5: Structured Request
    "PATIENT: {age} {gender_short}\nREFERRING: Dr. {doctor}\nDIAGNOSIS: {dx_name}\nPROCEDURE: Bronchoscopy with Therapeutic Aspiration & Neck US\nUS FINDINGS: {us_short_summary}\nSECRETIONS: {secretion_short}"
]

# ==========================================
# 4. GENERATOR LOGIC
# ==========================================
def generate_dataset():
    dataset = []
    
    for _ in range(NUM_SAMPLES):
        # A. Randomly select variables
        age = random.choice(data_pool["age"])
        gender_tup = random.choice(data_pool["gender_tuple"]) # (long, short, He/She, His/Her)
        doctor = random.choice(data_pool["doctor"])
        dx_tup = random.choice(data_pool["diagnosis_tuple"]) # (code, name)
        surrogate_tup = random.choice(data_pool["surrogate_tuple"]) # (rel, name)
        sedation_block = random.choice(data_pool["sedation_meds"])
        
        us_full = random.choice(data_pool["us_findings"])
        # Create a short summary for the prompt based on the full finding
        if "high-riding" in us_full:
            us_short = "high-riding innominate artery"
        elif "nodule" in us_full:
            us_short = "thyroid nodule"
        elif "No significant" in us_full:
            us_short = "no abnormal vessels"
        else:
            us_short = "minor vasculature"

        secretion_full = random.choice(data_pool["secretion_type"])
        # Create short summary for prompt
        if "yellow" in secretion_full:
            secretion_short = "thick yellow"
        elif "green" in secretion_full:
            secretion_short = "purulent green"
        elif "blood" in secretion_full:
            secretion_short = "blood-tinged"
        elif "white" in secretion_full:
            secretion_short = "thick white"
        else:
            secretion_short = "tenacious tan"

        segments_list = random.choice(data_pool["segments_cleared"])
        trach_days = random.choice(data_pool["trach_plan"])

        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_tup[1], 
            gender_long=gender_tup[0],
            doctor=doctor,
            dx_code=dx_tup[0],
            dx_name=dx_tup[1],
            us_short_summary=us_short,
            secretion_short=secretion_short,
            trach_days=trach_days
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            age=age, 
            gender_long=gender_tup[0], 
            doctor=doctor,
            dx_code=dx_tup[0],
            dx_name=dx_tup[1],
            surrogate_rel=surrogate_tup[0],
            surrogate_name=surrogate_tup[1],
            sedation_block=sedation_block,
            us_finding_text=us_full,
            secretion_desc=secretion_full,
            segments_list=segments_list,
            trach_days=trach_days
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