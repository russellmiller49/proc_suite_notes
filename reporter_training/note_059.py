import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_059"
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
    "age": ["42", "49", "55", "58", "61", "67", "72", "75", "81"],
    "gender_tuple": [("female", "F", "she"), ("male", "M", "he")],
    
    # Target Location Logic: (Lobe, Segment Name, Segment ID)
    "target_location": [
        ("RLL", "Posterior-basal Segment", "RB10"),
        ("RLL", "Lateral-basal Segment", "RB9"),
        ("RML", "Lateral Segment", "RB4"),
        ("RUL", "Apical Segment", "RB1"),
        ("RUL", "Posterior Segment", "RB2"),
        ("LUL", "Apical-posterior Segment", "LB1+2"),
        ("LUL", "Anterior Segment", "LB3"),
        ("LLL", "Superior Segment", "LB6"),
        ("LLL", "Posterior-basal Segment", "LB10")
    ],
    
    # Nodule Characteristics
    "nodule_size": ["0.8", "1.2", "1.5", "1.9", "2.1", "2.5", "3.0"],
    "radial_ebus_signal": ["Concentric", "Eccentric"],
    
    # ROSE (Rapid On-Site Evaluation) Results
    "rose_result": [
        "Cells present causing suspicion of malignant neoplasm",
        "Atypical cells present, suspicious for non-small cell carcinoma",
        "Malignant cells present consistent with adenocarcinoma",
        "Lymphocytes and macrophages, negative for malignancy",
        "Granulomatous inflammation, no malignant cells seen"
    ],
    
    # EBUS Node findings (Elastography patterns)
    "elastography_benign": [
        "Type 1 pattern (predominantly soft/green/yellow), suggesting a reactive or benign process",
        "Type 1 pattern, homogeneous soft tissue signal"
    ],
    "elastography_indeterminate": [
        "Type 2 pattern (mixed soft and stiff regions), heterogeneous and indeterminate",
        "Type 2 pattern, mixed echogenicity"
    ],
    "elastography_malignant": [
        "Type 3 pattern (predominantly stiff/blue), suspicious for metastatic involvement",
        "Type 3 pattern, stiff consistency consistent with infiltration"
    ],
    
    "bal_return": [("50", "10"), ("60", "15"), ("100", "40"), ("60", "20"), ("50", "25")],
    
    "complication": [
        "None",
        "None",
        "None", # Weighting towards None as per typical reports
        "Minor airway bleeding controlled with cold saline and suction",
        "Transient desaturation to 88% resolved with increased FiO2"
    ]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
