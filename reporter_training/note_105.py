import json
import random
import os
import datetime

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_105"
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
    "age": ["49", "52", "56", "59", "63", "67", "71", "74"],
    "gender_tuple": [("female", "F"), ("male", "M")],
    "indication": [
        "airway evaluation and stent change", 
        "surveillance bronchoscopy", 
        "evaluation of hypoxemia and secretion management",
        "clearance of mucous plugging"
    ],
    "diagnosis_code": ["J98.09", "T85.698A", "J96.00"],
    "diagnosis_text": [
        "Other diseases of bronchus, not elsewhere classified",
        "Complication of internal prosthetic device",
        "Acute respiratory failure, unspecified"
    ],
    "anesthesia": [
        "Local ONLY", 
        "Moderate Sedation", 
        "MAC (Monitored Anesthesia Care)"
    ],
    "secretion_type": [
        "frothy, non-obstructing white secretions",
        "thick, tenacious mucoid secretions",
        "purulent yellow secretions",
        "scant serosanguinous secretions"
    ],
    "stent_type": [
        "uncovered metallic stent",
        "partially covered metallic stent",
        "silicone Y-stent"
    ],
    "stent_position": [
        "in good position",
        "slightly migrated distally",
        "slightly migrated proximally"
    ],
    "rul_status": [
        "intentionally 'jailing off' the right upper lobe (RUL) bronchus",
        "partially obstructing the RUL orifice",
        "sitting just proximal to the RUL take-off"
    ],
    "tissue_health": [
        "significant ischemic and necrotic debris",
        "mild granulation tissue",
        "healthy, pink mucosa",
        "friable mucosa with contact bleeding"
    ],
    "plan_frequency": [
        "2-3x weekly bronchoscopy clean-out",
        "daily therapeutic aspiration",
        "weekly surveillance",
        "bronchoscopy PRN for desaturation"
    ],
    "next_step": [
        "Possible stent exchange late next week",
        "Continue current management, no stent change needed",
        "Consider upsizing to 16x40 B.S. SEMS",
        "Discuss rigid bronchoscopy for debridement"
    ]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
note_template = """NOTE_ID: {note_id}
SOURCE_FILE: {note_id}.txt

INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: {date_str}
INDICATION FOR OPERATION
The patient is a {age}-year-old {gender_long} who presents with {indication}.

The nature, purpose, risks, benefits, and alternatives to Bronchoscopy were discussed with the patient/surrogate in detail. The patient/surrogate indicated a wish to proceed with surgery and informed consent was signed.

CONSENT Obtained before the procedure. Indications, potential complications, and alternatives were discussed.

PREOPERATIVE DIAGNOSIS
{diagnosis_code} {diagnosis_text}

POSTOPERATIVE DIAGNOSIS
{diagnosis_code} {diagnosis_text}

PROCEDURE
31646 Therapeutic aspiration subsequent episodes
31622 Dx bronchoscope/cell washing

ANESTHESIA {anesthesia}

MONITORING Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.

INSTRUMENTATION Flexible Therapeutic Bronchoscope

ESTIMATED BLOOD LOSS None

COMPLICATIONS None

PROCEDURE IN DETAIL
A timeout was performed (confirming the patient's name, procedure type, and procedure location).

Anesthesia and Airway Entry
Lidocaine was instilled into the tracheostomy tube. The disposable bronchoscope was advanced. Lidocaine was applied to the main carina, right mainstem (RMS), bronchus intermedius (BI), and left secondary carina (LC2).

Initial Airway Inspection
Initial inspection revealed {secretion_type} in the RMS, BI, right middle lobe (RML), right lower lobe (RLL), left mainstem (LMS), and left lower lobe (LLL).

Therapeutic Aspiration
Successful therapeutic aspiration was performed to clean out the distal trachea, RMS, BI, RML, RLL, LMS, and LLL from mucus.

Airway Stent Surveillance and Findings
The {stent_type} was visualized {stent_position}, appropriately spanning from the mid-RMS to the proximal BI. It fully covers and closes the prior area of RMS anastomosis dehiscence.

RUL: The stent is {rul_status}, but uncovered perforations between struts allow for ventilation of the RUL. Minimal secretions were noted overlying this area. The RUL bronchus and segments RB1 and RB2 were visualized from the RMS. The RUL bronchus shows evidence of healing with fibrin exudates and desired granulation tissue.

Stent Integrity: The stent is perhaps mildly undersized, but there are no signs of migration nor significant granulation over the struts.

Right Lung: There is {tissue_health} remaining in the donor RMS and BI, overlying the RML take-off, and overlying the RB6 take-off. This is leading to moderate stenosis of the RML bronchus. The RLL basilar segments appear healthy.

Left Lung: The LMS anastomosis is intact with visible sutures and mild stenosis. The left upper lobe (LUL) bronchus shows evidence of healing with fibrin exudates and desired granulation tissue. The underlying mediastinum/pulmonary artery is no longer visible along the medial aspect of the LUL. The LLL bronchus and segments appear healthy.

Conclusion
The patient tolerated the procedure well. There were no immediate complications. At the conclusion of the operation, the patient will remain in the ICU in similar condition to prior.

SPECIMENS None

IMPRESSION / PLAN
Status: {age}-year-old {gender_long} presented for bronchoscopy for stent exchange.
Findings: {stent_type} in {stent_position}.
Plan:
No plan for bronchoscopy by IP team for the remainder of this week unless clinical change occurs.
Patient continues to have issues with secretion clearance; {plan_frequency} may be warranted until the patient becomes stronger or able to clear own secretions.
Will defer to lung transplant team's discretion/expertise regarding timing, which could be done under local anesthesia to minimize interruptions in nutrition/PT.
Likely bronchoscopy by IP team early next week.

Discussions with primary team regarding RML bronchus dilation.
{next_step}.
"""

