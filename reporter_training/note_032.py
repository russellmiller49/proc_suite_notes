import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_032"
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
# We use a "scenario" approach here because the anatomy must be consistent 
# (e.g., if the mass is in the Right Upper Lobe, the navigation plan must match).
data_pool = {
    "age": ["62", "65", "68", "71", "73", "75", "79", "82", "84"],
    "gender_tuple": [("female", "F", "She"), ("male", "M", "He")],
    "referring_doctor": ["Dr. Smith", "Dr. Chen", "Dr. Al-Fayed", "Dr. Rossi", "Dr. Bowers"],
    "attending_doctor": ["Dr. Ingraham", "Dr. Miller", "Dr. Jones", "Dr. Harken"],
    
    # Anatomical Scenarios to ensure consistency between Procedure Heading, History, and Body
    "anatomy_scenarios": [
        {
            "mass_loc": "LUL", "mass_seg": "Apical-Posterior Segment LB1/LB2", "mass_size": "7.4 cm",
            "nodule_loc": "RML", "nodule_seg": "Lateral Segment RB4", "nodule_size": "2.3 cm",
            "tumor_loc": "LLL", "tumor_segs": "LB7/8 and LB6", "tumor_open_segs": "LB9-10",
            "clot_loc_1": "Right", "clot_loc_2": "Left"
        },
        {
            "mass_loc": "RUL", "mass_seg": "Apical Segment RB1", "mass_size": "6.2 cm",
            "nodule_loc": "LUL", "nodule_seg": "Lingula LB4", "nodule_size": "1.8 cm",
            "tumor_loc": "RLL", "tumor_segs": "RB6 and RB10", "tumor_open_segs": "RB7-9",
            "clot_loc_1": "Left", "clot_loc_2": "Right"
        },
        {
            "mass_loc": "RLL", "mass_seg": "Superior Segment RB6", "mass_size": "5.5 cm",
            "nodule_loc": "LUL", "nodule_seg": "Anterior Segment LB3", "nodule_size": "2.1 cm",
            "tumor_loc": "RML", "tumor_segs": "RB4 and RB5", "tumor_open_segs": "RB6",
            "clot_loc_1": "Left", "clot_loc_2": "Right"
        }
    ],
    
    "bleeding_mgmt": [
        "suction, cold saline, epinephrine 0.2mg, and APC",
        "suction, iced saline, and topical epinephrine",
        "continuous suction and wedging of the scope",
        "application of cold saline and oxidized cellulose"
    ],
    
    "ebus_stations": [
        "Stations 11Ri, 11Rs, 4R, 7",
        "Stations 7, 4R, 4L, 11L",
        "Stations 2R, 4R, 7, 10R",
        "Stations 11L, 4L, 7"
    ]
}

# ==========================================
# 3. TEMPLATES
# ==========================================

