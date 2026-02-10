import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_047"
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
    "age": ["62", "68", "71", "74", "77", "81", "85"],
    "gender_tuple": [("female", "F"), ("male", "M")],
    "referring_md": ["Dr. Smith", "Dr. Patel", "Dr. Henderson", "Dr. Lee", "Dr. Gomez"],
    "attending": ["Dr. Ingraham", "Dr. Bowers", "Dr. Chen", "Dr. Wilson"],
    "assistant": ["Dr. Roberts (Fellow)", "Dr. Kim (Fellow)", "Dr. Davis (Fellow)"],
    
    # Primary Target (Successful)
    "prim_loc_tuple": [
        ("LUL", "Anterior Segment", "LB3"),
        ("RUL", "Apical Segment", "RB1"),
        ("RUL", "Posterior Segment", "RB2"),
        ("LUL", "Apico-posterior Segment", "LB1+2"),
        ("RLL", "Superior Segment", "RB6")
    ],
    "prim_size": ["1.2 cm", "1.5 cm", "2.0 cm", "2.4 cm", "3.1 cm"],
    "prim_rose": [
        "Conclusive evidence of malignant neoplasm",
        "Suspicious for malignancy",
        "Atypical cells present",
        "Granulomatous inflammation",
        "Non-small cell lung carcinoma"
    ],
    "prim_cryo_samples": ["3", "4", "5", "6"],
    
    # Secondary Target (Aborted/Failed)
    "sec_loc_tuple": [
        ("RLL", "Lateral-basal Segment", "RB9"),
        ("LLL", "Posterior-basal Segment", "LB10"),
        ("RML", "Lateral Segment", "RB4"),
        ("LUL", "Lingular Segment", "LB5")
    ],
    "sec_size": ["0.8 cm", "0.9 cm", "1.0 cm", "1.1 cm"],
    
    # EBUS Data
    "ebus_stations_group": [
        {
            "s1": "11Rs", "s1_size": "<10 mm", "s1_elast": "Type 1 (predominantly soft/benign)",
            "s2": "7", "s2_size": "≥10 mm", "s2_elast": "Type 2 (mixed soft/stiff)",
            "s3": "11L", "s3_size": "<10 mm", "s3_elast": "Type 2 (mixed soft/stiff)"
        },
        {
            "s1": "4R", "s1_size": "≥10 mm", "s1_elast": "Type 2 (mixed soft/stiff)",
            "s2": "7", "s2_size": "≥12 mm", "s2_elast": "Type 3 (predominantly stiff)",
            "s3": "4L", "s3_size": "<10 mm", "s3_elast": "Type 1 (predominantly soft/benign)"
        },
        {
            "s1": "10R", "s1_size": "<8 mm", "s1_elast": "Type 1 (soft)",
            "s2": "7", "s2_size": "≥15 mm", "s2_elast": "Type 2 (mixed)",
            "s3": "11L", "s3_size": "<10 mm", "s3_elast": "Type 1 (soft)"
        }
    ]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
