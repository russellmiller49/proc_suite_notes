import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_101"
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
    "age": ["49", "52", "56", "61", "65", "68", "72", "75"],
    "gender_tuple": [("female", "F", "She"), ("male", "M", "He")],
    "physician": ["Dr. Ingraham", "Dr. Bowers", "Dr. Chen", "Dr. Smith", "Dr. Miller", "Dr. Gupta"],
    "diagnosis_code": ["J96.90", "J96.00", "J96.21"],
    "diagnosis_text": [
        "Respiratory Failure",
        "Acute Respiratory Failure",
        "Hypoxic Respiratory Failure"
    ],
    "indication_context": [
        "bronchial anastomotic dehiscence and stenosis",
        "suspected airway obstruction and desaturation",
        "worsening dyspnea and suspected anastomotic complication",
        "surveillance of lung transplant anastomosis"
    ],
    
    # Right Lung Findings Variations
    "right_airway_findings": [
        {
            "desc": "persistent pale plaque of tissue along the anterior wall",
            "stenosis_loc": "RML orifice",
            "stenosis_pct": "75%",
            "anastomosis": "partially exposed hemoclip along the posterior membrane"
        },
        {
            "desc": "mild erythema and mucosal edema",
            "stenosis_loc": "RML orifice",
            "stenosis_pct": "50%",
            "anastomosis": "well-healed with no exposed hardware"
        },
        {
            "desc": "thickened white fibrin tags along the medial wall",
            "stenosis_loc": "Bronchus Intermedius",
            "stenosis_pct": "60%",
            "anastomosis": "single loose suture noted on the lateral wall"
        },
        {
            "desc": "circumferential granulation tissue",
            "stenosis_loc": "RML orifice",
            "stenosis_pct": "80%",
            "anastomosis": "small area of dehiscence at the 3 o'clock position"
        }
    ],

    # Left Lung Findings Variations
    "left_airway_findings": [
        "shows mild granulation tissue and similar pale soft tissue plaque along the anterior aspect",
        "appears patent with minimal mucosal inflammation",
        "shows moderate granulation tissue causing 20% narrowing",
        "demonstrates healthy mucosa with no evidence of dehiscence"
    ],

    # Secretions & BAL
    "secretion_type": ["Clear secretions", "Thick white mucus", "Purulent secretions", "Mucoid secretions"],
    "bal_location": ["Anterior-basal Segment of the RLL (RB8)", "Lateral Segment of the RML (RB4)", "Posterior Basal Segment RLL (RB10)"],
    "bal_volumes": [("40 cc", "10 cc"), ("50 cc", "20 cc"), ("30 cc", "5 cc"), ("60 cc", "25 cc")]
}

# ==========================================
# 3. TEMPLATES
# ==========================================

note_template = """NOTE_ID: {note_id}
SOURCE_FILE: {note_id}.txt

INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT
DATE OF PROCEDURE: [Date] CC Referred Physician: {physician}

INDICATION FOR OPERATION The patient is a {age}-year-old {gender_long} who presents with {diagnosis_text}.
The patient also presents for bronchoscopy for {indication_context}.
The nature, purpose, risks, benefits, and alternatives to Bronchoscopy were discussed with the patient in detail.
CONSENT Obtained before the procedure.

Indications, potential complications, and alternatives were discussed with the patient or surrogate.
Consent was signed and witnessed by an assisting medical professional.
PREOPERATIVE DIAGNOSIS

{dx_code} {diagnosis_text}

POSTOPERATIVE DIAGNOSIS

{dx_code} {diagnosis_text}

Bronchial anastomotic dehiscence and stenosis

PROCEDURE

31646 Therapeutic aspiration subsequent episodes 

31622 Dx bronchoscope/cell washing 

31624 Dx bronchoscope/lavage (BAL) 

ANESTHESIA Local ONLY 

MONITORING Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.
INSTRUMENTATION Disposable Bronchoscope.

ESTIMATED BLOOD LOSS None 

COMPLICATIONS None 

PROCEDURE IN DETAIL
After the successful induction of anesthesia, a timeout was performed (confirming the patient's name, procedure type, and procedure location).
Initial Airway Inspection The tracheostomy tube is in good position. The visualized portion of the trachea is of normal caliber.
The carina is sharp. The tracheobronchial tree was examined to at least the first subsegmental level.
Airway Findings

Right Lung: Airway exam was notable for {right_desc} of the Right Mainstem Bronchus (RMSB), Bronchus Intermedius (BI), and {stenosis_loc}.
The RMSB anastomosis continues to show a {right_anastomosis}.
The {stenosis_loc} is stenosed to ~{stenosis_pct} of its normal patency.
Left Lung: The Left Mainstem Bronchus (LMSB) anastomosis {left_desc} of the distal LMSB.
Segmental airways on the left are widely patent.

Secretions: {secretions} bilaterally.
Therapeutic Aspiration Successful therapeutic aspiration was performed to clean out the Trachea (Distal 1/3), Right Mainstem, Bronchus Intermedius, and Left Mainstem from mucus.
Bronchoalveolar Lavage (BAL) Bronchial alveolar lavage was performed at the {bal_loc}.
Instilled {vol_in} of NS, suction returned with {vol_out} of NS.

Samples sent for Cell Count and Microbiology (Cultures/Viral/Fungal).
Conclusion The patient tolerated the procedure well. There were no immediate complications.
At the conclusion of the operation, the patient was extubated in the operating room and transported to the recovery room in stable condition.
SPECIMEN(S)

RLL BAL 

IMPRESSION / PLAN

{age}-year-old {gender_long} with {diagnosis_text}, {indication_context}.

Successful therapeutic aspiration and BAL performed.
Plan: Follow-up BAL studies.
"""

