import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_078"
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
    "age": ["32", "45", "52", "58", "64", "69", "73", "77", "81"],
    "gender_tuple": [("female", "F", "She", "her"), ("male", "M", "He", "his")],
    "physician_last": ["Bowers", "Chen", "Smith", "Miller", "Jones", "Doe", "Patel", "Weiss"],
    "attending_last": ["Ingraham", "Alvarez", "Gupta", "Rossi", "Thompson"],
    
    # Anatomical Targets (Lobe, Segment Name, Segment Code)
    "target_anatomy": [
        ("LLL", "Anteromedial Segment", "Lb7/8"),
        ("LLL", "Superior Segment", "LB6"),
        ("LLL", "Posterior Basal Segment", "LB10"),
        ("RLL", "Superior Segment", "RB6"),
        ("RLL", "Posterior Basal Segment", "RB10"),
        ("RUL", "Apical Segment", "RB1"),
        ("RUL", "Posterior Segment", "RB2"),
        ("LUL", "Apicoposterior Segment", "LB1+2"),
        ("LUL", "Anterior Segment", "LB3"),
    ],
    
    "nodule_size": ["1.2", "1.5", "2.0", "2.5", "3.1", "3.8", "0.9"],
    
    # ROSE Findings (Rapid On-Site Evaluation)
    "rose_finding": [
        "Fungus", 
        "Adenocarcinoma", 
        "Squamous Cell Carcinoma", 
        "Granulomatous Inflammation", 
        "Atypical cells present", 
        "Necrotic debris",
        "Non-small cell lung carcinoma"
    ],
    
    "diagnosis_code": ["R91.1", "R91.8", "C34.90", "D38.1"],
    
    # EBUS Station specifics (keeping strictly to those usually staged)
    "elastography": ["Type 1 (soft)", "Type 2 (mixed soft/stiff)", "Type 3 (stiff)"],
}

# ==========================================
# 3. TEMPLATES
# ==========================================

note_template = """INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT
DATE OF PROCEDURE: [Date] CC Referred Physician: {ref_physician}

INDICATION FOR OPERATION
The patient is a {age}-year-old {gender_long} who presents with a lung nodule.
The nature, purpose, risks, benefits, and alternatives to Bronchoscopy were discussed with the patient in detail.

CONSENT
Obtained before the procedure.
Indications, potential complications, and alternatives were discussed with the patient or surrogate.
The patient wished to proceed and informed consent was obtained.

PREOPERATIVE DIAGNOSIS
{dx_code} Solitary Lung Nodule 

POSTOPERATIVE DIAGNOSIS
{dx_code} Solitary Lung Nodule 

ROSE from Ion procedure noted {rose_result} 

PROCEDURE
Robotic navigational bronchoscopy (Ion) 
Therapeutic aspiration (initial and subsequent) 
Radial EBUS (rEBUS) lesion verification 
Cone-beam CT (Cios Spin) with 3D reconstruction 
Transbronchial needle aspiration (TBNA) of {lobe} target 
Transbronchial cryobiopsy of {lobe} target 
Transbronchial brushing 
Bronchoalveolar lavage (BAL) 
Fiducial marker placement 
Endobronchial Ultrasound (EBUS) of mediastinal/hilar lymph nodes (staging) without biopsy 

ATTENDING
{attending}

ANESTHESIA
General Anesthesia 

MONITORING
Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer present throughout the entire procedure.

INSTRUMENTATION
Linear EBUS, Radial EBUS, Ion Robotic Bronchoscope, Disposable Bronchoscope.

ESTIMATED BLOOD LOSS
Minimum 

COMPLICATIONS
None 

PROCEDURE IN DETAIL
After the successful induction of anesthesia, a timeout was performed confirming the patient's name, procedure type, and procedure location.
Initial Airway Inspection: Normal appearing airway anatomy and mucosa bilaterally to the segmental level.
Successful therapeutic aspiration was performed to clean out the Trachea, Right Mainstem, Bronchus Intermedius, Left Mainstem, Carina, and bilateral lobar carinas from mucus.

Robotic Navigational Bronchoscopy (Ion) — {lobe} Nodule: A CT chest scan was utilized on a separate planning station to generate a 3D rendering of the pathway to the target.
The navigational plan was reviewed, verified, and loaded into the robotic platform.
Robotic navigation was performed with the Ion platform using partial registration.

Target: The Ion robotic catheter was used to engage the {segment_name} of the {lobe} ({segment_code}).
The target lesion was approximately {size} cm in diameter.

Navigation: Under navigational guidance, the catheter was advanced to 1.0 cm away from the planned target.
rEBUS Verification: Radial EBUS was performed, confirming the nodule location was eccentric.
Features noted included a continuous margin and absence of a linear-discrete air bronchogram.

Cone-Beam CT (Cios Spin): A low-dose spin was performed to acquire CT imaging.
3D reconstructions were performed and interpreted on an independent workstation.
Adjustment: Using the newly acquired nodule location from the Cios Spin system, the Ion robotic system was adjusted to the new targeted location.

{lobe} Target Sampling:
TBNA: Transbronchial needle aspiration was performed with a 21G needle through the extended working channel.
Total 4 samples were collected and sent for Microbiology and Cytology.

Cryobiopsy: Transbronchial cryobiopsy was performed with a 1.1mm cryoprobe (freeze time 6 seconds).
Total 8 samples were collected and sent for Microbiology and Pathology.
This required substantially greater work (>40%) due to increased intensity and technical difficulty.

Fiducial: A fiducial marker loaded with bone wax was placed under fluoroscopy guidance prior to withdrawal.

Brushing: Transbronchial brushing was performed with a protected cytology brush. 1 sample was collected for Cytology.

Lavage (BAL): Bronchial alveolar lavage was performed at the target site (20 cc instilled, 5 cc returned) and sent for Microbiology.
Additional lavage was performed at the subsegments of the {lobe} (40 cc instilled, 15 cc returned) and sent for Cell Count, Microbiology, and Cytology.

ROSE: Rapid On-Site Evaluation (ROSE) from the Ion procedure noted: {rose_result}.

EBUS Staging: The linear EBUS scope was introduced.
All lymph node stations were assessed; only those 5 mm or greater in short axis were considered for sampling.
Endobronchial ultrasound elastography was used to assess stiffness (Type 1–3) to guide selection.

Station 11L: < 10 mm on CT. Demonstrated {elastography} elastographic pattern. Not sampled.
Station 4L (Lower Paratracheal): < 10 mm on CT. {elastography} pattern. Not sampled.
Station 7 (Subcarinal): < 10 mm on CT. {elastography} pattern. Not sampled.
Station 4R (Lower Paratracheal): < 10 mm on CT. {elastography} pattern. Not sampled.
Station 11Ri: < 10 mm on CT. {elastography} pattern. Not sampled.

No biopsies were taken based upon ultrasound appearance.

Conclusion: Therapeutic aspiration was repeated to clean the airways of mucus and blood.
The patient tolerated the procedure well with no immediate complications.
The patient was extubated in the operating room and transported to recovery in stable condition.

SPECIMENS
{lobe} transbronchial needle aspiration (4 samples) — Microbiology, Cytology 
{lobe} transbronchial cryobiopsies (8 samples) — Microbiology, Pathology 
{lobe} transbronchial brush (1 sample) — Cytology 
{lobe} subsegmental bronchoalveolar lavage — Microbiology 
{lobe} lobar bronchoalveolar lavage — Cell Count, Microbiology, Cytology 

IMPRESSION / PLAN
{age}-year-old {gender_long} with lung nodule.
Nodule successfully sampled via Ion robotic bronchoscopy; ROSE noted {rose_result}.
Fiducial marker placed.
EBUS staging performed; no lymph nodes required sampling.

Plan:
Follow up bronchoscopic lab work.
Follow up CXR.
"""

