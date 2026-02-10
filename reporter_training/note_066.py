import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_066"
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
    "age": [str(x) for x in range(55, 88)],
    "gender_tuple": [("female", "F"), ("male", "M")],
    "attending": [
        "Dr. Smith", "Dr. Chen", "Dr. Rodriguez", "Dr. Patel", "Dr. Bowers", "Dr. Weiss"
    ],
    "ventilation_settings": [
        {"mode": "VCV", "rr": "14", "tv": "350", "peep": "10", "fio2": "100%", "flow": "10", "pmean": "15"},
        {"mode": "VCV", "rr": "12", "tv": "400", "peep": "8", "fio2": "80%", "flow": "12", "pmean": "14"},
        {"mode": "PCV", "rr": "16", "tv": "300", "peep": "12", "fio2": "100%", "flow": "10", "pmean": "18"},
    ],
    # Tuples of (Segment Name, Segment ID)
    "rul_targets": [
        ("Anterior Segment", "RB3"),
        ("Apical Segment", "RB1"),
        ("Posterior Segment", "RB2")
    ],
    "rll_targets": [
        ("Superior Segment", "RB6"),
        ("Posterior Basal Segment", "RB10"),
        ("Lateral Basal Segment", "RB9"),
        ("Medial Basal Segment", "RB7")
    ],
    "lul_targets": [
        ("Apical-Posterior Segment", "LB1/2"),
        ("Anterior Segment", "LB3"),
        ("Superior Lingular Segment", "LB4")
    ],
    # Tuples of (View, Margin Description)
    "rebus_features": [
        ("eccentric", "continuous margin"),
        ("concentric", "continuous margins"),
        ("eccentric", "discontinuous margin"),
        ("concentric", "slightly irregular margin")
    ],
    "nodule_size": ["0.8 cm", "1.0 cm", "1.2 cm", "1.5 cm", "1.8 cm", "2.1 cm"],
    "catheter_dist": ["0.5 cm", "1.0 cm", "1.5 cm", "touching the target"],
    # Tuples of (Instilled, Return)
    "bal_volumes": [
        ("20", "10"), ("20", "5"), ("30", "12"), ("40", "15"), ("50", "20"), ("20", "8")
    ],
    "tbna_samples": ["3", "4", "5"],
    "cryo_samples": ["3", "4", "5", "6"],
    "fiducial_type": ["0.8mm x 3mm soft tissue gold marker", "0.9mm x 4mm coil marker"],
    "diagnosis_code": [
        ("R91.8", "Other nonspecific abnormal finding of lung field"),
        ("R91.1", "Solitary pulmonary nodule")
    ]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