note_template = """INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT
INDICATION FOR OPERATION The patient is a {age}-year-old {gender_long} who presents with a lung nodule.
The nature, purpose, risks, benefits, and alternatives to bronchoscopy were discussed with the patient in detail.
The patient indicated a wish to proceed with surgery and informed consent was signed.
PREOPERATIVE DIAGNOSIS

R91.1 Solitary Lung Nodule 

POSTOPERATIVE DIAGNOSIS

R91.1 Solitary Lung Nodule 

ROSE status: {rose_result} 

PROCEDURE

Therapeutic aspiration, initial episode 

Diagnostic bronchoscopy with brushing and lavage (BAL) 

Transbronchial biopsy (TBBX), single lobe 

Transbronchial needle aspiration (TBNA), single lobe 

Fiducial marker placement 

Navigational Bronchoscopy (computer assisted) 

Radiologic guidance for CT guided needle placement (CIOS) 

3D rendering with interpretation and reporting (ION Planning Station) 

EBUS sampling (3 or more nodes) 

Radial EBUS for peripheral lesion 

Ultrasound Elastography 

ANESTHESIA General Anesthesia 

MONITORING Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present 
throughout the entire procedure.

INSTRUMENTATION Flexible Therapeutic Bronchoscope, Linear EBUS, Radial EBUS, Ion Robotic Bronchoscope, Disposable Bronchoscope.
ESTIMATED BLOOD LOSS None 

COMPLICATIONS {complication} 

PROCEDURE IN DETAIL
After the successful induction of anesthesia, a timeout was performed confirming the patient's name, procedure type, and procedure location.
Initial Airway Inspection & Therapeutic Aspiration Successful therapeutic aspiration was performed to clean out the Right Mainstem, Bronchus Intermedius, and Left Mainstem from mucus.
Robotic Navigational Bronchoscopy (Ion) — {target_lobe} Nodule A CT chest scan was placed on a separate planning station to generate a 3D rendering of the pathway to the target.
The navigational plan was reviewed, verified, and loaded into the robotic bronchoscopy platform.
Robotic navigation was performed with the Ion platform using partial registration.
Targeting: The Ion robotic catheter was used to engage the {target_seg_name} of the {target_lobe} ({target_seg_id}).
The target lesion is about {nodule_size} cm in diameter. Under navigational guidance, the catheter was advanced to 1.0 cm away from the planned target.
Radial EBUS: Performed to confirm location; the nodule signal was {r_ebus_signal} with a continuous margin.
Cone Beam CT (Cios Spin): A low-dose spin was performed to acquire CT imaging for evaluation of nodule location.
The 3D images were reconstructed and interpreted on an independent workstation.
Adjustment: Using the newly acquired nodule location, the Ion robotic system was adjusted to the new targeted location.
I personally interpreted the cone beam CT and 3-D reconstruction.
{target_lobe} Target Sampling

TBNA: Performed with a 21G needle through the extended working channel.
Total 6 samples were collected and sent for Cytology.

Transbronchial Biopsy: Performed with alligator forceps.
Total 1 sample was collected and sent for Pathology.

Cryobiopsy: Performed with a 1.1mm cryoprobe (freeze time 6 seconds).
Total 6 samples were collected and sent for Pathology.

Brushing: Performed with a protected cytology brush.
Total 1 sample was collected and sent for Microbiology.

BAL: Instilled {bal_in} cc of NS, suction returned with {bal_out} cc of NS.
Samples sent for Microbiology.


Fiducial Marker: A 0.8mm x 3mm soft tissue gold CIVCO marker was loaded with bone wax and placed under fluoroscopy guidance.
ROSE Results: {rose_result}.

Inspection prior to withdrawal demonstrated no evidence of bleeding.
EBUS STAGING
Technique All lymph node stations were assessed. Only those 5 mm or greater in short axis were sampled.
Lymph node sizing was performed by EBUS and sampling was performed using 25-gauge and 22-gauge needles.
Endobronchial ultrasound (EBUS) elastography was performed to assess lymph node stiffness and tissue characteristics.
Lymph Nodes Evaluated & Sampled

Station 11L (< 10 mm):


Elastography: {elasto_11L}.
Sampling: TBNA directed at representative areas. 4 samples obtained.

Station 7 (Subcarinal, < 10 mm):


Elastography: {elasto_7}.
Sampling: TBNA performed to confirm absence of malignancy. 4 samples obtained.
Station 11Rs (< 10 mm):


Elastography: {elasto_11Rs}.
Sampling: TBNA directed at representative areas. 4 samples obtained.

Other sites inspected included 4R, 4L, 10R, 10L, and 11Ri.
DISPOSITION The patient tolerated the procedure well with {complication_lower}.
At the conclusion of the operation, the patient was extubated in the operating room and transported to the recovery room in stable condition.
SPECIMENS

{target_lobe} TBCBX, TBNA, Brush, BAL 

TBNA: Stations 11Rs, 11L, 7 

IMPRESSION/PLAN

{age}-year-old {gender_long} who presents for bronchoscopy for lung nodule.
Follow-up in clinic.

Follow-up CXR.
"""

