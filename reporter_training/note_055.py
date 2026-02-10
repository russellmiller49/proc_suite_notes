import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_055"
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
    "ages": ["55", "62", "67", "71", "74", "78", "81", "85"],
    "genders": [("female", "F", "She"), ("male", "M", "He")],
    "attendings": ["Dr. Smith", "Dr. Patel", "Dr. Rodriguez", "Dr. Chen", "Dr. Weiss"],
    "assistants": ["Dr. Lee (Fellow)", "Dr. Jones (Fellow)", "Dr. Kim (Resident)"],
    
    # Target 1 Variations (Location, Segment, Anatomical Name)
    "target_1_options": [
        ("RLL", "RB6", "Superior Segment"),
        ("RUL", "RB1", "Apical Segment"),
        ("RML", "RB4", "Lateral Segment"),
        ("LUL", "LB1+2", "Apical-Posterior Segment"),
    ],
    
    # Target 2 Variations
    "target_2_options": [
        ("LLL", "LB10", "Posterior-Basal Segment"),
        ("LUL", "LB3", "Anterior Segment"),
        ("RLL", "RB9", "Lateral-Basal Segment"),
        ("LLL", "LB9", "Lateral-Basal Segment"),
    ],
    
    # Lesion Details
    "lesion_sizes": ["0.5 cm", "0.8 cm", "1.1 cm", "1.5 cm", "0.4 cm"],
    "rose_results": [
        "Malignant neoplasm",
        "Adenocarcinoma",
        "Squamous cell carcinoma",
        "Non-small cell lung cancer",
        "Suspicious for malignancy"
    ],
    
    # EBUS Station Details
    "lymph_nodes": [
        ("Station 7 (Subcarinal)", "Type 2 pattern (mixed soft and stiff regions)"),
        ("Station 4R (Right Lower Paratracheal)", "Type 1 pattern (predominantly soft)"),
        ("Station 11L (Left Interlobar)", "Type 3 pattern (predominantly stiff)"),
        ("Station 4L (Left Lower Paratracheal)", "Type 2 pattern (mixed soft and stiff regions)")
    ]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
# The template mirrors the structure of note_055.txt
note_template = """NOTE_ID: {note_id} SOURCE_FILE: {note_id}.txt

INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: [Date] CC Referred Physician: {ref_phys}

INDICATION FOR OPERATION
{gender_long_cap} is a {age}-year-old {gender_long} who presents with a lung nodule requiring bronchoscopic diagnosis and staging.
The nature, purpose, risks, benefits, and alternatives to bronchoscopy were discussed with the patient in detail.
The patient wished to proceed and informed consent was obtained.

CONSENT Obtained before the procedure.
Indications, potential complications, and alternatives were discussed with the patient or surrogate.
Consent was signed and witnessed by an assisting medical professional.

PREOPERATIVE DIAGNOSIS
R91.8 Other nonspecific abnormal finding of lung field

POSTOPERATIVE DIAGNOSIS
R91.8 Other nonspecific abnormal finding of lung field
{rose_result} (ROSE conclusive for {t1_loc} and {t2_loc} targets)

PROCEDURE
Robotic navigational bronchoscopy (Ion) to {t1_loc} and {t2_loc} targets
Radial EBUS (rEBUS) localization
Cone-beam CT imaging (Cios Spin) with 3D reconstruction and trajectory verification
Transbronchial needle aspiration (TBNA) of lung nodules
Transbronchial cryobiopsy of lung nodules
Transbronchial brushing
Bronchoalveolar lavage (BAL)
Fiducial marker placement
EBUS-TBNA staging ({node_name}) with Elastography
Therapeutic aspiration

ATTENDING {attending}
ASSISTANT {assistant}
SUPPORT STAFF RN: [Name] RT: [Name]

ANESTHESIA General Anesthesia

MONITORING Pulse oximetry, heart rate, telemetry, and BP were continuously
monitored by an independent trained observer that was present throughout the entire procedure.

INSTRUMENTATION Flexible Therapeutic Bronchoscope; Linear EBUS;
Radial EBUS; Ion Robotic Bronchoscope; Cios Spin system; Cryobiopsy probe.

ESTIMATED BLOOD LOSS None

COMPLICATIONS None

PROCEDURE IN DETAIL
After the successful induction of anesthesia, a timeout was performed confirming the patient's name, procedure type, and procedure location.

Initial Airway Inspection: Successful therapeutic aspiration was performed to clean out the Right Mainstem, Bronchus Intermedius, and Left Mainstem from mucus.

Robotic Navigational Bronchoscopy (Ion) — {t1_loc} Target
A CT-based navigation plan was loaded into the robotic bronchoscopy platform and partial registration was completed.

Navigation: The Ion robotic catheter was used to engage the {t1_anat} of the {t1_loc} ({t1_seg}).
The target lesion measured approximately {size1} in diameter. Under navigational guidance, the catheter was advanced to 1.0 cm from the planned target.

rEBUS: Radial EBUS confirmed an eccentric nodule location with continuous margins and absence of linear-discrete air bronchogram.

Imaging Verification: Cone Beam CT (Cios Spin) was performed with 3D reconstruction on an independent workstation.
The images were interpreted, and the Ion system was adjusted to the newly acquired nodule location.

Sampling:
TBNA: 21G needle, 4 samples collected.
Cryobiopsy: 1.1mm cryoprobe, 6-second freeze time, 6 samples collected.
Brushing: Protected cytology brush, 1 sample collected.
BAL: 10 cc NS instilled, 5 cc returned.
Fiducial Placement: A 0.8mm x 3mm soft tissue gold marker was placed under fluoroscopy guidance.
ROSE: Conclusive evidence of {rose_result}.

Robotic Navigational Bronchoscopy (Ion) — {t2_loc} Target

Navigation: The Ion robotic catheter was used to engage the {t2_anat} of the {t2_loc} ({t2_seg}).
The target lesion measured approximately {size2} in diameter. The catheter was advanced to 1.0 cm from the target.

rEBUS: Radial EBUS confirmed an eccentric nodule location with continuous margins.

Imaging Verification: Cone Beam CT (Cios Spin) was performed;
3D reconstruction confirmed nodule location and the system was adjusted accordingly.

Sampling:
TBNA: 21G needle, 6 samples collected.
Cryobiopsy: 1.1mm cryoprobe, 6-second freeze time, 6 samples collected.
Brushing: Protected cytology brush, 1 sample collected.
BAL: 10 cc NS instilled, 5 cc returned.
Fiducial Placement: A 0.8mm x 3mm soft tissue gold marker was placed under fluoroscopy guidance.
ROSE: Conclusive evidence of {rose_result}.

Inspection prior to bronchoscope withdrawal demonstrated no evidence of bleeding.

EBUS Staging
The linear EBUS scope was introduced. All lymph node stations were assessed;
only those 5 mm or greater were sampled.

{node_name}: Node measured => 10 mm on CT.
Elastography demonstrated a {node_elast}.

Sampling: TBNA was performed with 4 passes.

Final airway inspection demonstrated no immediate complications. The patient was extubated in the operating room and transported to the recovery room in stable condition.

SPECIMENS
{node_name} TBNA
{t1_loc}: Transbronchial Cryobiopsy (TBCBX), TBNA, Brush, BAL
{t2_loc}: Transbronchial Cryobiopsy (TBCBX), TBNA, Brush, BAL

IMPRESSION / PLAN
Successful robotic bronchoscopy with sampling of {t1_loc} ({t1_seg}) and {t2_loc} ({t2_seg}) nodules.
Cone-beam CT and rEBUS confirmed tool-in-lesion for both targets.
ROSE conclusive for {rose_result} at both lung nodule sites.
EBUS staging of {node_name} performed.
Fiducial markers placed in {t1_loc} and {t2_loc} targets.
Follow-up in clinic.
"""

