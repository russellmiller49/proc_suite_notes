import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_076"
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
    "age": ["34", "41", "49", "52", "58", "64", "68", "71", "77", "83"],
    "gender_tuple": [("female", "F", "She", "her"), ("male", "M", "He", "his")],
    "ref_physician": ["Dr. Mehtsun", "Dr. Al-Jabi", "Dr. Smith", "Dr. Klein", "Dr. Rodriguez", "Dr. Chang"],
    "attending": ["Dr. Anderson", "Dr. Lee", "Dr. Patel", "Dr. Gomez"],
    "assistant": ["Dr. Roberts", "Dr. Chen", "Dr. Lewis", "PA-C Davis"],
    
    # Context: Why is the patient intubated?
    "surgery_context": [
        "gastric surgery", 
        "orthopedic fixation", 
        "exploratory laparotomy", 
        "cervical spine fusion",
        "bowel resection"
    ],

    # Specific Findings/Pathology Location variations (Tuple: Lobe Name, Segment Detail, Stenosis Description)
    "target_pathology": [
        ("Right Middle Lobe (RML)", "Lateral Segment of RML (RB4) and Medial Segment of RML (RB5)", "Moderately stenotic from extrinsic compression"),
        ("Left Upper Lobe (LUL)", "Apical-Posterior Segment (RB1/2)", "Mildly stenotic due to mucosal edema"),
        ("Right Lower Lobe (RLL)", "Superior Segment (RB6)", "Significantly narrowed due to secretions and inflammation"),
        ("Lingula", "Superior Lingular Segment (RB4)", "Compressed by adjacent lymphadenopathy"),
        ("Bronchus Intermedius (BI)", "Distal BI", "Stenotic with cobbling appearance")
    ],

    "bi_finding": [
        "Notable for small endobronchial nodules at distal BI as before",
        "Clear of endobronchial lesions",
        "Mild mucosal erythema noted",
        "Small polypoid lesion noted, unchanged from prior"
    ],

    "secretions": [
        "Moderate clear thick secretions",
        "Copious purulent secretions",
        "Scant mucoid secretions",
        "Thick white mucous plugs",
        "Bloody tinged secretions"
    ],

    # Fluid mechanics
    "fluids": [
        ("60", "20"),
        ("80", "15"),
        ("100", "40"),
        ("120", "35"),
        ("50", "10")
    ],
    
    "plan_followup": [
        "Repeat bronchoscopy in 4-6 weeks",
        "Repeat bronchoscopy in 2-3 months",
        "Follow up in clinic in 2 weeks",
        "CT Chest in 4 weeks followed by clinic visit"
    ]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
# Using f-string compatible format (doubling braces for literal JSON or LaTeX if needed, but standard text here)
note_template = """NOTE_ID:  {note_id} SOURCE_FILE: {note_id}.txt

INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: [Date] CC Referred Physician: {ref_physician}

INDICATION FOR OPERATION {patient_name_redacted} is a {age}-year-old {gender_long} who presents with bronchial stenosis.
The nature, purpose, risks, benefits and alternatives to Bronchoscopy were discussed with the patient in detail.
CONSENT Obtained before the procedure.

PREOPERATIVE DIAGNOSIS

J98.09 Other diseases of bronchus, not elsewhere classified 

POSTOPERATIVE DIAGNOSIS

J98.09 Other diseases of bronchus, not elsewhere classified 

PROCEDURE

31645 Therapeutic aspiration initial episode 

31624 Dx bronchoscope/lavage (BAL) 

ATTENDING {attending}

ASSISTANT {assistant}

ANESTHESIA General Anesthesia 

MONITORING Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.
INSTRUMENTATION Disposable Bronchoscope 

ESTIMATED BLOOD LOSS None 

COMPLICATIONS None 

PROCEDURE IN DETAIL After the successful induction of anesthesia, a timeout was performed (confirming the patient's name, procedure type, and procedure location).
Patient Position: Patient was already intubated for {poss_pronoun} {surgery_context} with {ref_physician}.
Initial Airway Inspection: The endotracheal tube is in good position. The visualized portion of the trachea is of normal caliber.
The carina is sharp. The tracheobronchial tree was examined to at least the first subsegmental level.
Airway Exam Findings:


Bronchus Intermedius (BI): {bi_finding}.
{target_lobe_name}: {stenosis_desc}.


Secretions: {secretion_desc} bilaterally.
Therapeutic Aspiration Successful therapeutic aspiration was performed to clean out the Trachea (Distal 1/3), Right Mainstem, Bronchus Intermedius, and Left Mainstem from mucus.
Bronchoalveolar Lavage (BAL) Bronchial alveolar lavage was performed at {lavage_segments}.
Instilled {instilled_cc} cc of NS, suction returned with {return_cc} cc of NS.
Samples sent for Cell Count, Microbiology (Cultures/Viral/Fungal), and Cytology.

The patient tolerated the procedure well. There were no immediate complications.
Patient was left intubated for the rest of {poss_pronoun} surgery.
SPECIMENS

{lobe_short} BAL 

IMPRESSION / PLAN {patient_name_redacted} is a {age}-year-old {gender_long} who presents for bronchoscopy for bronchial stenosis.

Follow-up BAL studies.
Consult ID for pulmonary fungal infection while admitted.

{plan_followup}.
"""