prompt_styles = [
    # Style 1: Telegraphic
    "{age}{gender_short}, ref {physician}. Dx {dx_code}. Indication: {indication_context}. Right lung: {right_desc_short}, {stenosis_pct} stenosis. Left: {left_desc_short}. BAL {bal_loc}.",
    
    # Style 2: Dictation
    "Please generate a bronchoscopy note for a {age}-year-old {gender_long} referred by {physician}. Patient has {diagnosis_text}. We found {right_desc_short} in the right airway with {stenosis_pct} stenosis. BAL done at {bal_loc}.",
    
    # Style 3: Sloppy / Quick
    "{age}yo {gender_short} bronch. {indication_context}. findings: {right_desc_short}, hemoclip {right_anastomosis_short}. lavage {vol_in}/{vol_out}. no comps.",
    
    # Style 4: Billing Focus
    "Procedure codes 31646, 31622, 31624. Pt {age} {gender_short}. Dx {dx_code}. Findings: {stenosis_pct} stenosis at {stenosis_loc}, {left_desc_short}. Specimen: BAL.",
    
    # Style 5: Structured
    "Patient: {age} {gender_short}\nPhysician: {physician}\nIndication: {indication_context}\nFindings:\n- Right: {right_desc_short}, {stenosis_pct} stenosis\n- Left: {left_desc_short}\n- BAL: {bal_loc}"
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
        physician = random.choice(data_pool["physician"])
        dx_code = random.choice(data_pool["diagnosis_code"])
        diagnosis_text = random.choice(data_pool["diagnosis_text"])
        indication_context = random.choice(data_pool["indication_context"])
        
        # Complex Logic for Findings (Keeping consistency)
        right_lung_complex = random.choice(data_pool["right_airway_findings"])
        left_lung_desc = random.choice(data_pool["left_airway_findings"])
        secretions = random.choice(data_pool["secretion_type"])
        bal_loc = random.choice(data_pool["bal_location"])
        volumes = random.choice(data_pool["bal_volumes"])
        
        # Helper string shorteners for Prompts
        right_desc_short = right_lung_complex["desc"].split(" along")[0] # Shorten for prompt
        left_desc_short = left_lung_desc.split(" along")[0]
        right_anastomosis_short = "present" if "exposed" in right_lung_complex["anastomosis"] else "absent"

        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_tup[1], 
            gender_long=gender_tup[0],
            physician=physician, 
            dx_code=dx_code,
            diagnosis_text=diagnosis_text,
            indication_context=indication_context,
            right_desc_short=right_desc_short,
            stenosis_pct=right_lung_complex["stenosis_pct"],
            stenosis_loc=right_lung_complex["stenosis_loc"],
            left_desc_short=left_desc_short,
            bal_loc=bal_loc,
            right_anastomosis_short=right_anastomosis_short,
            vol_in=volumes[0],
            vol_out=volumes[1]
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            age=age, 
            gender_long=gender_tup[0],
            physician=physician,
            dx_code=dx_code,
            diagnosis_text=diagnosis_text,
            indication_context=indication_context,
            right_desc=right_lung_complex["desc"],
            stenosis_loc=right_lung_complex["stenosis_loc"],
            right_anastomosis=right_lung_complex["anastomosis"],
            stenosis_pct=right_lung_complex["stenosis_pct"],
            left_desc=left_lung_desc,
            secretions=secretions,
            bal_loc=bal_loc,
            vol_in=volumes[0],
            vol_out=volumes[1]
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