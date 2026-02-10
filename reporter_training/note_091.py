import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_091" 
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
    "age": ["45", "52", "57", "61", "66", "73", "78", "82"],
    "gender_tuple": [("female", "F", "her"), ("male", "M", "his")],
    "doctor": ["Smith", "Patel", "Gomez", "Weiss", "O'Connor", "Lee", "Al-Fayed"],
    
    # Anatomical Locations and Abbreviations
    "location_tuple": [
        ("right middle lobe", "RML"),
        ("right upper lobe", "RUL"),
        ("left upper lobe", "LUL"),
        ("left lower lobe", "LLL"),
        ("right lower lobe", "RLL"),
        ("bronchus intermedius", "BI")
    ],
    
    # Pathology variations
    "pathology": [
        "weblike stenosis and pedunculated granulation tissue",
        "fibrotic scarring and concentric stenosis",
        "exophytic tumor ingrowth",
        "inflammatory stricture with granulation",
        "circumferential airway narrowing"
    ],
    
    # Secretion descriptions
    "secretions": [
        "thick purulent secretions",
        "copious mucoid secretions",
        "blood-tinged mucus",
        "tenacious white secretions",
        "moderate mucopurulent secretions"
    ],
    
    # Degree of narrowing (Pre-op)
    "stenosis_pre": ["60%", "70%", "75%", "80%", "90%", "95%"],
    
    # Post-op patency
    "patency_post": ["100%", "90%", "95%", "widely patent"],
    
    # Balloon Dilation Details (Type / Size dilated to)
    "balloon_tuple": [
        ("Mustang 6/7/8", "6 mm and 7 mm"),
        ("CRE 8/9/10", "8 mm and 9 mm"),
        ("Mustang 4mm", "4 mm"),
        ("CRE 10/11/12", "10 mm and 11 mm")
    ],
    
    # Plan variations
    "plan_note": [
        "patient is currently on a stent holiday",
        "surveillance for stent restenosis",
        "management of post-transplant airway complications",
        "monitor for benign airway stenosis recurrence"
    ]
}

# ==========================================
# 3. TEMPLATES
# ==========================================

# The template uses placeholders mapped to the variables above.
note_template = """INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: February 9, 2026 CC Referred Physician: {doctor}

INDICATION FOR OPERATION The patient is a {age}-year-old {gender_long} who presents with bronchial stenosis of the {loc_long} ({loc_short}).

The nature, purpose, risks, benefits, and alternatives to bronchoscopy were discussed with the patient in detail.

CONSENT Obtained before the procedure. Indications, potential complications, and alternatives were discussed.

PREOPERATIVE DIAGNOSIS
J98.09 Other diseases of bronchus, not elsewhere classified 

POSTOPERATIVE DIAGNOSIS
J98.09 Other diseases of bronchus, not elsewhere classified 

PROCEDURE
Therapeutic aspiration, initial episode (31645) 
Bronchoalveolar lavage (BAL) (31624) 
Endobronchial Biopsy(s) (31625) 
Balloon dilation (31630) 
Destruction of tumor OR relief of stenosis by any method other than excision (e.g., cryotherapy) (31641) 

ANESTHESIA General Anesthesia 

MONITORING Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.

INSTRUMENTATION Disposable Bronchoscope 

ESTIMATED BLOOD LOSS Minimum 

COMPLICATIONS None 

PROCEDURE IN DETAIL After the successful induction of anesthesia, a timeout was performed (confirming the patient's name, procedure type, and procedure location).

Initial Airway Inspection The endotracheal tube was in good position.
The visualized portion of the trachea was of normal caliber and the carina was sharp.
The tracheobronchial tree was examined to at least the first subsegmental level.

Findings: The airway exam was notable for mildly tortuous airways as before, with intact anastomoses bilaterally.
Mild secretions were noted bilaterally, with {secretions} emanating from the {loc_short}.

Stenosis: The {loc_short} orifice was approximately {stenosis_pre} narrowed with a combination of {pathology}.

Therapeutic Aspiration Successful therapeutic aspiration was performed to clean out the Bronchus and {loc_short} Carina from mucus and mucus plugs.

Endobronchial Biopsy Endobronchial biopsy was performed at the {loc_short}. The lesion was successfully removed. Samples were sent for Microbiology (Cultures/Viral/Fungal).

Balloon Dilation Balloon dilation was performed at the {loc_short}.
A Mustang 4mm balloon was used to perform dilation to 4 mm (1 inflation, 60 seconds).
A {balloon_type} balloon was subsequently used to perform dilation to {balloon_size} at the {loc_short} (2 inflations, 60 seconds each).

Endobronchial Tumor Destruction (Cryotherapy) Endobronchial obstruction at the {loc_short} was treated with cryotherapy.

Modality: Cryoprobe (1.7mm probe) 
Setting: 30-second freeze-thaw cycles 
Result: Ablation performed.

Prior to treatment, the affected airway was noted to be {patency_pre_inv} patent. After treatment, the airway was {patency_post}.

Bronchoalveolar Lavage (BAL) Bronchial alveolar lavage was performed at the {loc_short}.
Instilled 60 cc of NS, suction returned with 15 cc of NS.
Samples sent for Cell Count, Microbiology (Cultures/Viral/Fungal), and Cytology.

The patient tolerated the procedure well. There were no immediate complications.
At the conclusion of the operation, the patient was extubated in the operating room and transported to the recovery room in stable condition.

SPECIMENS
{loc_short} EBBx (micro) 
{loc_short} BAL 

IMPRESSION / PLAN
{age}-year-old {gender_long} with bronchial stenosis of the {loc_short}.
Ongoing recurrence of stenosis; {plan_note}.
Will need ongoing close vigilance of the airway due to tendency to fuse shut.
Follow-up BAL results.
Repeat bronchoscopy in 2 weeks for dilation.
"""