note_template = """INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: [Date] CC Referred Physician: {referring_md}

INDICATION FOR OPERATION [REDACTED] is a {age}-year-old {gender_long} who presents with a lung nodule.
The nature, purpose, risks, benefits, and alternatives to bronchoscopy were discussed with the patient in detail.
The patient wished to proceed and informed consent was signed.

CONSENT Obtained before the procedure.
Indications, potential complications, and alternatives were discussed with the patient.
PREOPERATIVE DIAGNOSIS

R91.1 Solitary Lung Nodule 

POSTOPERATIVE DIAGNOSIS

R91.1 Solitary Lung Nodule 

{prim_lobe} nodule: {prim_rose} on ROSE 

PROCEDURE

Robotic navigational bronchoscopy (Ion) to {prim_lobe} target ({prim_seg}) 

Radial EBUS (rEBUS) verification 

Cone-beam CT (Cios Spin) with 3D reconstruction and tool-in-lesion confirmation 

Target sampling: TBNA (4 passes), Forceps biopsy (1 sample), Transbronchial cryobiopsy ({prim_cryo_samples} samples), Brush (1 sample), BAL 

Fiducial marker placement ({prim_lobe}) 

Attempted sampling of {sec_lobe} target (Aborted due to inability to identify on CBCT) 

EBUS-TBNA staging (Stations {s1}, {s2}, {s3}) with Elastography 

ATTENDING {attending}

ASSISTANT {assistant}

SUPPORT STAFF RN: [Name] RT: [Name]

ANESTHESIA General Anesthesia 

MONITORING Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer throughout the procedure.
INSTRUMENTATION Flexible Therapeutic Bronchoscope, Linear EBUS, Radial EBUS, Ion Robotic Bronchoscope, Cios Spin system.
ESTIMATED BLOOD LOSS None 

COMPLICATIONS None 

PROCEDURE IN DETAIL After successful induction of anesthesia, a timeout was performed confirming the patient's name, procedure type, and location.
Airway Inspection and Preparation Therapeutic aspiration was performed to clear the Right Mainstem, Bronchus Intermedius, and Left Mainstem of mucus.
A CT chest scan was loaded onto the planning station to generate a 3D rendering of the pathway, which was verified and loaded into the robotic platform.
Robotic Navigational Bronchoscopy (Ion) — {prim_lobe} Nodule


Target: {prim_seg} of {prim_lobe} ({prim_lb_code}); lesion approximately {prim_size}.
Navigation: The Ion robotic catheter was engaged and advanced to 1.0 cm from the planned target under navigational guidance.
rEBUS: Radial EBUS confirmed an eccentric location with a continuous margin and absence of a linear-discrete air bronchogram.
Cone-Beam CT (Cios Spin): A low-dose spin was performed to acquire CT imaging.
The 3D reconstructions were interpreted on the Ion workstation, and the robotic system was adjusted to the newly acquired nodule location.
Sampling:

TBNA: Transbronchial needle aspiration with 21G needle; 4 samples collected.

Biopsy: Transbronchial biopsy with alligator forceps; 1 sample collected.
Cryobiopsy: Transbronchial cryobiopsy performed with 1.1mm probe (6-second freeze); {prim_cryo_samples} samples collected.
Note: This required substantially greater work due to technical difficulty.

Brushing: Transbronchial brushing performed; 1 sample collected.
BAL: Lavage performed with 10 cc NS instilled, 5 cc return.
Fiducial Placement: A 0.8mm x 3mm soft tissue gold marker was loaded with bone wax and placed under fluoroscopic guidance.
ROSE: {prim_rose}.

Robotic Navigational Bronchoscopy (Ion) — {sec_lobe} Nodule (Attempted)


Target: {sec_seg} of {sec_lobe} ({sec_lb_code});
lesion approximately {sec_size}.


Navigation: Catheter advanced to 1.0 cm from target.


rEBUS: Nodule not visible.
Cone-Beam CT: Two spins were performed to assess the area, but the {sec_lobe} nodule was not identified on the system.
Outcome: Procedure aborted for this target due to inability to identify the nodule.
EBUS STAGING Endobronchial ultrasound (EBUS) was performed for diagnostic and staging purposes.
All lymph node stations were assessed, and those ≥5 mm were considered for sampling.
Elastography was used to assess stiffness (Types 1-3).

Station {s1} ({s1_size}):

Elastography: {s1_elast}.
Sampling: 4 biopsies performed (TBNA) despite benign appearance to confirm absence of malignancy.
Station {s2} ({s2_size}):

Elastography: {s2_elast}.

Sampling: 4 biopsies performed (TBNA) directed at representative areas.
Station {s3} ({s3_size}):

Elastography: {s3_elast}.

Sampling: 4 biopsies performed (TBNA) directed at representative areas.
The patient tolerated the procedure well with no immediate complications.
SPECIMENS

{prim_lobe} Target: TBCBX (Cryo), TBNA, TBBX (Forceps), BAL, Brush 

EBUS TBNA: Stations {s1}, {s2}, {s3} 

IMPRESSION / PLAN

{age}-year-old {gender_long} with lung nodule.
Successful sampling of {prim_lobe} nodule ({prim_lb_code}) with ROSE showing {prim_rose_lower}.

Fiducial marker placed in {prim_lobe} target.
{sec_lobe} target sampling aborted due to inability to visualize lesion on CBCT.
EBUS staging completed at stations {s1}, {s2}, and {s3}.

Follow-up in clinic.
"""