note_template = """NOTE_ID: {note_id}
DATE OF PROCEDURE: [Date] CC Referred Physician: {referring_doctor}

INDICATION FOR OPERATION
{patient_age}-year-old {gender_long} who presents with lung mass, multiple lung nodules, mediastinal/hilar lymphadenopathy, and {tumor_loc} lobar atelectasis.

PREOPERATIVE DIAGNOSIS
R91.8 Other nonspecific abnormal finding of lung field

POSTOPERATIVE DIAGNOSIS
R91.8 Other nonspecific abnormal finding of lung field

PROCEDURE
Navigational Bronchoscopy (computer assisted) with Ion Robotic Bronchoscope ({mass_loc} and {nodule_loc})
Radiology guidance for CT guided needle placement (Cios Spin)
3D rendering with interpretation and reporting (Ion Planning Station)
Radial EBUS for peripheral lesion
Fiducial marker placement
Transbronchial needle aspiration (TBNA) of {mass_loc} and {nodule_loc} targets
Transbronchial cryobiopsy (TBBX) of {mass_loc} and {nodule_loc} targets
Transbronchial brushing and Mini-BAL
Bronchoalveolar lavage (BAL) of {mass_loc}, {nodule_loc}, and {tumor_loc}
Therapeutic aspiration (initial episode) for clot/mucus clearance
EBUS sampling 3 or more nodes ({ebus_stations})
Ultrasound Elastography (First and Additional Targets)
Destruction of tumor (Cryotherapy and APC) at {tumor_loc}
31899 Unlisted Procedure (Trach Change with Mature Tract or Procedure NOS)

MODIFIER 22 (INCREASED PROCEDURAL SERVICES)
This patient required Transbronchial Cryo biopsies at two different locations, Robotic Navigation to two different sites ({mass_loc} and {nodule_loc}), CT-guided needle placement at two locations, multiple Bronchoalveolar lavages in three different locations, Brushings at multiple locations, and Radial EBUS performed at multiple locations. The patient required endobronchial biopsies at two discrete locations and endobronchial destruction of tumor by method other than excision at two discrete locations. The patient required ultrasound elastography evaluation of discrete lymph node sites, with the images/interpretation used for intraprocedural decision-making. This resulted in >100% increased work due to increased intensity, time, technical difficulty, severity of patient's condition, and physical/mental effort required.

ATTENDING: {attending_doctor}

ANESTHESIA: General Anesthesia
MONITORING: Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.
INSTRUMENTATION: Flexible Therapeutic Bronchoscope; Linear EBUS; Radial EBUS; Ion Robotic Bronchoscope.
ESTIMATED BLOOD LOSS: Moderate
COMPLICATIONS: None

PROCEDURE IN DETAIL
A timeout was performed confirming the patient's name, procedure type, and procedure location. After the successful induction of anesthesia, anesthesia placed an ETT.
Ventilation Parameters: Mode: VCV; RR: 14; TV: 450; PEEP: 12; FiO2: 70%; Flow Rate: 10; Pmean: 17.

Initial Airway Inspection
The Flexible Therapeutic Bronchoscope was advanced. Endobronchial topical lidocaine was applied to the main carina, right carina 1, and left carina 2.

Trachea: Distal 1/3 normal with thin bloody secretions.
{clot_loc_1} Lung: Bloody secretions and scattered mild blood clot burden within the airways. Normal anatomic branching to first subsegmental level. No endobronchial tumor or active bleeding source identified.
{clot_loc_2} Lung: Moderate blood secretions and large clot burden, including complete obstruction of {tumor_loc} bronchus due to clot.

Following therapeutic aspiration, endobronchial tumor was noted protruding from the {tumor_loc} segments ({tumor_segs}), causing complete obstruction. {tumor_open_segs} segments appeared patent after clot removal.

Therapeutic Aspiration: Successful aspiration was performed to clean out the distal trachea and bilateral mainstems from mucus, blood, and blood clots.

Robotic Navigational Bronchoscopy (Ion) — {mass_loc} Mass
A CT-based navigation plan was loaded and partial registration was completed. The Ion robotic catheter was advanced to 0.5 cm from the planned target ({mass_seg}, {mass_size} lesion).
rEBUS: Concentric pattern with continuous margin and absence of linear-discrete air bronchogram.
Cone-Beam CT (Cios Spin): A low dose spin was performed; 3D reconstruction and overlay confirmed tool-in-lesion.

Sampling:
TBNA: 8 samples collected with 21G and 23G needles (Cytology, Flow, Cultures).
Cryobiopsy: 10 samples collected with 1.1 mm cryoprobe (6s freeze) (Pathology).
Brushing: 1 sample (Cytology).
Mini-BAL: 10 cc instilled, 5 cc return (Cytology).
Fiducial: One 0.8mm x 3mm soft tissue gold marker placed under fluoroscopy.
ROSE: TBNA showed atypical cells, large naked nuclei; cryo showed possible atypical histiocytes; not definitive for RCC.
{mass_loc} BAL: Performed with 40 cc saline, 15 cc return.

Robotic Navigational Bronchoscopy (Ion) — {nodule_loc} Nodule
Partial registration was repeated. The catheter was advanced to 0.5 cm from the target ({nodule_seg}, {nodule_size}).
rEBUS: Eccentric pattern with continuous margin.
Cone-Beam CT (Cios Spin): 3D reconstruction confirmed tool-in-lesion.

Sampling:
TBNA: 7 samples collected with 21G and 23G needles (Cytology, Cultures).
Cryobiopsy: 6 samples collected with 1.1 mm cryoprobe (Pathology).
Brushing: 1 sample (Cytology).
Mini-BAL: 10 cc instilled, 5 cc return (Micro/Cultures).
Fiducial: Attempted, but marker appeared to fall out and did not enter the nodule.
ROSE: Macrophages, lymphocytes, bronchial cells.
{nodule_loc} BAL: Performed with 60 cc saline, 60 cc return.

Post-biopsy fluoroscopy was negative for pneumothorax bilaterally.

EBUS Staging and Elastography
The EBUS scope was introduced. All lymph node stations were assessed; only those >=5 mm were sampled.
Lymph nodes sampled: {ebus_stations}.
Elastography showed mixed Type 1 (soft/benign) and Type 2 (mixed soft/stiff) patterns across stations.
ROSE for EBUS: Adequate lymphocytes and histiocytes present in all samples.

Endobronchial Tumor Management ({tumor_loc})
Endobronchial tumor within multiple {tumor_loc} segmental airways was friable and bled easily.
Biopsy: Endobronchial cryobiopsy performed at {tumor_segs}; lesions successfully removed and sent for pathology.
ROSE: Atypical cells, large naked nuclei.

Tumor Destruction ({tumor_segs}):
Cryotherapy: 1.1mm probe used (8-12 sec) to debulk tumor.
APC: 1.5mm probe (forcedAPC, 0.5 LPM, Effect 2) applied for coagulation/devitalization.

Results: Partial ablation achieved; hemostasis achieved (resolution of bleeding). However, airways ({tumor_segs}) remained 0% patent. {tumor_open_segs} airways were 100% patent after extraction of clot and nearby tumor.
Hemostasis: Nashville Grade 2 bleeding controlled with {bleeding_mgmt}.

Conclusion
Residual secretions were suctioned. No active bleeding was seen. The patient tolerated the procedure well without immediate complications.

SPECIMENS
{mass_loc} Mass: TBNA (cytology, flow, cultures), TBCBx (pathology), Brushing (cytology), Mini-BAL (cytology)
{mass_loc} BAL: Cell count, micro, cytology
{nodule_loc} Nodule: TBNA (cytology, cultures), TBCBx (pathology), Brushing (cytology), Mini-BAL (cultures)
{nodule_loc} BAL: Cell count, micro, cytology
EBUS TBNA: {ebus_stations} (cytology for each)
{tumor_loc} BAL: Cell count, micro, cytology
{tumor_loc} Endobronchial Biopsy: Pathology

IMPRESSION / PLAN
{patient_age}-year-old {gender_long} who underwent bronchoscopy for lung mass biopsy, lung nodule biopsy, lymph node assessment, and endobronchial tumor destruction.
Obtain post-procedure CXR (ordered).
Inpatient primary team and IP consult team to follow up final results.
If discharged, follow up in IP clinic in 1-2 weeks.
If hemoptysis develops, recommend starting nebulized TXA.
"""