# ==========================================
# 4. GENERATOR LOGIC
# ==========================================
prompt_styles = [
    # Style 1: Telegraphic / Summary
    "Patient: {age}{gender_short}. Indication: Lung nodules. Procedure: Ion Bronch to {t1_loc} and {t2_loc} + EBUS {node_short}. Findings: {rose_result}.",
    
    # Style 2: Dictation Request
    "Please generate an operative report for a {age}-year-old {gender_long}. We performed a Robotic Navigational Bronchoscopy targeting the {t1_loc} and {t2_loc}, along with EBUS of {node_short}. ROSE was positive for {rose_result}.",
    
    # Style 3: Sloppy / Quick Input
    "{age}yo {gender_short} ion bronch {t1_loc} {t2_loc} and ebus {node_short}. rose showed {rose_result}. fiducials placed. no comps.",
    
    # Style 4: Structured / Clinical Handoff
    "PROCEDURE: Robotic Bronchoscopy (Ion) & EBUS.\nPATIENT: {age} {gender_short}.\nTARGETS: {t1_loc} ({t1_seg}) & {t2_loc} ({t2_seg}).\nNODE: {node_short}.\nRESULT: {rose_result}.",
    
    # Style 5: Billing / Coding Focus
    "Op Note needed. Dx: R91.8, {rose_result}. Proc: Ion Nav Bronch ({t1_loc}/{t2_loc}), 3D Spin, EBUS ({node_short}), Cryobiopsy. Attending: {attending}."
]

def generate_dataset():
    dataset = []
    
    for _ in range(NUM_SAMPLES):
        # A. Randomly select variables
        age = random.choice(data_pool["ages"])
        gender_tup = random.choice(data_pool["genders"]) # (long, short, cap)
        attending = random.choice(data_pool["attendings"])
        assistant = random.choice(data_pool["assistants"])
        ref_phys = "Referred" # Placeholder or could be randomized
        
        # Select Targets (Ensure they aren't the exact same for realism, though code allows random)
        t1 = random.choice(data_pool["target_1_options"]) # (Loc, Seg, Anat)
        t2 = random.choice(data_pool["target_2_options"])
        
        # Select Lesion Sizes
        size1 = random.choice(data_pool["lesion_sizes"])
        size2 = random.choice(data_pool["lesion_sizes"])
        
        # Select ROSE Result
        rose = random.choice(data_pool["rose_results"])
        
        # Select Lymph Node
        node_data = random.choice(data_pool["lymph_nodes"]) # (Name, Elastography)
        node_short = node_data[0].split('(')[0].strip() # e.g., "Station 7"
        
        # B. Generate Prompt
        style = random.choice(prompt_styles)
        prompt = style.format(
            age=age,
            gender_short=gender_tup[1],
            gender_long=gender_tup[0],
            t1_loc=t1[0], t1_seg=t1[1],
            t2_loc=t2[0], t2_seg=t2[1],
            node_short=node_short,
            rose_result=rose,
            attending=attending
        )
        
        # C. Generate Completion
        completion = note_template.format(
            note_id=NOTE_ID,
            age=age,
            gender_long=gender_tup[0],
            gender_long_cap=gender_tup[2].capitalize() + " is a " + age, # "He is a 67..."
            ref_phys=ref_phys,
            attending=attending,
            assistant=assistant,
            t1_loc=t1[0], t1_seg=t1[1], t1_anat=t1[2],
            t2_loc=t2[0], t2_seg=t2[1], t2_anat=t2[2],
            size1=size1,
            size2=size2,
            rose_result=rose,
            node_name=node_data[0],
            node_elast=node_data[1]
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