import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_038"
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
    "age": ["62", "68", "71", "74", "76", "79", "82", "85"],
    "gender_tuple": [("female", "F"), ("male", "M")],
    "doctor": ["Dr. Smith", "Dr. Chen", "Dr. Rodriguez", "Dr. Bowers", "Dr. Ingraham"],
    "diagnosis_code": ["J98.09", "J95.5", "C34.90", "J44.9"],
    "indication": [
        "airway stenosis", 
        "malignant airway obstruction", 
        "stridor and shortness of breath", 
        "recurrent tumor ingrowth"
    ],
    "anesthesia_type": ["General Anesthesia", "MAC with local"],
    "blood_loss": ["Minimal", "Scant", "Moderate", "Less than 10cc"],
    
    # Anatomy logic: Tuple = (Affected Side, Affected Lobe, Contralateral Side, Contralateral Findings)
    "site_config": [
        ("Right", "RUL and bronchus intermedius", "Left", "Normal anatomic branching to segmental level."),
        ("Left", "LUL and distal mainstem", "Right", "Normal anatomic branching to segmental level."),
    ],
    
    # Tumor characteristics
    "tumor_desc": [
        "extrinsic compression from tumor as well as some extruding tumor",
        "exophytic endobronchial mass with mixed extrinsic compression",
        "polypoid tumor growth causing subtotal occlusion",
        "circumferential mucosal infiltration and stenosis"
    ],
    
    # Pre and Post Patency percentages
    "patency_tuple": [
        ("5", "15"), ("10", "50"), ("0", "40"), ("20", "80"), ("5", "60")
    ],
    
    # Tools Used
    "apc_probe": ["2.3mm Straightfire probe", "1.5mm apical probe", "Side-fire probe"],
    "cryo_probe": ["2.4mm Cryoprobe", "1.9mm Cryoprobe"],
    "cryo_duration": ["3-10 second", "5-15 second", "10-20 second"],
    
    # Medications for hemostasis
    "meds_tuple": [
        ("cold saline, TXA (total 1000mg), and epinephrine (total 1000mg)", "TXA 500mg NEB Q8h"),
        ("cold saline and dilute epinephrine", "Monitor for hemoptysis"),
        ("cold saline and TXA (500mg)", "TXA 250mg NEB PRN"),
        ("iced saline lavage", "Standard post-op care")
    ]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
note_template = """INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: [Date] CC Referred Physician: {doctor} INDICATION FOR OPERATION {patient_name_placeholder} is a {age}-year-old {gender_long} who presents with {indication}.
The nature, purpose, risks, benefits, and alternatives to Bronchoscopy were discussed with the patient in detail.
Patient indicated a wish to proceed with surgery and informed consent was signed.

CONSENT Obtained before the procedure.
Its indications and potential complications and alternatives were discussed with the patient or surrogate.
The patient or surrogate read and signed the provided consent form/provided consent over the phone.
PREOPERATIVE DIAGNOSIS

{dx_code} Other diseases of bronchus, not elsewhere classified

POSTOPERATIVE DIAGNOSIS

{dx_code} Other diseases of bronchus, not elsewhere classified

PROCEDURE

31645 Therapeutic aspiration initial episode

31640 Bronchoscopy with excision

31641 Destruction of tumor OR relief of stenosis by any method other than excision (eg. laser therapy, cryotherapy)

Modifier 22 Details: Unusual Procedure.
This patient required multiple modalities for debulking and to treat bronchial stenosis.
This resulted in >100% increased work due to Increased intensity, Time, Technical difficulty of procedure, and Physical and mental effort required.
Apply to: 31640 Bronchoscopy with excision; 31641 Destruction of tumor OR relief of stenosis.
ATTENDING [REDACTED]

ANESTHESIA {anesthesia}

MONITORING Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.
INSTRUMENTATION Flexible Therapeutic Bronchoscope; Flexible Hybrid (Pediatric) Bronchoscope.

ESTIMATED BLOOD LOSS {blood_loss}

COMPLICATIONS None

PROCEDURE IN DETAIL After the successful induction of anesthesia, a timeout was performed (confirming the patient's name, procedure type, and procedure location).
Patient Position: Supine

Initial Airway Inspection Findings: The laryngeal mask airway (LMA) is in good position.
Pharynx: Not assessed due to bronchoscopy introduction through LMA.

Larynx: Normal.

Vocal Cords: Tissue/web at anterior commissure.
Trachea: {tumor_desc} at distal trachea, {side_long} side.

Main Carina: Sharp.
{side_long} Lung Proximal Airways: Obstructed airways at {affected_lobe} secondary to {tumor_desc_short}.
{contra_side} Lung Proximal Airways: {contra_findings} No evidence of mass, lesions, bleeding or other endobronchial pathology.
Mucosa: Erythematous and Friable.

Secretions: Minimal, thin, and clear mucus. Blood at the bronchus intermedius and distal {side_long}-sided airways.
Therapeutic Aspiration Successful therapeutic aspiration was performed to clean out the Trachea (Distal 1/3), {side_long} Mainstem, and lobar segments.
Endobronchial Tumor Excision Endobronchial tumor was noted and excised with mechanical debridement using forceps.
Note: Bleeding/oozing was noted from the airways so the decision was made to intubate the patient with an endotracheal tube.
Anesthesia placed 8.0mm ETT without issue.

Endobronchial Tumor Destruction Endobronchial obstruction at the {affected_lobe} was treated with the following modalities:

Mechanical: Forceps used for tissue/tumor debulking.
APC: {apc_probe} (Forced, effect 3) used for tissue/tumor debulking and hemostasis.
Cryoprobe: {cryo_probe} ({cryo_dur} applications) used for tissue/tumor debulking and hemostasis.
Prior to treatment, affected airway was noted to be {pre_pat}% patent. After treatment, the airway was {post_pat}% patent.
Hemostasis Endobronchial hemostasis was achieved. Bleeding/oozing was treated with {hemostasis_meds}.
The patient tolerated the procedure well. There were no immediate complications.
At the conclusion of the operation, the patient was extubated in the operating room and transported to the recovery room in stable condition.
SPECIMENS

None

IMPRESSION / PLAN

[REDACTED] is a {age}-year-old {gender_long} who presents for bronchoscopy for evaluation of {indication}.
Patient was noted to have extensive endobronchial tumor involvement at the {side_long}-sided airways.
This was treated with multiple modalities including forceps, APC, and cryotherapy.
At the conclusion of the case patent distal {side_long}-sided airways were identified.

Post procedure CXR.

Continued care per primary team.
If patient has scant hemoptysis, would treat with {post_op_meds}.
"""