prompt_styles = [
    # Style 1: Telegraphic
    "Operative note for {age}yo {gender_short}. Ion bronch of {target_lobe} nodule ({target_seg_id}). Size {nodule_size}cm. ROSE: {rose_short}. EBUS staging 11L, 7, 11Rs. Complications: {complication}.",
    
    # Style 2: Dictation
    "Please generate a procedure note for a {age} year old {gender_long} undergoing robotic bronchoscopy. Target was a {nodule_size} cm lesion in the {target_lobe}, {target_seg_name}. We used Cone Beam CT and Radial EBUS. ROSE showed {rose_short}. We also did EBUS staging.",
    
    # Style 3: Sloppy / Quick
    "Robotic bronch note. Pt {age} {gender_short}. {target_lobe} mass found. RB-EBUS {r_ebus_signal}. Biopsies taken, ROSE {rose_short}. Fiducials placed. EBUS performed on 11L/7/11Rs.",
    
    # Style 4: Billing Focus
    "Procedure: Navigational Bronchoscopy, EBUS, Fiducial Placement. Patient: {age} {gender_short}. Site: {target_lobe} ({target_seg_id}). ROSE: {rose_short}. No complications.",
    
    # Style 5: Structured
    "Patient: {age} {gender_short}\nProcedure: Ion Robotic Bronchoscopy + EBUS\nTarget: {target_lobe} ({target_seg_id}), {nodule_size}cm\nRadial EBUS: {r_ebus_signal}\nROSE: {rose_short}\nComplications: {complication}"
]

# ==========================================
# 4. GENERATOR LOGIC
# ==========================================
def generate_dataset():
    dataset = []
    
    for _ in range(NUM_SAMPLES):
        # A. Randomly select variables
        age = random.choice(data_pool["age"])
        gender_tup = random.choice(data_pool["gender_tuple"]) # (long, short, pronoun)
        gender_long = gender_tup[0]
        gender_short = gender_tup[1]
        
        # Target details
        target_loc = random.choice(data_pool["target_location"])
        target_lobe = target_loc[0]
        target_seg_name = target_loc[1]
        target_seg_id = target_loc[2]
        
        nodule_size = random.choice(data_pool["nodule_size"])
        r_ebus_signal = random.choice(data_pool["radial_ebus_signal"])
        
        # Findings
        rose_result = random.choice(data_pool["rose_result"])
        rose_short = "Malignant" if "malignant" in rose_result.lower() and "no" not in rose_result.lower() else "Benign/Indeterminate"
        
        # EBUS Findings (Randomize elastography for stations to create variety)
        elasto_options = (
            data_pool["elastography_benign"] + 
            data_pool["elastography_indeterminate"] + 
            data_pool["elastography_malignant"]
        )
        elasto_11L = random.choice(elasto_options)
        elasto_7 = random.choice(data_pool["elastography_benign"]) # Usually keep subcarinal benign for variety unless specified otherwise, but keeping it random-ish from benigh list
        elasto_11Rs = random.choice(elasto_options)
        
        # Fluids
        bal_vals = random.choice(data_pool["bal_return"])
        bal_in = bal_vals[0]
        bal_out = bal_vals[1]
        
        complication = random.choice(data_pool["complication"])
        complication_lower = "no immediate complications" if complication == "None" else complication.lower()

        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_long=gender_long, 
            gender_short=gender_short,
            target_lobe=target_lobe,
            target_seg_name=target_seg_name,
            target_seg_id=target_seg_id,
            nodule_size=nodule_size,
            rose_short=rose_short,
            r_ebus_signal=r_ebus_signal,
            complication=complication
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            age=age,
            gender_long=gender_long,
            target_lobe=target_lobe,
            target_seg_name=target_seg_name,
            target_seg_id=target_seg_id,
            nodule_size=nodule_size,
            r_ebus_signal=r_ebus_signal,
            bal_in=bal_in,
            bal_out=bal_out,
            rose_result=rose_result,
            elasto_11L=elasto_11L,
            elasto_7=elasto_7,
            elasto_11Rs=elasto_11Rs,
            complication=complication,
            complication_lower=complication_lower
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