# ==========================================
# 4. PROMPT STYLES
# ==========================================
prompt_styles = [
    # Style 1: Telegraphic / Handoff
    "Pt {age} {gender_short}. Indication: Mass {mass_loc}, nodule {nodule_loc}, {tumor_loc} atelectasis. Done: Ion bx x2 targets, EBUS, and tumor destruction {tumor_loc} for obstruction. Bleeding controlled. Samples sent.",

    # Style 2: Dictation
    "Please generate an IP operative report for a {age} year old {gender_long}. We performed a Robotic Navigational Bronchoscopy on a {mass_size} mass in the {mass_loc} and a {nodule_size} nodule in the {nodule_loc}. We also did EBUS staging and debulked a tumor in the {tumor_loc} using Cryo and APC.",

    # Style 3: Sloppy / Quick Note
    "{age}yo {gender_short} ion bronc. mass {mass_loc}, nodule {nodule_loc}. ebus stations {ebus_stations}. also had to ablate tumor in {tumor_loc} causing blockage. used cryo/apc. hemostasis ok.",

    # Style 4: Billing Focus
    "Complex bronchoscopy with Modifier 22. Robot nav to {mass_loc} and {nodule_loc}. EBUS staging. Endobronchial destruction of tumor at {tumor_loc}. Multiple biopsies and BALs. Time extended due to complexity.",

    # Style 5: Structured
    "Patient: {age} {gender_short}\nAttending: {attending_doctor}\nProcedures: Ion Robotic Bronchoscopy ({mass_loc}/{nodule_loc}), EBUS, Tumor Destruction ({tumor_loc})\nFindings: {mass_size} mass, {nodule_size} nodule, obstructing tumor {tumor_loc}.\nComplications: None."
]

# ==========================================
# 5. GENERATOR LOGIC
# ==========================================
def generate_dataset():
    dataset = []
    
    for _ in range(NUM_SAMPLES):
        # A. Randomly select variables
        age = random.choice(data_pool["age"])
        gender_tup = random.choice(data_pool["gender_tuple"]) # (long, short, pronoun)
        ref_doc = random.choice(data_pool["referring_doctor"])
        att_doc = random.choice(data_pool["attending_doctor"])
        bleeding = random.choice(data_pool["bleeding_mgmt"])
        ebus = random.choice(data_pool["ebus_stations"])
        
        # Select an anatomical scenario to ensure logical consistency
        scenario = random.choice(data_pool["anatomy_scenarios"])
        
        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_tup[1], 
            gender_long=gender_tup[0],
            mass_loc=scenario["mass_loc"],
            mass_size=scenario["mass_size"],
            nodule_loc=scenario["nodule_loc"],
            nodule_size=scenario["nodule_size"],
            tumor_loc=scenario["tumor_loc"],
            ebus_stations=ebus,
            attending_doctor=att_doc
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            patient_age=age,
            gender_long=gender_tup[0],
            referring_doctor=ref_doc,
            attending_doctor=att_doc,
            
            # Anatomy from Scenario
            mass_loc=scenario["mass_loc"],
            mass_seg=scenario["mass_seg"],
            mass_size=scenario["mass_size"],
            nodule_loc=scenario["nodule_loc"],
            nodule_seg=scenario["nodule_seg"],
            nodule_size=scenario["nodule_size"],
            tumor_loc=scenario["tumor_loc"],
            tumor_segs=scenario["tumor_segs"],
            tumor_open_segs=scenario["tumor_open_segs"],
            clot_loc_1=scenario["clot_loc_1"],
            clot_loc_2=scenario["clot_loc_2"],
            
            # Other variables
            ebus_stations=ebus,
            bleeding_mgmt=bleeding
        )
        
        dataset.append({"prompt": prompt, "completion": completion})
    
    return dataset

# ==========================================
# 6. EXECUTION & SAVING
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