import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_070"
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
    "age": ["34", "41", "49", "51", "55", "62", "67", "71", "74", "80"],
    "gender_tuple": [("female", "F"), ("male", "M")],
    "referring_md": ["Smith", "Patel", "Johnson", "Garcia", "Wong", "Self", "ED Physician"],
    "attending_md": ["Dr. Ingraham", "Dr. Bowers", "Dr. Chen", "Dr. Miller"],
    "fellow_md": ["Dr. Lee", "Dr. Jacobs", "Dr. Khan", "Dr. Doe"],
    "rn_name": ["S. Jones", "M. Davis", "L. White"],
    "rt_name": ["K. Brown", "J. Wilson", "T. Clark"],
    
    # Diagnosis and Indications
    "diagnosis": [
        {"code": "R91.1", "desc": "Solitary Lung Nodule"},
        {"code": "R91.8", "desc": "Other nonspecific abnormal finding of lung field"},
        {"code": "C34.11", "desc": "Malignant neoplasm of upper lobe, right bronchus or lung"},
        {"code": "D14.31", "desc": "Benign neoplasm of right bronchus and lung"}
    ],

    # Linked Target Data (Lobe + Segment + Pathway difficulty)
    "target_data": [
        {"lobe": "RUL", "seg": "Anterior Segment of the RUL (RB3)", "side": "Right"},
        {"lobe": "RUL", "seg": "Apical Segment of the RUL (RB1)", "side": "Right"},
        {"lobe": "RLL", "seg": "Superior Segment of the RLL (RB6)", "side": "Right"},
        {"lobe": "LUL", "seg": "Apical-Posterior Segment (LB1+2)", "side": "Left"},
        {"lobe": "LUL", "seg": "Anterior Segment of the LUL (LB3)", "side": "Left"},
        {"lobe": "LLL", "seg": "Posterior Basal Segment (LB10)", "side": "Left"}
    ],

    "nodule_size": ["0.8 cm", "1.0 cm", "1.2 cm", "1.5 cm", "2.1 cm", "2.8 cm"],
    
    # Balloon Details
    "balloon": [
        {"size": "5mm x 20mm Mustang", "reason": "small carina"},
        {"size": "6mm x 40mm Mustang", "reason": "airway stenosis"},
        {"size": "7mm x 20mm Mustang", "reason": "tortuous airway anatomy"}
    ],

    # ROSE / Pathology Results
    "rose_result": [
        "conclusive for malignant neoplasm (lung nodule)",
        "suspicious for malignancy",
        "diagnostic for granulomatous inflammation",
        "conclusive for adenocarcinoma",
        "conclusive for squamous cell carcinoma"
    ],
    
    # EBUS Station 7 Details
    "station_7_status": [
        {"size": "≥ 10 mm", "elast": "Type 2 elastographic pattern (mixed soft and stiff regions)", "action": "Sampled"},
        {"size": "< 10 mm", "elast": "Type 1 elastographic pattern (predominantly soft/benign)", "action": "Not sampled (not clinically indicated)"},
        {"size": "15 mm", "elast": "Type 3 elastographic pattern (stiff/blue)", "action": "Sampled"}
    ]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