# 5 DISTINCT PROMPT STYLES
prompt_styles = [
    # Style 1: Telegraphic / Rapid
    "{age}{gender_short}, ref {doctor}. Dx: {indication}. Found {tumor_desc_short} in {side_long} lung ({affected_lobe}). Used Forceps, APC ({apc_probe}), Cryo. Patency improved {pre_pat}% -> {post_pat}%. Meds: {hemostasis_meds_short}. Plan: {post_op_meds} if bleeding.",
    
    # Style 2: Dictation Style
    "Generate an operative report for a {age} year old {gender_long} referred by {doctor} for {indication}. We performed complex debulking (Modifier 22). Findings: {tumor_desc} in the {side_long} lung. We used mechanical forceps, APC, and cryotherapy. Patency went from {pre_pat}% to {post_pat}%. EBL {blood_loss}.",
    
    # Style 3: Billing/Coder Focus
    "Procedures: 31645, 31640, 31641. Modifier 22 for >100% effort due to complex debulking. Pt: {age} {gender_short}. Indication: {indication}. Site: {side_long} ({affected_lobe}). Methods: Forceps, APC, Cryo. Hemostasis: {hemostasis_meds_short}.",
    
    # Style 4: Sloppy / Short
    "{age}yo {gender_short} bronch. {side_long} side obstruction ({affected_lobe}). {tumor_desc_short}. did debulking with apc/cryo/forceps. {pre_pat}% open to {post_pat}% open. {doctor} pt.",
    
    # Style 5: Structured Request
    "Patient Demographics: {age} / {gender_long}\nIndication: {indication}\nFindings: {side_long} sided obstruction, {tumor_desc}\nIntervention: Multimodality (Forceps, APC, Cryo)\nOutcome: Improved patency ({pre_pat}% to {post_pat}%)"
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
        doctor = random.choice(data_pool["doctor"])
        dx_code = random.choice(data_pool["diagnosis_code"])
        indication = random.choice(data_pool["indication"])
        anesthesia = random.choice(data_pool["anesthesia_type"])
        blood_loss = random.choice(data_pool["blood_loss"])
        
        # Site Logic
        site_config = random.choice(data_pool["site_config"])
        side_long = site_config[0]
        affected_lobe = site_config[1]
        contra_side = site_config[2]
        contra_findings = site_config[3]
        
        # Tumor Logic
        tumor_desc = random.choice(data_pool["tumor_desc"])
        tumor_desc_short = "tumor compression" if "compression" in tumor_desc else "endobronchial mass"
        
        # Patency & Tools
        pat_tup = random.choice(data_pool["patency_tuple"])
        apc = random.choice(data_pool["apc_probe"])
        cryo = random.choice(data_pool["cryo_probe"])
        cryo_dur = random.choice(data_pool["cryo_duration"])
        
        # Meds
        meds_tup = random.choice(data_pool["meds_tuple"])
        hemostasis_meds = meds_tup[0]
        post_op_meds = meds_tup[1]
        hemostasis_meds_short = "TXA/Epi" if "TXA" in hemostasis_meds else "Saline/Epi"

        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, gender_short=gender_tup[1], gender_long=gender_tup[0],
            doctor=doctor, indication=indication, side_long=side_long,
            affected_lobe=affected_lobe, tumor_desc=tumor_desc,
            tumor_desc_short=tumor_desc_short, apc_probe=apc,
            pre_pat=pat_tup[0], post_pat=pat_tup[1],
            hemostasis_meds_short=hemostasis_meds_short,
            post_op_meds=post_op_meds, blood_loss=blood_loss
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            patient_name_placeholder="[REDACTED]",
            age=age, gender_long=gender_tup[0],
            doctor=doctor, indication=indication,
            dx_code=dx_code, anesthesia=anesthesia,
            blood_loss=blood_loss,
            tumor_desc=tumor_desc, tumor_desc_short=tumor_desc_short,
            side_long=side_long, affected_lobe=affected_lobe,
            contra_side=contra_side, contra_findings=contra_findings,
            apc_probe=apc, cryo_probe=cryo, cryo_dur=cryo_dur,
            pre_pat=pat_tup[0], post_pat=pat_tup[1],
            hemostasis_meds=hemostasis_meds,
            post_op_meds=post_op_meds
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