note_template = """NOTE_ID: {note_id}
DATE OF PROCEDURE: [Date]

ATTENDING PHYSICIAN: {attending}

INDICATION FOR OPERATION: The patient is a {age}-year-old {gender_long} who presents with lung nodules.
The nature, purpose, risks, benefits, and alternatives to bronchoscopy were discussed with the patient in detail.
CONSENT Obtained before the procedure.

PREOPERATIVE DIAGNOSIS
{dx_code} {dx_name}.

POSTOPERATIVE DIAGNOSIS
{dx_code} {dx_name}.

PROCEDURE
Robotic navigation bronchoscopy (Ion) to RUL, RLL, and LUL targets.
Radial EBUS for peripheral lesions.
Cone-beam CT (Cios Spin) with 3D rendering and instrument guidance.
Transbronchial needle aspiration (TBNA) of single and additional lobes.
Transbronchial biopsy (TBBX) of single and additional lobes.
Transbronchial cryobiopsy.
Transbronchial brushing.
Bronchoalveolar lavage (BAL).
Fiducial marker placement.
Bronchoscopy with Endobronchial Ultrasound (EBUS) of mediastinal/hilar lymph nodes without biopsy.

ANESTHESIA General Anesthesia.

MONITORING Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.
INSTRUMENTATION Linear EBUS, Radial EBUS, Ion Robotic Bronchoscope, Disposable Bronchoscope, Cios Spin system.

ESTIMATED BLOOD LOSS None.

COMPLICATIONS None.

PROCEDURE IN DETAIL
After the successful induction of anesthesia, a timeout was performed confirming the patient's name, procedure type, and procedure location.
A CT Chest scan was placed on a separate planning station to generate a 3D rendering of the pathway to the target.
The navigational plan was reviewed, verified, and loaded into the robotic bronchoscopy platform.
Successful therapeutic aspiration was performed to clean out the Right Mainstem, Bronchus Intermedius, and Left Mainstem from mucus.
Ventilation Parameters: Mode: {vent_mode}; RR: {vent_rr}; TV: {vent_tv}; PEEP: {vent_peep}; FiO2: {vent_fio2}; Flow Rate: {vent_flow};
Pmean: {vent_pmean}.

RUL Target ({rul_seg_name} {rul_seg_id}) Robotic navigation bronchoscopy was performed with the Ion platform using partial registration.
The Ion robotic catheter was used to engage the {rul_seg_name} of the RUL ({rul_seg_id}).
The target lesion is about {rul_size} in diameter, and the catheter was advanced to {rul_dist} away from the planned target under navigational guidance.
rEBUS: Radial EBUS confirmed an {rul_rebus_type} nodule location. Features noted included {rul_rebus_margin} and absence of linear-discrete air bronchogram.
Imaging: Cone Beam CT (Cios Spin) was performed for evaluation of nodule location.
3D reconstructions were performed on an independent workstation and passed to the Ion platform.
The robotic system was adjusted to the new targeted location based on this imaging.

Sampling:
TBNA: performed with 21G needle; {rul_tbna_n} samples collected and sent for cytology.
TBBX: performed with alligator forceps; 1 sample collected and sent for pathology.
Cryobiopsy: performed with 1.1mm cryoprobe (6-second freeze); {rul_cryo_n} samples collected and sent for pathology.
Brushing: performed with protected cytology brush; 1 sample collected and sent for microbiology.
BAL: Instilled {rul_bal_in} cc NS, return {rul_bal_out} cc; sent for microbiology.
Fiducial Marker: One {fiducial} was placed under fluoroscopy guidance.
ROSE: No evidence of malignant neoplasm.

RLL Target ({rll_seg_name} {rll_seg_id}) Robotic navigation bronchoscopy was performed with the Ion platform using partial registration to engage the {rll_seg_name} of the RLL ({rll_seg_id}).
The target lesion is about {rll_size} in diameter, and the catheter was advanced to {rll_dist} away from the planned target.
rEBUS: Radial EBUS confirmed a {rll_rebus_type} nodule location with {rll_rebus_margin}.
Imaging: Cone Beam CT (Cios Spin) was performed with 3D reconstruction to evaluate and adjust nodule location.
Sampling:
TBNA: performed with 21G needle; {rll_tbna_n} samples collected and sent for cytology.
Cryobiopsy: performed with 1.1mm cryoprobe (6-second freeze); {rll_cryo_n} samples collected and sent for pathology.
Brushing: performed with protected cytology brush; 1 sample collected and sent for microbiology.
BAL: Instilled {rll_bal_in} cc NS, return {rll_bal_out} cc; sent for cell count, microbiology, and cytology.
Fiducial Marker: One {fiducial} was placed under fluoroscopy guidance.
ROSE: No evidence of malignant neoplasm.

LUL Target ({lul_seg_name} {lul_seg_id}) Robotic navigation bronchoscopy was performed with the Ion platform using partial registration to engage the {lul_seg_name} of the LUL ({lul_seg_id}).
The target lesion is about {lul_size} in diameter, and the catheter was advanced to {lul_dist} away from the planned target.
rEBUS: Radial EBUS confirmed an {lul_rebus_type} nodule location. Features noted included {lul_rebus_margin} and absence of linear-discrete air bronchogram.
Imaging: Cone Beam CT (Cios Spin) was performed with 3D reconstruction to evaluate and adjust nodule location.
Sampling:
TBNA: performed with 21G needle; {lul_tbna_n} samples collected and sent for cytology.
Cryobiopsy: performed with 1.1mm cryoprobe (6-second freeze); {lul_cryo_n} samples collected and sent for pathology.
Brushing: performed with protected cytology brush; 1 sample collected and sent for microbiology.
BAL: Instilled {lul_bal_in} cc NS, return {lul_bal_out} cc; sent for microbiology.
Fiducial Marker: One {fiducial} was placed under fluoroscopy guidance.
ROSE: No evidence of malignant neoplasm.

Prior to withdrawal of the bronchoscope, inspection demonstrated no evidence of bleeding.

EBUS STAGING
Indications: Diagnostic. Technique: All lymph node stations were assessed.
Only those 5 mm or greater in short axis were considered for sampling.
Lymph Nodes Inspected:
4R (lower paratracheal)
4L (lower paratracheal)
7 (subcarinal)
10R, 10L (hilar)
11Rs, 11Ri, 11L (interlobar).
Findings: Lymph node sizing was performed by EBUS; no sampling was done as none met biopsy criteria.
Endobronchial ultrasound (EBUS) elastography was performed to assess lymph node stiffness (Type 1–3).

CONCLUSION The patient tolerated the procedure well.
There were no immediate complications. At the conclusion of the operation, the patient was extubated in the operating room and transported to the recovery room in stable condition.

SPECIMENS
RUL: TBNA, TBCBX, Brush, BAL, TBBX.
RLL: TBNA, TBCBX, Brush, BAL.
LUL: TBNA, TBCBX, Brush, BAL.

IMPRESSION / PLAN
{age}-year-old {gender_long} who presented for bronchoscopy for lung nodules.
Successful sampling of RUL, RLL, and LUL nodules using robotic navigation and cone-beam CT guidance.
Follow up in clinic for results.
"""

