import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_080"
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
    "age": ["55", "62", "67", "71", "74", "59", "64", "68", "79", "81"],
    "gender_tuple": [("female", "F", "her"), ("male", "M", "his")],
    "ref_physician": [
        "Dr. Sarah Miller", "Dr. James Chen", "Dr. Emily Bowers", 
        "Dr. Richard Smith", "Dr. A. Patel", "Dr. L. Wong"
    ],
    "attending": [
        "Dr. Michael Johnson", "Dr. Elena Rodriguez", "Dr. William Thou", 
        "Dr. K. Anderson"
    ],
    "assistant": [
        "Dr. Fellows", "Dr. Resident", "Dr. House", "Dr. Grey"
    ],
    # Target 1 (Primary Nodule) Variations - (Full Name, Lobe Short, Segment Code)
    "target_1_tuple": [
        ("Apical-Posterior Segment of the LUL (LB1/2)", "LUL", "LB1/2"),
        ("Anterior Segment of the LUL (LB3)", "LUL", "LB3"),
        ("Superior Segment of the LLL (LB6)", "LLL", "LB6"),
        ("Lingular Segment of the LUL (LB4)", "LUL", "LB4")
    ],
    "target_1_size": ["0.8", "0.9", "1.1", "1.2", "0.7", "1.5"],
    
    # Target 2 (Secondary Nodule) Variations - (Full Name, Lobe Short, Segment Code)
    "target_2_tuple": [
        ("Apical Segment of the RUL (RB1)", "RUL", "RB1"),
        ("Posterior Segment of the RUL (RB2)", "RUL", "RB2"),
        ("Superior Segment of the RLL (RB6)", "RLL", "RB6"),
        ("Lateral Basal Segment of the RLL (RB9)", "RLL", "RB9")
    ],
    "target_2_size": ["0.6", "0.5", "0.7", "0.4", "0.8"],

    # ROSE (Rapid On-Site Evaluation) Results
    "rose_1_result": [
        "No evidence of malignant neoplasm",
        "Atypical cells present, suspicious for malignancy",
        "Positive for Adenocarcinoma",
        "Lymphocytes and macrophages, negative for malignancy"
    ],
    "rose_2_result": [
        "Atypical cells present but no evidence of malignant neoplasm",
        "No evidence of malignancy",
        "Rare atypical cells seen",
        "Benign bronchial cells only"
    ],
    
    # EBUS Stations Inspected
    "ebus_stations": [
        "4R, 4L, 7, 11Rs, 11Ri, 11L",
        "4R, 4L, 7, 10R",
        "7, 4L, 11L, 11R",
        "2R, 4R, 7, 10R"
    ],
    
    "complications": ["None", "None immediate", "Minor bleeding controlled with cold saline", "None"],
    "date": ["01/15/2025", "02/10/2025", "03/05/2025", "11/20/2024", "12/12/2024"]
}

# ==========================================
# 3. TEMPLATES
# ==========================================