# 5 distinct prompt styles to simulate different user inputs
prompt_styles = [
    # Style 1: Telegraphic
    "Generate IP report. {age}yo {gender_short}, Ref: Dr. {doctor}. Indication: {loc_short} stenosis. Findings: {pathology}, {stenosis_pre} blocked. Tx: Aspiration, Biopsy, Balloon ({balloon_type}), Cryo. Post-op {patency_post}. Plan: 2wk f/u.",
    
    # Style 2: Dictation
    "Please write an operative note for a {age} year old {gender_long} referred by {doctor}. The patient has stenosis of the {loc_long}. We found {secretions} and {pathology} causing {stenosis_pre} narrowing. We did BAL, biopsy, cryotherapy, and dilated with a {balloon_type} to {balloon_size}. The airway was {patency_post} at the end.",
    
    # Style 3: Sloppy / Quick
    "{age} {gender_short} {loc_short} stenosis. {pathology} found. used cryo and balloon {balloon_type}. {secretions} cleaned out. {doctor} ref. J98.09.",
    
    # Style 4: Billing Focus
    "Codes 31645, 31624, 31625, 31630, 31641. {age}/{gender_short}. Dx: {loc_short} stenosis ({stenosis_pre}). Procedure: Balloon dilation ({balloon_type}) and Cryo. Path: {pathology}.",
    
    # Style 5: Structured
    "Patient: {age} {gender_short}\nReferring: {doctor}\nDiagnosis: {loc_short} Stenosis\nFindings: {stenosis_pre} narrowing, {pathology}, {secretions}\nIntervention: Cryo, Balloon ({balloon_type} to {balloon_size}), BAL, Biopsy\nOutcome: {patency_post} patent."
]

# ==========================================
# 4. GENERATOR LOGIC
# ==========================================
def generate_dataset():
    dataset = []
    
    for _ in range(NUM_SAMPLES):
        # A. Randomly select variables
        age = random.choice(data_pool["age"])
        gender_tup = random.choice(data_pool["gender_tuple"]) # (long, short, possessive)
        doctor = random.choice(data_pool["doctor"])
        
        loc_tup = random.choice(data_pool["location_tuple"]) # (long, short)
        pathology = random.choice(data_pool["pathology"])
        secretions = random.choice(data_pool["secretions"])
        stenosis_pre = random.choice(data_pool["stenosis_pre"])
        patency_post = random.choice(data_pool["patency_post"])
        
        balloon_tup = random.choice(data_pool["balloon_tuple"]) # (type, size description)
        plan_note = random.choice(data_pool["plan_note"])
        
        # Calculate inverse patency for the "Prior to treatment" line (roughly 100 - stenosis)
        # Just creating a logical string based on stenosis_pre
        try:
            sten_val = int(stenosis_pre.replace('%',''))
            patency_pre_inv = f"{100 - sten_val}%"
        except:
            patency_pre_inv = "25%" # Fallback

        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_tup[1], 
            gender_long=gender_tup[0],
            doctor=doctor, 
            loc_short=loc_tup[1],
            loc_long=loc_tup[0],
            pathology=pathology,
            stenosis_pre=stenosis_pre,
            balloon_type=balloon_tup[0],
            balloon_size=balloon_tup[1],
            patency_post=patency_post,
            secretions=secretions
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            age=age, 
            gender_long=gender_tup[0], 
            doctor=doctor,
            loc_long=loc_tup[0],
            loc_short=loc_tup[1],
            secretions=secretions,
            stenosis_pre=stenosis_pre,
            pathology=pathology,
            balloon_type=balloon_tup[0],
            balloon_size=balloon_tup[1],
            patency_pre_inv=patency_pre_inv,
            patency_post=patency_post,
            plan_note=plan_note
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