prompt_styles = [
    # Style 1: Telegraphic
    "Operative Report. {age}yo {gender_short}, {attending}. Robotic bronch Ion 3 targets: RUL {rul_seg_id}, RLL {rll_seg_id}, LUL {lul_seg_id}. All fiducials placed. EBUS neg.",
    
    # Style 2: Dictation
    "Write an op note for a {age} year old {gender_long} patient. Procedure was Robotic Navigation Bronchoscopy using the Ion system. We targeted three lesions: RUL {rul_seg_name}, RLL {rll_seg_name}, and LUL {lul_seg_name}. We did TBNA, cryo, brush, and BAL for all. Also did EBUS staging, but no nodes were sampled.",
    
    # Style 3: Sloppy / Quick
    "{age} {gender_short} lung nodules. Robotic bronch + EBUS. Targets: RUL ({rul_seg_id}), RLL ({rll_seg_id}), LUL ({lul_seg_id}). Fiducials placed in all. No complications.",
    
    # Style 4: Billing Focus
    "Procedure Code: Robotic Bronchoscopy with EBUS. Patient: {age} {gender_short}. Targets: RUL {rul_seg_id}, RLL {rll_seg_id}, LUL {lul_seg_id}. Specimen collected: TBNA, Cryo, Brush, BAL. Fiducials placed.",
    
    # Style 5: Structured
    "PATIENT: {age} / {gender_short}\nPROCEDURE: Ion Robotic Bronchoscopy + EBUS\nTARGETS:\n1. RUL {rul_seg_id} ({rul_size})\n2. RLL {rll_seg_id} ({rll_size})\n3. LUL {lul_seg_id} ({lul_size})\nFINDINGS: EBUS negative. Successful sampling of all nodules."
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
        attending = random.choice(data_pool["attending"])
        vent = random.choice(data_pool["ventilation_settings"])
        dx = random.choice(data_pool["diagnosis_code"])
        fiducial = random.choice(data_pool["fiducial_type"])
        
        # RUL Target Vars
        rul_target = random.choice(data_pool["rul_targets"])
        rul_rebus = random.choice(data_pool["rebus_features"])
        rul_size = random.choice(data_pool["nodule_size"])
        rul_dist = random.choice(data_pool["catheter_dist"])
        rul_bal = random.choice(data_pool["bal_volumes"])
        rul_tbna_n = random.choice(data_pool["tbna_samples"])
        rul_cryo_n = random.choice(data_pool["cryo_samples"])
        
        # RLL Target Vars
        rll_target = random.choice(data_pool["rll_targets"])
        rll_rebus = random.choice(data_pool["rebus_features"])
        rll_size = random.choice(data_pool["nodule_size"])
        rll_dist = random.choice(data_pool["catheter_dist"])
        rll_bal = random.choice(data_pool["bal_volumes"])
        rll_tbna_n = random.choice(data_pool["tbna_samples"])
        rll_cryo_n = random.choice(data_pool["cryo_samples"])
        
        # LUL Target Vars
        lul_target = random.choice(data_pool["lul_targets"])
        lul_rebus = random.choice(data_pool["rebus_features"])
        lul_size = random.choice(data_pool["nodule_size"])
        lul_dist = random.choice(data_pool["catheter_dist"])
        lul_bal = random.choice(data_pool["bal_volumes"])
        lul_tbna_n = random.choice(data_pool["tbna_samples"])
        lul_cryo_n = random.choice(data_pool["cryo_samples"])
        
        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, gender_short=gender_tup[1], gender_long=gender_tup[0],
            attending=attending,
            rul_seg_id=rul_target[1], rul_seg_name=rul_target[0], rul_size=rul_size,
            rll_seg_id=rll_target[1], rll_seg_name=rll_target[0], rll_size=rll_size,
            lul_seg_id=lul_target[1], lul_seg_name=lul_target[0], lul_size=lul_size
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            age=age, gender_long=gender_tup[0], attending=attending,
            dx_code=dx[0], dx_name=dx[1],
            fiducial=fiducial,
            
            # Ventilation
            vent_mode=vent["mode"], vent_rr=vent["rr"], vent_tv=vent["tv"],
            vent_peep=vent["peep"], vent_fio2=vent["fio2"], vent_flow=vent["flow"],
            vent_pmean=vent["pmean"],
            
            # RUL
            rul_seg_name=rul_target[0], rul_seg_id=rul_target[1],
            rul_size=rul_size, rul_dist=rul_dist,
            rul_rebus_type=rul_rebus[0], rul_rebus_margin=rul_rebus[1],
            rul_tbna_n=rul_tbna_n, rul_cryo_n=rul_cryo_n,
            rul_bal_in=rul_bal[0], rul_bal_out=rul_bal[1],
            
            # RLL
            rll_seg_name=rll_target[0], rll_seg_id=rll_target[1],
            rll_size=rll_size, rll_dist=rll_dist,
            rll_rebus_type=rll_rebus[0], rll_rebus_margin=rll_rebus[1],
            rll_tbna_n=rll_tbna_n, rll_cryo_n=rll_cryo_n,
            rll_bal_in=rll_bal[0], rll_bal_out=rll_bal[1],
            
            # LUL
            lul_seg_name=lul_target[0], lul_seg_id=lul_target[1],
            lul_size=lul_size, lul_dist=lul_dist,
            lul_rebus_type=lul_rebus[0], lul_rebus_margin=lul_rebus[1],
            lul_tbna_n=lul_tbna_n, lul_cryo_n=lul_cryo_n,
            lul_bal_in=lul_bal[0], lul_bal_out=lul_bal[1]
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