note_template = """NOTE_ID: {note_id} SOURCE_FILE: {note_id}.txt

INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: {date} CC Referred Physician: {ref_physician}

INDICATION FOR OPERATION The patient is a {age}-year-old {gender_long} who presents with lung nodules requiring bronchoscopic diagnosis.

The nature, purpose, risks, benefits, and alternatives to bronchoscopy were discussed with the patient in detail.

CONSENT Obtained before the procedure. Indications, potential complications, and alternatives were discussed with the patient or surrogate.

The patient wished to proceed and informed consent was obtained.

PREOPERATIVE DIAGNOSIS

R91.1 Solitary Lung Nodule 

POSTOPERATIVE DIAGNOSIS

R91.1 Solitary Lung Nodule 

{t1_lobe} and {t2_lobe} nodules sampled

EBUS inspection performed (no biopsies)

PROCEDURE

Robotic navigational bronchoscopy (Ion) to {t1_lobe} and {t2_lobe} targets 

Radial EBUS (rEBUS) localization ({t1_lobe}, {t2_lobe}) 

Cone-beam CT (Cios Spin) with 3D reconstruction and trajectory adjustment 

Transbronchial needle aspiration (TBNA) of {t1_lobe} and {t2_lobe} targets 

Transbronchial cryobiopsy of {t1_lobe} and {t2_lobe} targets 

Transbronchial brushing of {t1_lobe} and {t2_lobe} targets 

Fiducial marker placement ({t1_lobe}) 

Bronchoalveolar lavage (BAL) of targets and lobar lavage 

Therapeutic aspiration for airway clearance 

EBUS mediastinal lymph node inspection (without biopsy) 

ATTENDING {attending}

ASSISTANT {assistant}

SUPPORT STAFF RN: [Name] RT: [Name]

ANESTHESIA 

General Anesthesia 

MONITORING Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.

INSTRUMENTATION Linear EBUS; Radial EBUS; Ion Robotic Bronchoscope; Disposable Bronchoscope; Cios Spin System.

ESTIMATED BLOOD LOSS Minimum 

COMPLICATIONS {complications} 

PROCEDURE IN DETAIL After the successful induction of anesthesia, a timeout was performed confirming the patient's name, procedure type, and procedure location.

Initial Airway Inspection: Normal appearing airway anatomy and mucosa bilaterally to the segmental level.

Therapeutic Aspiration: Successful therapeutic aspiration was performed to clean out the Trachea, Mainstems, Bronchus Intermedius, Carina, and bilateral lobar carinas from mucus.

Robotic Navigational Bronchoscopy (Ion) -- {t1_lobe} Nodule A CT-based navigation plan was loaded into the robotic platform and partial registration was completed.

Navigation: The Ion robotic catheter was used to engage the {t1_full_loc}.

The target lesion measured approximately {t1_size} cm. The catheter was advanced to 1.0 cm from the target.

rEBUS Assessment: Radial EBUS confirmed an eccentric nodule location with continuous margins and absence of linear-discrete air bronchogram.

Cone-Beam CT: A Cios Spin low-dose CT spin was performed.

3D reconstructions on the Ion workstation were used to adjust the robotic system to the precise nodule location.

Sampling:

TBNA: 21G needle, 4 samples collected.

Cryobiopsy: 1.1mm cryoprobe, 6-second freeze time, 10 samples collected.

Brushing: Protected cytology brush, 1 sample collected.

BAL: 20 cc instilled, 5 cc return.

Fiducial: A fiducial marker with bone wax was placed under fluoroscopy guidance.

ROSE: {rose_1}.

Robotic Navigational Bronchoscopy (Ion) -- {t2_lobe} Nodule

Navigation: The Ion robotic catheter was used to engage the {t2_full_loc}.

The target lesion measured approximately {t2_size} cm.

rEBUS Assessment: Radial EBUS confirmed an eccentric nodule location with continuous margins and absence of linear-discrete air bronchogram.

Cone-Beam CT: Cios Spin CT imaging and 3D reconstruction were used to confirm and adjust nodule location.

Sampling:

TBNA: 21G needle, 4 samples collected.

Cryobiopsy: 1.1mm cryoprobe, 6-second freeze time, 6 samples collected.

Brushing: Protected cytology brush, 1 sample collected.

BAL: 20 cc instilled, 5 cc return.

ROSE: {rose_2}.

Additional Bronchoalveolar Lavage

{t1_lobe} Lobar Lavage: Performed at {t1_seg}, LB3, LB4, and LB5. Instilled 40 cc, returned 15 cc.

{t2_lobe} Lobar Lavage: Performed at {t2_seg}, RB2, and RB3. Instilled 40 cc, returned 15 cc.

EBUS Inspection A linear EBUS scope was used to assess lymph node stations.

Only nodes >=5 mm were considered for sampling.

Nodes Inspected: {ebus_stations}.

Elastography: EBUS elastography was performed to assess stiffness. Stations 11L, 4L, and 7 demonstrated Type 2 patterns (mixed soft/stiff).

Outcome: All assessed nodes (11L, 4L, 7) were <10 mm on CT.

Based on size and ultrasound appearance, biopsies were not clinically indicated and were not taken.

Conclusion The patient tolerated the procedure well with no immediate complications.

The patient was extubated in the operating room and transported to recovery in stable condition.

SPECIMENS

{t1_lobe} Target: TBNA, cryobiopsy, brush, BAL 

{t2_lobe} Target: TBNA, cryobiopsy, brush, BAL 

Lobar BALs: {t1_lobe} and {t2_lobe} 

Samples sent for Microbiology (Cultures/Viral/Fungal), Cytology, and Pathology.

IMPRESSION / PLAN

Successful robotic bronchoscopy and sampling of {t1_lobe} and {t2_lobe} nodules with Cone-Beam CT confirmation.

ROSE Results:

{t1_lobe} Nodule: {rose_1}.

{t2_lobe} Nodule: {rose_2}.

EBUS inspection performed;

no lymphadenopathy requiring biopsy identified.

Fiducial marker placed in {t1_lobe} target.

Follow-up bronchoscopic lab work and CXR.
"""