# Based on note_070.txt structure
note_template = """NOTE_ID: {note_id}
SOURCE_FILE: {note_id}.txt

INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: [Date] CC Referred Physician: {ref_md}

INDICATION FOR OPERATION {age}-year-old {gender_long} who presents with a {dx_desc} ({dx_code}) requiring bronchoscopic diagnosis and staging.

The nature, purpose, risks, benefits, and alternatives to bronchoscopy were discussed with the patient in detail.

CONSENT Obtained before the procedure. Indications, potential complications, and alternatives were discussed with the patient or surrogate.

Consent was signed and witnessed by an assisting medical professional.

PREOPERATIVE DIAGNOSIS

{dx_code} {dx_desc}

POSTOPERATIVE DIAGNOSIS

{dx_code} {dx_desc}

ROSE {rose_res} 

PROCEDURE

Therapeutic aspiration (initial airway clearance) 

Robotic navigational bronchoscopy (Ion) to {target_lobe} target 

Balloon dilation of airway 

Radial EBUS (rEBUS) localization 

Cone-beam CT imaging (Cios Spin) with 3D reconstruction 

TBNA of {target_lobe} target (6 samples) 

Transbronchial biopsy (TBBX) of {target_lobe} target (2 samples) 

Transbronchial cryobiopsy of {target_lobe} target (6 samples) 

Transbronchial brushing of {target_lobe} target 

Bronchoalveolar lavage (BAL) 

Fiducial marker placement 

EBUS-TBNA staging (Station 7) with elastography 

ATTENDING {attending}

ASSISTANT {fellow}

SUPPORT STAFF RN: {rn} RT: {rt}

ANESTHESIA General Anesthesia 

MONITORING Pulse oximetry, heart rate, telemetry, and 
BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.

INSTRUMENTATION Linear EBUS, Radial EBUS, Ion Robotic Bronchoscope, Disposable Bronchoscope, Cios Spin system.

ESTIMATED BLOOD LOSS None 

COMPLICATIONS None 

PROCEDURE IN DETAIL After the successful induction of anesthesia, a timeout was performed confirming the patient's name, procedure type, and procedure location.

Initial Airway Inspection & Therapeutic Aspiration Successful therapeutic aspiration was performed to clean out the Right Mainstem, Bronchus Intermedius, and Left Mainstem from mucus.

Robotic Navigational Bronchoscopy (Ion) — {target_lobe} Nodule A CT scan was used to generate a 3D rendering of the pathway, which was verified and loaded into the robotic platform.

Robotic navigation was performed with the Ion platform using partial registration.

The robotic catheter was used to engage the {target_seg}.

The target lesion measured approximately {nodule_size} in diameter.

Balloon Dilation Significant difficulties were encountered during navigation due to a {balloon_reason}.
A {balloon_size} balloon was used to dilate the distal airway under direct fluoro-guidance using Omnipaque 240 as the inflation agent.

Following dilation, the robotic bronchoscope was successfully navigated to the distal nodule.

Target Localization & Confirmation


Navigation: The Ion catheter was advanced to 1.0 cm away from the planned target.

Radial EBUS: Performed to confirm location; the nodule appeared Eccentric with a continuous margin.

Cone-Beam CT (Cios Spin): A low-dose spin was performed to acquire CT imaging.

3D reconstructions were interpreted on an independent workstation and passed to the Ion platform.

Adjustment: Using the newly acquired nodule location, the Ion robotic system was adjusted to the new targeted location.

I personally interpreted the cone beam CT and 3-D reconstruction.

{target_lobe} Target Sampling


TBNA: Transbronchial needle aspiration was performed with a 21G needle; total 6 samples collected for Cytology.

Forceps Biopsy: Transbronchial biopsy was performed with alligator forceps; total 2 samples collected for Pathology.

Cryobiopsy: Transbronchial cryobiopsy was performed with a 1.1mm cryoprobe (6-second freeze time); total 6 samples collected for Pathology.

Note: This patient required Transbronchial Cryobiopsies, resulting in >40% increased work due to technical difficulty and physical/mental effort required.

Brushing: Transbronchial brushing performed with a protected cytology brush; 1 sample collected for Microbiology.

BAL: Bronchoalveolar lavage performed with 40 cc NS instilled and 15 cc returned; sent for Cell Count, Microbiology, and Cytology.

Fiducial Placement: A fiducial marker (0.8mm x 3mm soft tissue gold CIVCO) was loaded with bone wax and placed under fluoroscopy guidance prior to withdrawal.

ROSE (Ion Procedure) {rose_res}.

EBUS STAGING


Indications: Diagnostic and Staging. Technique: All lymph node stations were assessed.

Only those 5 mm or greater in short axis were sampled.

Lymph node sizing was performed by EBUS and elastography was used to assess stiffness.

Lymph Nodes Evaluated:

Station 11L: < 10 mm. Type 1 elastographic pattern (predominantly soft/benign). Not sampled (not clinically indicated).

Station 7 (Subcarinal): {st7_size}. {st7_elast}. {st7_action}.

Station 4R (Lower Paratracheal): < 10 mm.
Type 1 elastographic pattern (predominantly soft/benign). Not sampled (not clinically indicated).

Station 11Rs: < 10 mm.
Type 1 elastographic pattern (predominantly soft/benign). Not sampled (not clinically indicated).


Also Inspected: 4L (lower paratracheal).

COMPLICATIONS There were no immediate complications.

SPECIMENS

{target_lobe} Lung Nodule: TBNA, TBBX (Forceps), TBBX (Cryo), Brush, BAL 

Station 7: TBNA 

IMPRESSION / PLAN

{age}-year-old {gender_long} with {dx_desc_lower}.
Successful sampling of {target_lobe} nodule and Station 7 lymph node.

ROSE from lung nodule showed {rose_res}.
Follow-up results in clinic.

Follow-up CXR.
"""