prompt_styles = [
    # Style 1: Telegraphic
    "IP Bronch note. {age}yo {gender_short}. Indication: {indication}. Found {secretion_type} and {tissue_health}. Stent {stent_position}. Plan: {plan_frequency}.",
    
    # Style 2: Dictation
    "Generate an operative report for a {age} year old {gender_long}. We performed {indication}. The {stent_type} was {stent_position}. We found {tissue_health} in the right lung. Plan is {next_step}.",
    
    # Style 3: Sloppy / Quick
    "{age} {gender_short} bronch. {diagnosis_code}. {secretion_type} suctioned out. Stent {rul_status}. {tissue_health} noted. {plan_frequency}.",
    
    # Style 4: Billing Focus
    "Procedure 31646, 31622. Pt {age} {gender_short}. Diagnosis {diagnosis_code}. Findings: {stent_type}, {stent_position}. Complications: None. Plan: {next_step}.",
    
    # Style 5: Structured
    "Patient: {age} {gender_short}\nIndication: {indication}\nFindings: {secretion_type}, {tissue_health}\nStent Status: {stent_position}\nPlan: {plan_frequency}"
]

# ==========================================
# 4. GENERATOR LOGIC
# ==========================================
def generate_dataset():
    dataset = []
    
    # Generate a random date within the last year for realism
    base_date = datetime.date(2025, 1, 1)
    
    for _ in range(NUM_SAMPLES):
        # A. Randomly select variables
        age = random.choice(data_pool["age"])
        gender_tup = random.choice(data_pool["gender_tuple"])
        indication = random.choice(data_pool["indication"])
        dx_index = random.randint(0, len(data_pool["diagnosis_code"])-1)
        diagnosis_code = data_pool["diagnosis_code"][dx_index]
        diagnosis_text = data_pool["diagnosis_text"][dx_index]
        anesthesia = random.choice(data_pool["anesthesia"])
        secretion_type = random.choice(data_pool["secretion_type"])
        stent_type = random.choice(data_pool["stent_type"])
        stent_position = random.choice(data_pool["stent_position"])
        rul_status = random.choice(data_pool["rul_status"])
        tissue_health = random.choice(data_pool["tissue_health"])
        plan_frequency = random.choice(data_pool["plan_frequency"])
        next_step = random.choice(data_pool["next_step"])
        
        # Generate random date
        random_days = random.randint(0, 365)
        date_str = (base_date + datetime.timedelta(days=random_days)).strftime("%B %d, %Y")

        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_tup[1], 
            gender_long=gender_tup[0],
            indication=indication,
            diagnosis_code=diagnosis_code,
            secretion_type=secretion_type,
            tissue_health=tissue_health,
            stent_position=stent_position,
            plan_frequency=plan_frequency,
            stent_type=stent_type,
            rul_status=rul_status,
            next_step=next_step
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            date_str=date_str,
            age=age, 
            gender_long=gender_tup[0],
            indication=indication,
            diagnosis_code=diagnosis_code,
            diagnosis_text=diagnosis_text,
            anesthesia=anesthesia,
            secretion_type=secretion_type,
            stent_type=stent_type,
            stent_position=stent_position,
            rul_status=rul_status,
            tissue_health=tissue_health,
            plan_frequency=plan_frequency,
            next_step=next_step
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