prompt_styles = [
    # Style 1: Telegraphic / Short
    "{age}yo {gender_short} with bilat nodules. Robot bronch Ion used for {t1_lobe} and {t2_lobe}. Fiducial in {t1_lobe}. ROSE {t1_lobe} {rose_1_short}, {t2_lobe} {rose_2_short}. EBUS done no bx.",
    
    # Style 2: Dictation
    "Please write an operative report for a {age} year old {gender_long} patient, Dr. {ref_physician} referring. We performed a robotic bronchoscopy targeting lesions in the {t1_lobe} and {t2_lobe}. We also did EBUS staging but found no nodes to biopsy.",
    
    # Style 3: Sloppy / Quick
    "post op dx R91.1. {age} {gender_short}. Ion robot case. {t1_lobe} ({t1_size}cm) and {t2_lobe} ({t2_size}cm) sampled. TBNA/Cryo/Brush. fiducial {t1_lobe}. attending {attending}.",
    
    # Style 4: Billing Focus
    "Procedure: Robotic Navigational Bronchoscopy (Ion) + rEBUS + Cone Beam CT. Targets: {t1_lobe}, {t2_lobe}. EBUS inspection included. Patient {age} {gender_short}. Complications: {complications}.",
    
    # Style 5: Structured
    "Patient: {age} {gender_short}\nRef MD: {ref_physician}\nProcedures: Ion Robot, rEBUS, CBCT, EBUS (inspection only)\nTargets:\n1. {t1_lobe} ({t1_size}cm) - ROSE: {rose_1_short}\n2. {t2_lobe} ({t2_size}cm) - ROSE: {rose_2_short}"
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
        ref_physician = random.choice(data_pool["ref_physician"])
        attending = random.choice(data_pool["attending"])
        assistant = random.choice(data_pool["assistant"])
        date = random.choice(data_pool["date"])
        complications = random.choice(data_pool["complications"])
        
        # Target 1
        t1_tup = random.choice(data_pool["target_1_tuple"])
        t1_size = random.choice(data_pool["target_1_size"])
        rose_1 = random.choice(data_pool["rose_1_result"])
        
        # Target 2
        t2_tup = random.choice(data_pool["target_2_tuple"])
        t2_size = random.choice(data_pool["target_2_size"])
        rose_2 = random.choice(data_pool["rose_2_result"])
        
        ebus_stations = random.choice(data_pool["ebus_stations"])

        # Helper for short ROSE summary in prompts
        rose_1_short = "Neg" if "No evidence" in rose_1 else "Suspicious" if "Atypical" in rose_1 else "Pos"
        rose_2_short = "Neg" if "No evidence" in rose_2 else "Suspicious" if "Atypical" in rose_2 else "Pos"

        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, gender_short=gender_tup[1], gender_long=gender_tup[0],
            ref_physician=ref_physician, attending=attending,
            t1_lobe=t1_tup[1], t1_size=t1_size, rose_1_short=rose_1_short,
            t2_lobe=t2_tup[1], t2_size=t2_size, rose_2_short=rose_2_short,
            complications=complications
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            date=date,
            ref_physician=ref_physician,
            age=age, gender_long=gender_tup[0],
            attending=attending, assistant=assistant,
            complications=complications,
            
            # Target 1 Details
            t1_full_loc=t1_tup[0], t1_lobe=t1_tup[1], t1_seg=t1_tup[2],
            t1_size=t1_size, rose_1=rose_1,
            
            # Target 2 Details
            t2_full_loc=t2_tup[0], t2_lobe=t2_tup[1], t2_seg=t2_tup[2],
            t2_size=t2_size, rose_2=rose_2,
            
            ebus_stations=ebus_stations
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