# <--- CREATE 5 DISTINCT PROMPT STYLES HERE --->
prompt_styles = [
    # Style 1: Telegraphic
    "Operative note: Ion bronch. {age}yo {gender_short}. Target {lobe} {segment_name} ({size}cm). ROSE showed {rose_result}. EBUS staging neg. Attending {attending}.",
    
    # Style 2: Dictation
    "Please generate a procedure note for Dr. {attending}. Patient is {age} {gender_long} with a {size} cm {lobe} nodule. We used Ion, rEBUS, and Cone Beam CT. ROSE was {rose_result}. No EBUS nodes sampled.",
    
    # Style 3: Sloppy / Quick
    "{age}F {lobe} nodule {size}cm. robotic bronch + ebus. rose: {rose_result}. ref by {ref_physician}. fiducial placed.",
    
    # Style 4: Billing Focus
    "Code for Ion Bronchoscopy + EBUS + Fiducial. Dx {dx_code}. Patient {age} {gender_short}. Site: {lobe} {segment_code}. Findings: {rose_result}.",
    
    # Style 5: Structured
    "Patient Age: {age}\nGender: {gender_long}\nProcedure: Robotic Bronchoscopy (Ion)\nTarget: {lobe} {segment_name}, {size} cm\nROSE: {rose_result}\nComplications: None"
]

# ==========================================
# 4. GENERATOR LOGIC
# ==========================================
def generate_dataset():
    dataset = []
    
    for _ in range(NUM_SAMPLES):
        # A. Randomly select variables
        age = random.choice(data_pool["age"])
        gender_tup = random.choice(data_pool["gender_tuple"]) # (long, short, He/She, his/her)
        ref_physician = "Dr. " + random.choice(data_pool["physician_last"])
        attending = "Dr. " + random.choice(data_pool["attending_last"])
        
        # Anatomy logic (keeps Lobe and Segment synced)
        anatomy = random.choice(data_pool["target_anatomy"])
        lobe = anatomy[0]
        seg_name = anatomy[1]
        seg_code = anatomy[2]
        
        size = random.choice(data_pool["nodule_size"])
        rose = random.choice(data_pool["rose_finding"])
        dx_code = random.choice(data_pool["diagnosis_code"])
        elasto = random.choice(data_pool["elastography"])
        
        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_tup[1], 
            gender_long=gender_tup[0],
            attending=attending,
            ref_physician=ref_physician,
            lobe=lobe,
            segment_name=seg_name,
            segment_code=seg_code,
            size=size,
            rose_result=rose,
            dx_code=dx_code
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            age=age, 
            gender_long=gender_tup[0],
            ref_physician=ref_physician,
            attending=attending,
            dx_code=dx_code,
            rose_result=rose,
            lobe=lobe,
            segment_name=seg_name,
            segment_code=seg_code,
            size=size,
            elastography=elasto
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