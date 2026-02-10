import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_100"
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
    "age": ["45", "52", "56", "61", "67", "74", "79", "83"],
    "gender_tuple": [("female", "F"), ("male", "M")],
    "diagnosis_code": ["J96.90", "J96.00", "J96.10", "J98.01"],
    "diagnosis_text": ["Respiratory Failure", "Acute Respiratory Failure", "Chronic Respiratory Failure", "Bronchial Stenosis"],
    
    # Cohesive Clinical Scenarios to ensure findings match the plan/indication
    "scenarios": [
        {
            "indication": "bronchial anastomotic dehiscence and stenosis",
            "right_finding": "Airway exam notable for persistent pale plaque of tissue along the anterior wall of the Right Mainstem Bronchus (RMSB), Bronchus Intermedius (BI), and Right Middle Lobe (RML) orifice. The RML orifice is now completely stenosed by overlying necrotic debris. Unable to probe into the airway to achieve patency.",
            "left_finding": "The Left Mainstem Bronchus (LMSB) anastomosis shows mild granulation tissue and similar pale soft tissue plaque along the anterior aspect of the distal LMSB.",
            "plan_action": "Plan for bronchoscopy under GA for management of RML stenosis—likely excision of overlying debris, balloon dilation, and stent placement.",
            "summary_for_prompt": "stenosis with necrotic debris in RML and plaque in RMSB",
            "aspiration_areas": "Trachea (Distal 1/3), Right Mainstem, Bronchus Intermedius, Left Mainstem, and RLL and LLL"
        },
        {
            "indication": "severe mucous plugging and hypoxia",
            "right_finding": "Significant amount of thick, tenacious secretions noted in the Right Mainstem Bronchus (RMSB) extending into the lower lobes. No endobronchial lesions or stenosis identified after clearance.",
            "left_finding": "The Left Mainstem Bronchus (LMSB) contains moderate mucoid secretions. Mucosa appears erythematous but patent.",
            "plan_action": "Continue aggressive pulmonary toilet and nebulizer treatments. Repeat bronchoscopy if lobar collapse recurs.",
            "summary_for_prompt": "severe mucous plugging bilaterally, no stenosis",
            "aspiration_areas": "Trachea, Bilateral Mainstems, and all segmental airways"
        },
        {
            "indication": "suspected granulation tissue obstruction",
            "right_finding": "Exophytic granulation tissue noted at the distal Right Mainstem Bronchus (RMSB), causing 40% luminal narrowing. No necrotic debris observed.",
            "left_finding": "The Left Mainstem Bronchus (LMSB) is patent with healthy mucosa. No granulation tissue seen.",
            "plan_action": "Consider laser ablation or cryotherapy for RMSB granulation tissue in future session if symptoms worsen.",
            "summary_for_prompt": "granulation tissue in RMSB causing mild narrowing",
            "aspiration_areas": "Right Mainstem and RLL"
        }
    ],
    
    "anesthesia_sites": [
        "trachea, main carina, RMS, and LMS",
        "vocal cords, trachea, and bilateral mainstem bronchi",
        "posterior oropharynx, vocal cords, and carina"
    ],
    "secretions_desc": [
        "Clear secretions noted bilaterally.",
        "Thick, white secretions noted throughout.",
        "Blood-tinged secretions noted in distal airways.",
        "Minimal frothy secretions."
    ],
    "trachea_exam": [
        "The tracheostomy tube is in good position. The visualized portion of the trachea is of normal caliber and the carina is sharp.",
        "The tracheostomy tube is patent. Tracheal mucosa shows mild inflammation.",
        "The ETT is in good position above the carina. Trachea is patent."
    ]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
note_template = """NOTE_ID: {note_id}
SOURCE_FILE: {note_id}.txt

INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

INDICATION FOR OPERATION
[REDACTED] is a {age}-year-old {gender_long} who presents with {indication}.

PREOPERATIVE DIAGNOSIS
{dx_code} {dx_text}

POSTOPERATIVE DIAGNOSIS
{dx_code} {dx_text}

PROCEDURE
Therapeutic aspiration, subsequent episodes (CPT 31646)
Diagnostic bronchoscopy with cell washing (CPT 31622)

ANESTHESIA
Local ONLY. Lidocaine applied to {anesthesia_sites}.

MONITORING
Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.

INSTRUMENTATION
Disposable Bronchoscope.

ESTIMATED BLOOD LOSS
None.

COMPLICATIONS
None.

PROCEDURE IN DETAIL
A timeout was performed (confirming the patient's name, procedure type, and procedure location).

Airway Inspection

Trachea: {trachea_exam}

Extent: The tracheobronchial tree was examined to at least the first subsegmental level.

Right Lung Findings:
{right_finding}

Left Lung Findings:
{left_finding}
Segmental airways on the left are widely patent.

Secretions: {secretions}

Interventions

Therapeutic Aspiration: Successful therapeutic aspiration was performed to clean out the {aspiration_areas} from mucus.

Conclusion
The patient tolerated the procedure well. There were no immediate complications.
At the conclusion of the operation, the patient was extubated in the operating room and transported to the recovery room in stable condition.

SPECIMEN(S)
None.

IMPRESSION / PLAN
{plan}
Likely on [REDACTED].
"""

prompt_styles = [
    # Style 1: Telegraphic
    "Gen report: {age}yo {gender_short}, dx {dx_text}. Ind: {indication}. Findings: {summary}. Plan: {plan_short_hint}.",
    
    # Style 2: Dictation
    "Please write an interventional pulm op report for a {age} year old {gender_long} presenting with {indication}. We used local anesthesia. On exam, we found {summary}. We performed therapeutic aspiration.",
    
    # Style 3: Sloppy / Quick
    "{age} {gender_short} bronch note. {dx_code}. findings: {summary}. cleared secretions from {aspiration_areas}. no comps.",
    
    # Style 4: Billing Focus
    "CPT 31646, 31622. Dx {dx_code}. Patient {age} {gender_short}. Indication: {indication}. Findings: {summary}.",
    
    # Style 5: Structured
    "Patient: {age} {gender_short}\nPre-op Dx: {dx_text}\nProcedure: Therapeutic aspiration\nKey Findings: {summary}\nAction: Create full op note."
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
        dx_code = random.choice(data_pool["diagnosis_code"])
        dx_text = random.choice(data_pool["diagnosis_text"])
        anesthesia = random.choice(data_pool["anesthesia_sites"])
        secretions = random.choice(data_pool["secretions_desc"])
        trachea = random.choice(data_pool["trachea_exam"])
        
        # Select a cohesive clinical scenario
        scenario = random.choice(data_pool["scenarios"])
        
        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        
        # Create a short hint for the plan for the telegraphic prompt
        plan_short = "future bronch" if "future" in scenario["plan_action"] else "continue care"
        
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_tup[1], 
            gender_long=gender_tup[0],
            dx_text=dx_text,
            dx_code=dx_code,
            indication=scenario["indication"],
            summary=scenario["summary_for_prompt"],
            aspiration_areas=scenario["aspiration_areas"],
            plan_short_hint=plan_short
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            age=age, 
            gender_long=gender_tup[0],
            indication=scenario["indication"],
            dx_code=dx_code,
            dx_text=dx_text,
            anesthesia_sites=anesthesia,
            trachea_exam=trachea,
            right_finding=scenario["right_finding"],
            left_finding=scenario["left_finding"],
            secretions=secretions,
            aspiration_areas=scenario["aspiration_areas"],
            plan=scenario["plan_action"]
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