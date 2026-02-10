import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_058" 
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
    "age": ["62", "65", "71", "74", "79", "82", "88", "91"],
    "gender_tuple": [("female", "F"), ("male", "M")],
    "attending_name": ["Dr. Smith", "Dr. Patel", "Dr. Johnson", "Dr. Lee", "Dr. Rodriguez"],
    "fellow_name": ["Dr. Davis", "Dr. Kim", "Dr. Wright", "Dr. Gomez"],
    
    # Target Pairs to ensure anatomical consistency (Target 1, Target 1 Segment, Target 2, Target 2 Segment)
    "target_pairs": [
        ("Lingula", "Superior Segment of the Lingula (LB4)", "LUL Anterior", "Anterior Segment of LUL (LB3)"),
        ("RUL", "Apical Segment of RUL (RB1)", "RLL Superior", "Superior Segment of RLL (RB6)"),
        ("RML", "Medial Segment of RML (RB5)", "RUL Posterior", "Posterior Segment of RUL (RB2)"),
        ("LUL", "Apico-posterior Segment of LUL (LB1+2)", "LLL", "Lateral Basal Segment of LLL (LB9)"),
    ],
    
    "lesion_size": ["0.8 cm", "1.0 cm", "1.2 cm", "1.5 cm", "1.8 cm", "2.1 cm"],
    "rebus_signal": ["Eccentric", "Concentric"],
    "rose_result": ["malignant neoplasm", "suspicious for malignancy", "atypical cells present", "diagnostic for carcinoma"],
    
    # EBUS Station Logic
    "lymph_node_stations": [
        "4R, 4L, 7, 10R, 10L",
        "4R, 4L, 7, 11Rs, 11L",
        "4R, 4L, 7, 10R, 11Ri"
    ],
    
    # Specific Cryo outcome for Target 2 (sometimes it fails, sometimes it works)
    "t2_cryo_outcome_tuple": [
        ("Attempted but technically challenging; unable to penetrate airway wall for consistent biopsy.", "Cryobiopsy: Attempted"),
        ("1.1mm cryoprobe used; 3 samples collected successfully.", "Cryobiopsy (3 samples)")
    ]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