# <--- CREATE 5 DISTINCT PROMPT STYLES HERE --->
prompt_styles = [
    # Style 1: Telegraphic
    "Operative note IP. {age}{gender_short}, ref {ref_md}. Dx: {dx_code} {dx_desc}. Proc: Ion bronch to {target_lobe} ({target_seg}), {nodule_size}. Need balloon dilation ({balloon_reason}). ROSE: {rose_short}. EBUS St 7 {st7_action}.",
    
    # Style 2: Dictation
    "Please generate a procedure note for Dr. {attending}. The patient is a {age}-year-old {gender_long} referred by {ref_md}. Indication is {dx_desc}. We performed a Robotic Navigational Bronchoscopy on a {nodule_size} target in the {target_lobe}, specifically the {target_seg}. We used a {balloon_size} balloon due to {balloon_reason}. EBUS Station 7 was {st7_action}. ROSE was {rose_short}.",
    
    # Style 3: Sloppy / Quick
    "{age}yo {gender_short} {dx_code}. Ion bronch {target_lobe} {nodule_size} lesion. {balloon_reason} so used balloon. EBUS 7 {st7_action}. rose {rose_short}. no comps.",
    
    # Style 4: Billing Focus
    "Billing: Ion Bronchoscopy, EBUS, Cryobiopsy. Patient: {age} {gender_short}. Dx: {dx_code}. Target: {target_lobe} ({nodule_size}). Interventions: Balloon dilation ({balloon_size}), Fiducial placement. ROSE: {rose_short}.",
    
    # Style 5: Structured
    "Patient: {age} {gender_short}\nDiagnosis: {dx_desc} ({dx_code})\nProcedure: Ion Robotic Bronchoscopy + EBUS\nTarget: {target_lobe}, {target_seg}\nNodule Size: {nodule_size}\nBalloon Used: Yes ({balloon_size})\nROSE Results: {rose_short}"
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
        ref_md = random.choice(data_pool["referring_md"])
        attending = random.choice(data_pool["attending_md"])
        fellow = random.choice(data_pool["fellow_md"])
        rn = random.choice(data_pool["rn_name"])
        rt = random.choice(data_pool["rt_name"])
        
        dx_obj = random.choice(data_pool["diagnosis"])
        
        target = random.choice(data_pool["target_data"])
        nodule_size = random.choice(data_pool["nodule_size"])
        
        balloon = random.choice(data_pool["balloon"])
        
        rose = random.choice(data_pool["rose_result"])
        rose_short = rose.split(" (")[0] if "(" in rose else rose # simplify for prompt
        
        st7 = random.choice(data_pool["station_7_status"])

        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_tup[1], 
            gender_long=gender_tup[0],
            ref_md=ref_md,
            attending=attending,
            dx_code=dx_obj["code"],
            dx_desc=dx_obj["desc"],
            target_lobe=target["lobe"],
            target_seg=target["seg"],
            nodule_size=nodule_size,
            balloon_size=balloon["size"],
            balloon_reason=balloon["reason"],
            rose_short=rose_short,
            st7_action=st7["action"]
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            age=age, 
            gender_long=gender_tup[0],
            ref_md=ref_md,
            dx_desc=dx_obj["desc"],
            dx_desc_lower=dx_obj["desc"].lower(),
            dx_code=dx_obj["code"],
            rose_res=rose,
            target_lobe=target["lobe"],
            target_seg=target["seg"],
            nodule_size=nodule_size,
            balloon_reason=balloon["reason"],
            balloon_size=balloon["size"],
            attending=attending,
            fellow=fellow,
            rn=rn,
            rt=rt,
            st7_size=st7["size"],
            st7_elast=st7["elast"],
            st7_action=st7["action"]
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