prompt_styles = [
    # Style 1: Telegraphic / Summary
    "Write a bronchoscopy report. {age}yo {gender_short}, ref {ref_physician}. Indication: Stenosis. Found {stenosis_desc} in {lobe_short}. {secretion_desc}. BAL performed {lobe_short} ({instilled_cc}cc in/{return_cc}cc out). Pt intubated for {surgery_context}.",
    
    # Style 2: Dictation / Narrative
    "Dictate an op note for Dr. {attending}. Patient is a {age} year old {gender_long} already intubated for {surgery_context}. We did a therapeutic aspiration and BAL. Findings included {bi_finding} and {stenosis_desc} in the {lobe_short}. Lavage done at {lavage_segments}. Plan: {plan_followup}.",
    
    # Style 3: Sloppy / Quick Handoff
    "Gen Anesthesia bronch note. {age} {gender_short}. Dx J98.09. {lobe_short} stenosis seen, also {bi_finding}. Suctioned {secretion_desc}. BAL {lobe_short} samples sent. No comps. Thx.",
    
    # Style 4: Billing Focused
    "Procedure codes 31645, 31624. Diagnosis J98.09. Patient {age}/{gender_short}. Key findings: {stenosis_desc} at {lobe_short}. Therapeutic aspiration of {secretion_desc} and BAL performed ({instilled_cc}cc NS). Surgeon: {attending}.",
    
    # Style 5: Structured Request
    "Create Interventional Pulmonology Report:\n- Patient: {age} y/o {gender_long}\n- Context: Intubated for {surgery_context}\n- Findings: {stenosis_desc} ({lobe_short}); {bi_finding}\n- Procedure: Aspiration & BAL ({lavage_segments})"
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
        subj_pronoun = gender_tup[2]
        poss_pronoun = gender_tup[3]
        
        ref_physician = random.choice(data_pool["ref_physician"])
        attending = random.choice(data_pool["attending"])
        assistant = random.choice(data_pool["assistant"])
        surgery_context = random.choice(data_pool["surgery_context"])
        
        # Pathology logic extraction
        pathology_tup = random.choice(data_pool["target_pathology"])
        target_lobe_name = pathology_tup[0]
        lavage_segments = pathology_tup[1]
        stenosis_desc = pathology_tup[2]
        
        # Extract short lobe name for prompt brevity (e.g., "Right Middle Lobe (RML)" -> "RML")
        if "(" in target_lobe_name:
            lobe_short = target_lobe_name.split("(")[1].replace(")", "")
        else:
            lobe_short = target_lobe_name

        bi_finding = random.choice(data_pool["bi_finding"])
        secretion_desc = random.choice(data_pool["secretions"])
        
        fluid_tup = random.choice(data_pool["fluids"])
        instilled_cc = fluid_tup[0]
        return_cc = fluid_tup[1]
        
        plan_followup = random.choice(data_pool["plan_followup"])

        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, gender_short=gender_short, gender_long=gender_long,
            ref_physician=ref_physician, attending=attending,
            lobe_short=lobe_short, stenosis_desc=stenosis_desc,
            secretion_desc=secretion_desc, instilled_cc=instilled_cc,
            return_cc=return_cc, surgery_context=surgery_context,
            bi_finding=bi_finding, lavage_segments=lavage_segments,
            plan_followup=plan_followup
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            patient_name_redacted="[REDACTED]",
            age=age,
            gender_long=gender_long,
            ref_physician=ref_physician,
            attending=attending,
            assistant=assistant,
            poss_pronoun=poss_pronoun,
            surgery_context=surgery_context,
            bi_finding=bi_finding,
            target_lobe_name=target_lobe_name,
            stenosis_desc=stenosis_desc,
            secretion_desc=secretion_desc,
            lavage_segments=lavage_segments,
            instilled_cc=instilled_cc,
            return_cc=return_cc,
            lobe_short=lobe_short,
            plan_followup=plan_followup
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