note_template = """NOTE_ID: {note_id}
SOURCE_FILE: {note_id}.txt

INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: [Date] CC Referred Physician: [Name / Self, Referred]

INDICATION FOR OPERATION {age}-year-old {gender_long} who presents with lung nodules requiring bronchoscopic diagnosis.
The nature, purpose, risks, benefits, and alternatives to Bronchoscopy were discussed with the patient in detail.
The patient wished to proceed and informed consent was signed.

CONSENT Obtained before the procedure.
Indications, potential complications, and alternatives were discussed with the patient or surrogate.
Consent was signed and witnessed by an assisting medical professional.

PREOPERATIVE DIAGNOSIS
R91.1 Solitary Lung Nodule 

POSTOPERATIVE DIAGNOSIS
R91.1 Solitary Lung Nodule 
{rose_result_cap} (ROSE confirmation for {t1_loc} and {t2_loc_short} nodules) 

PROCEDURE
Robotic navigational bronchoscopy (Ion) to {t1_loc} and {t2_loc_short} targets 
Radial EBUS (rEBUS) localization 
Cone-beam CT imaging (Cios Spin) with trajectory adjustment and confirmation 
TBNA of {t1_loc} and {t2_loc_short} targets 
Transbronchial cryobiopsy of {t1_loc} target 
Transbronchial biopsy (forceps) and brushing of {t1_loc} target 
Bronchoalveolar lavage (BAL) 
Fiducial marker placement ({t1_loc}) 
EBUS mediastinal/hilar lymph node survey (inspection only) 

ATTENDING {attending}
ASSISTANT {fellow}
SUPPORT STAFF RN: [Name] RT: [Name]

ANESTHESIA General Anesthesia 

MONITORING Pulse oximetry, heart rate, telemetry, and blood pressure were continuously monitored by an 
independent trained observer throughout the procedure.

INSTRUMENTATION Flexible Therapeutic Bronchoscope; Linear EBUS; Radial EBUS; Ion Robotic Bronchoscope; Cios Spin System.
ESTIMATED BLOOD LOSS None 

COMPLICATIONS None 

PROCEDURE IN DETAIL After successful induction of anesthesia, a timeout was performed confirming patient identity, planned procedures, and procedure location.
Patient position: [Supine]. Initial airway inspection: Successful therapeutic aspiration was performed to clean out the Right Mainstem, Bronchus Intermedius, and Left Mainstem from mucus.
A CT-based navigation plan was loaded into the robotic bronchoscopy platform.

Target 1: {t1_loc} Nodule Robotic navigation bronchoscopy was performed with the Ion platform using partial registration.
The Ion robotic catheter was used to engage the {t1_seg}.
Target: Lesion is approximately {size1} in diameter. Catheter advanced to 1.0 cm from target under navigational guidance.
rEBUS: Radial EBUS confirmed an {rebus1} signal. Features noted: Continuous margin and absence of linear-discrete air bronchogram.
Cone-beam CT (Cios Spin): A low-dose spin was performed. 3D reconstructions on an independent workstation were interpreted by the attending.
Adjustment: The system was updated with the acquired nodule location and the robotic catheter was adjusted to the new target.

Sampling:
TBNA: 21G needle; 4 samples collected.
Transbronchial Biopsy: Alligator forceps; 1 sample collected.
Cryobiopsy: 1.1mm cryoprobe, 6-second freeze time; 6 samples collected.
Brushing: Protected cytology brush; 1 sample collected.
BAL: 20 cc NS instilled, 10 cc returned.
Fiducial: One 0.8mm x 3mm soft tissue gold marker was placed under fluoroscopy guidance.

ROSE: Conclusive evidence of {rose_result}.
No bleeding was noted prior to withdrawal.

Target 2: {t2_loc_short} Nodule Robotic navigation was performed to the {t2_seg}.
Target: Lesion is approximately {size2} in diameter. Catheter advanced to 1.0 cm from target.
rEBUS: Radial EBUS confirmed an {rebus2} signal. Features noted: Continuous margin and absence of linear-discrete air bronchogram.
Cone-beam CT (Cios Spin): Spin performed, 3D images interpreted, and catheter position adjusted/confirmed.

Sampling:
TBNA: 21G needle; 6 samples collected.
Cryobiopsy: {t2_cryo_text}
BAL: 60 cc NS instilled, 15 cc returned.

ROSE: Conclusive evidence of {rose_result}.
Hemostasis: 200mg of Tranexamic Acid (TXA) was placed in the {t2_loc_short} to achieve hemostasis. No evidence of bleeding upon inspection.

EBUS STAGING The EBUS bronchoscope was introduced. All lymph node stations were assessed.
Technique: Only nodes ≥5 mm in short axis were considered for sampling.
EBUS elastography was performed to assess tissue stiffness (Type 1-3).

Stations Inspected: {stations}.
Site 1 - Station 4L: <10 mm on CT, Non-Hypermetabolic on PET. Elastography Type 1 (soft/benign).
Not sampled (not clinically indicated).

Site 2 - Station 7: <10 mm on CT, Non-Hypermetabolic on PET.
Elastography Type 1 (soft/benign). Not sampled (not clinically indicated).

Other Stations: No detectable lymph nodes noted in other stations.
No immediate complications. The patient was extubated in the operating room and transported to recovery in stable condition.

SPECIMENS
{t1_loc} nodule: TBNA (4 samples), TBBX (1 sample), Cryobiopsy (6 samples), Brush (1 sample) — Pathology/Cytology.
{t1_loc} nodule: BAL — Microbiology.
{t2_loc_short} nodule: TBNA (6 samples) — Cytology.
{t2_loc_short} nodule: BAL — Cell Count, Microbiology, Cytology.

IMPRESSION / PLAN
{age}-year-old {gender_long} with bilateral lung nodules successfully sampled via Robotic Bronchoscopy.

{t1_loc} Nodule: ROSE conclusive for {rose_result}.
Fiducial marker placed.

{t2_loc_short} Nodule: ROSE conclusive for {rose_result}.

EBUS Staging: Complete inspection performed;
no nodes met criteria for sampling (benign elastography/size/PET features).

Follow-up in clinic for final pathology results.
"""