# <--- 5 DISTINCT PROMPT STYLES --->
prompt_styles = [
    # Style 1: Telegraphic
    "Ion bronch {age}yo {gender_short}. Target 1: {prim_lobe} ({prim_seg}), ROSE {prim_rose_lower}, fiducial placed. Target 2: {sec_lobe} ({sec_seg}), aborted (cant see on CBCT). EBUS {s1}, {s2}, {s3}.",
    
    # Style 2: Dictation
    "Write an op note for Dr. {attending}. Patient is {age}, {gender_long}. We did a robotic bronch. The {prim_lobe} nodule in the {prim_seg} was sampled successfully with {prim_cryo_samples} cryo passes and ROSE showed {prim_rose_lower}. We tried to get the {sec_lobe} nodule but couldn't find it on the cone beam CT so we aborted that part. Finished with EBUS staging at {s1}, {s2}, and {s3}.",
    
    # Style 3: Sloppy / Quick
    "{age} {gender_short} lung nodule. Ion/EBUS. {prim_lobe} found -> malignant. {sec_lobe} aborted (not viz). EBUS stations {s1}/{s2}/{s3} sampled. No comps.",
    
    # Style 4: Billing Focus
    "Procedure: Robotic Bronchoscopy + EBUS. {age}y {gender_short}. Sites: {prim_lobe} (success, malignant), {sec_lobe} (aborted/failed visualization). EBUS nodes {s1}, {s2}, {s3}. Cryobiopsy used.",
    
    # Style 5: Structured
    "Patient: {age} {gender_short}\nAttending: {attending}\nProcedure: Ion Bronchoscopy\nTarget 1: {prim_lobe} {prim_seg} (Successful, {prim_rose_lower})\nTarget 2: {sec_lobe} (Aborted, not seen on CBCT)\nStaging: EBUS {s1}, {s2}, {s3}"
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
        referring_md = random.choice(data_pool["referring_md"])
        attending = random.choice(data_pool["attending"])
        assistant = random.choice(data_pool["assistant"])
        
        # Primary Target (Success)
        prim_tup = random.choice(data_pool["prim_loc_tuple"])
        prim_lobe, prim_seg, prim_lb_code = prim_tup
        prim_size = random.choice(data_pool["prim_size"])
        prim_rose = random.choice(data_pool["prim_rose"])
        prim_cryo_samples = random.choice(data_pool["prim_cryo_samples"])
        
        # Secondary Target (Failure) - ensure lobe is different from primary
        sec_tup = random.choice(data_pool["sec_loc_tuple"])
        while sec_tup[0] == prim_lobe: # Retry if same lobe
             sec_tup = random.choice(data_pool["sec_loc_tuple"])
        sec_lobe, sec_seg, sec_lb_code = sec_tup
        sec_size = random.choice(data_pool["sec_size"])
        
        # EBUS
        ebus_group = random.choice(data_pool["ebus_stations_group"])
        
        # B. Generate Prompt
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, gender_short=gender_tup[1], gender_long=gender_tup[0],
            attending=attending,
            prim_lobe=prim_lobe, prim_seg=prim_seg, prim_rose_lower=prim_rose.lower(), prim_cryo_samples=prim_cryo_samples,
            sec_lobe=sec_lobe, sec_seg=sec_seg,
            s1=ebus_group["s1"], s2=ebus_group["s2"], s3=ebus_group["s3"]
        )
        
        # C. Generate Completion
        completion = note_template.format(
            note_id=NOTE_ID,
            age=age, gender_long=gender_tup[0],
            referring_md=referring_md, attending=attending, assistant=assistant,
            
            # Primary
            prim_lobe=prim_lobe, prim_seg=prim_seg, prim_lb_code=prim_lb_code,
            prim_size=prim_size, prim_rose=prim_rose, prim_rose_lower=prim_rose.lower(),
            prim_cryo_samples=prim_cryo_samples,
            
            # Secondary
            sec_lobe=sec_lobe, sec_seg=sec_seg, sec_lb_code=sec_lb_code,
            sec_size=sec_size,
            
            # EBUS
            s1=ebus_group["s1"], s1_size=ebus_group["s1_size"], s1_elast=ebus_group["s1_elast"],
            s2=ebus_group["s2"], s2_size=ebus_group["s2_size"], s2_elast=ebus_group["s2_elast"],
            s3=ebus_group["s3"], s3_size=ebus_group["s3_size"], s3_elast=ebus_group["s3_elast"]
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