prompt_styles = [
    # Style 1: Telegraphic
    "Gen Anesth Robotic Bronch. Pt {age} {gender_short}. Targets: {t1_loc}, {t2_loc_short}. rEBUS {rebus1}/{rebus2}. ROSE: {rose_result}. Fiducial in {t1_loc}. EBUS staging neg.",
    
    # Style 2: Dictation
    "Record a robotic bronchoscopy note for Dr. {attending}. Patient is {age}yo {gender_long}. We targeted the {t1_loc} and {t2_loc_short} using Ion and Cios Spin. Both nodules showed {rose_result} on ROSE. EBUS was performed, no nodes sampled.",
    
    # Style 3: Sloppy / Quick
    "{age} {gender_short} bilat nodules {t1_loc} {t2_loc_short}. ion/rebus/cios used. {rose_result}. fiducial placed t1. ebus staging clear. no comps.",
    
    # Style 4: Billing Focus
    "Procedures: Robotic Nav Bronch (Ion), Radial EBUS, Cone Beam CT, Fiducial Placement. Dx: R91.1. Pt: {age} {gender_short}. Targets: {t1_loc} ({size1}), {t2_loc_short} ({size2}). Path: {rose_result}.",
    
    # Style 5: Structured
    "Patient: {age} {gender_short}\nProcedure: Ion Robotic Bronchoscopy + EBUS\nTargets: {t1_loc}, {t2_loc_short}\nFindings: {rose_result} (ROSE)\nIntervention: Fiducial placed in {t1_loc}. EBUS staging negative."
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
        attending = random.choice(data_pool["attending_name"])
        fellow = random.choice(data_pool["fellow_name"])
        
        # Target Logic
        target_pair = random.choice(data_pool["target_pairs"])
        t1_loc = target_pair[0]
        t1_seg = target_pair[1]
        t2_loc_short = target_pair[2].split()[0] # e.g., "LUL" from "LUL Anterior" for brevity in some spots
        t2_loc_full = target_pair[2]
        t2_seg = target_pair[3]
        
        size1 = random.choice(data_pool["lesion_size"])
        size2 = random.choice(data_pool["lesion_size"])
        rebus1 = random.choice(data_pool["rebus_signal"])
        rebus2 = random.choice(data_pool["rebus_signal"])
        rose = random.choice(data_pool["rose_result"])
        
        stations = random.choice(data_pool["lymph_node_stations"])
        
        # T2 Cryo variation
        cryo_tup = random.choice(data_pool["t2_cryo_outcome_tuple"])
        t2_cryo_text = cryo_tup[0]
        
        # B. Generate Prompt
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, gender_short=gender_tup[1], gender_long=gender_tup[0],
            attending=attending,
            t1_loc=t1_loc, t2_loc_short=t2_loc_short,
            rebus1=rebus1, rebus2=rebus2,
            rose_result=rose,
            size1=size1, size2=size2
        )
        
        # C. Generate Completion
        completion = note_template.format(
            note_id=NOTE_ID,
            age=age, gender_long=gender_tup[0],
            attending=attending, fellow=fellow,
            t1_loc=t1_loc, t1_seg=t1_seg,
            t2_loc_short=t2_loc_full, t2_seg=t2_seg, # Using full name for template text
            size1=size1, size2=size2,
            rebus1=rebus1, rebus2=rebus2,
            rose_result=rose,
            rose_result_cap=rose.capitalize(),
            t2_cryo_text=t2_cryo_text,
            stations=stations
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