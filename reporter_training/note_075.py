import json
import random
import os
import datetime

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_075"
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
    "dates": [
        "January 12, 2024", "February 28, 2024", "March 15, 2024", 
        "April 04, 2024", "May 22, 2024", "June 10, 2024", 
        "August 19, 2024", "September 05, 2024", "October 30, 2024"
    ],
    "ref_phys": [
        "Dr. Smith", "Dr. Al-Fayed", "Dr. Chen", "Dr. Rodriguez", 
        "Self-referred", "Dr. Johnson", "Dr. Gupta"
    ],
    "age": ["55", "59", "61", "64", "68", "72", "75", "81"],
    "gender_tuple": [("female", "F"), ("male", "M")],
    "attending": [
        "Dr. B. Wayne", "Dr. C. Kent", "Dr. D. Prince", "Dr. H. Jordan"
    ],
    "fellow": ["Dr. Grayson", "Dr. Todd", "Dr. Drake", "Dr. Brown"],
    
    # Lesion Location Logic: (Lobe, Segment Name, Segment ID)
    "lesion_location": [
        ("RUL", "Anterior Segment", "RB3"),
        ("RUL", "Apical Segment", "RB1"),
        ("RUL", "Posterior Segment", "RB2"),
        ("LUL", "Apicoposterior Segment", "LB1+2"),
        ("LUL", "Anterior Segment", "LB3"),
        ("RLL", "Superior Segment", "RB6"),
        ("LLL", "Superior Segment", "LB6"),
        ("RML", "Lateral Segment", "RB4")
    ],
    
    # Nodule Characteristics
    "nodule_size": ["0.8 cm", "1.0 cm", "1.2 cm", "1.5 cm", "1.8 cm", "2.1 cm"],
    "nodule_orientation": ["Eccentric", "Concentric"],
    "nodule_margin": ["continuous margin", "slightly irregular margin", "smooth margin"],
    
    # Sampling Counts
    "tbna_count": ["3", "4", "5", "6", "7"],
    "tbbx_count": ["4", "5", "6", "8"],
    
    # BAL Volumes (Instilled, Returned)
    "bal_vols": [
        ("60", "20"), ("100", "40"), ("50", "15"), ("120", "50"), ("60", "25")
    ],
    
    # Lymph Node Scenarios (The node that was actually sampled)
    # Format: (Station Name, Description, Size Status on CT)
    "ln_scenario": [
        ("Station 7", "Subcarinal", ">= 10 mm"),
        ("Station 4R", "Lower Paratracheal", ">= 10 mm"),
        ("Station 4L", "Lower Paratracheal", ">= 10 mm"),
        ("Station 11L", "Interlobar", ">= 10 mm"),
        ("Station 11Rs", "Interlobar", ">= 10 mm")
    ]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
note_template = """NOTE_ID:  {note_id} SOURCE_FILE: {note_id}.txt

INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: {date} CC Referred Physician: {ref_phys}

INDICATION FOR OPERATION The patient is a {age}-year-old {sex_long} who presents with a lung nodule.

The nature, purpose, risks, benefits, and alternatives to bronchoscopy were discussed with the patient in detail.

CONSENT Obtained before the procedure.

Indications, potential complications, and alternatives were discussed with the patient or surrogate.
The patient wished to proceed and informed consent was obtained.

PREOPERATIVE DIAGNOSIS
R91.1 Solitary Lung Nodule 

POSTOPERATIVE DIAGNOSIS
R91.1 Solitary Lung Nodule 

PROCEDURE
Therapeutic aspiration, initial episode (31645) 
Bronchoscopy with brushing (31623) 
Bronchoscopy with bronchoalveolar lavage (BAL) (31624) 
Transbronchial biopsy (TBBX), single lobe (31628) 
Transbronchial needle aspiration (TBNA), single lobe (31629) 
Fiducial marker placement (31626) 
Navigational Bronchoscopy (computer assisted) (31627) 
Radiologic guidance for CT guided needle placement (CIOS) (77012) 
3D rendering with interpretation (ION Planning Station) (76377) 
EBUS sampling 1 or 2 nodes (31652) 
Radial EBUS for peripheral lesion (31654) 
Ultrasound Elastography (76982, 76983) 

ATTENDING {attending}
ASSISTANT {fellow}
SUPPORT STAFF RN: [Name] RT: [Name]

ANESTHESIA General Anesthesia 
MONITORING Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.

INSTRUMENTATION Flexible Therapeutic Bronchoscope; Linear EBUS; Radial EBUS; Ion Robotic Bronchoscope.

ESTIMATED BLOOD LOSS None 
COMPLICATIONS None 

PROCEDURE IN DETAIL After the successful induction of anesthesia, a timeout was performed confirming the patient's name, procedure type, and procedure location.

Patient Position: Supine 
Initial Airway Inspection: Successful therapeutic aspiration was performed to clean out the Right Mainstem, Bronchus Intermedius, and Left Mainstem from mucus.

Robotic Navigational Bronchoscopy (Ion) A CT chest scan was used on a separate planning station to generate a 3D rendering of the pathway to the target.
The navigational plan was reviewed, verified, and loaded into the robotic bronchoscopy platform.

Registration: Robotic navigation was performed with the Ion platform using partial registration.
Navigation: The Ion robotic catheter was used to engage the {lesion_seg} of the {lesion_lobe} ({lesion_id}).
Under navigational guidance, the catheter was advanced to 1.0 cm away from the planned target.

rEBUS Verification: Radial EBUS was performed to confirm the location of the nodule (approx. {nodule_size} in diameter).
The nodule location was confirmed as {nodule_orientation} with a {nodule_margin}.

Cone Beam CT (Cios Spin): The Cios Spin system was used for evaluation of nodule location.
A low dose spin was performed to acquire CT imaging.
3D reconstructions were performed on an independent workstation and interpreted personally by the attending.

Adjustment: The images were passed to the Ion platform; using the newly acquired nodule location, the robotic system was adjusted to the new targeted location.

Target Sampling ({lesion_lobe} {lesion_seg}/{lesion_id})

TBNA: Transbronchial needle aspiration was performed with a 21G needle through the extended working channel.
Total {tbna_count} samples were collected.

TBBX: Transbronchial biopsy was performed with alligator forceps. Total {tbbx_count} samples were collected.
Brushing: Transbronchial brushing was performed with a protected cytology brush. Total 1 sample was collected.
BAL: Bronchial alveolar lavage was performed. Instilled {bal_instilled} cc of NS, suction returned with {bal_return} cc of NS.
Fiducial Placement: A fiducial marker (0.8mm x 3mm soft tissue gold CIVCO) was loaded with bone wax and placed under fluoroscopy guidance.
Inspection prior to withdrawal demonstrated no evidence of bleeding.

EBUS STAGING

Indications: Diagnostic and Staging.
Technique: All lymph node stations were assessed. Only those 5 mm or greater in short axis were sampled.
Lymph node sizing was performed by EBUS and sampling was performed using a 22-gauge needle.
Endobronchial ultrasound (EBUS) elastography was performed to assess lymph node stiffness.

Lymph Nodes Evaluated:

{ln_station} ({ln_desc}): {ln_size_status} on CT.
Demonstrated a Type 1 elastographic pattern (predominantly soft/benign).
Despite benign appearance, TBNA was performed to confirm absence of malignancy. 4 samples were obtained.

Other stations evaluated but not sampled due to benign appearance/size < 10mm.

There were no immediate complications.
At the conclusion of the operation, the patient was extubated in the operating room and transported to the recovery room in stable condition.

SPECIMENS

{lesion_lobe} TBNA ({tbna_count} samples) — Microbiology, Cytology, Flow cytometry 
{lesion_lobe} TBBX ({tbbx_count} samples) — Pathology 
{lesion_lobe} Brush (1 sample) — Microbiology 
{lesion_lobe} BAL — Microbiology and Cytology 
{ln_station} TBNA 

IMPRESSION / PLAN

{age}-year-old {sex_long} who presented for bronchoscopy for lung nodule and lymphadenopathy.
Successful sampling of {lesion_lobe} nodule and {ln_station} lymph node.

Follow-up results.
Follow-up CXR.
"""

prompt_styles = [
    # Style 1: Telegraphic / Summary
    "Bronchoscopy report. {age}yo {sex_short}. Indication: Lung nodule. Procedure: Ion nav bronch to {lesion_lobe} {lesion_seg} ({lesion_id}) + EBUS. Findings: {nodule_size} {nodule_orientation} nodule. Sampling: TBNA x{tbna_count}, TBBX x{tbbx_count}, BAL. EBUS sampled {ln_station}. Fiducial placed. No comps.",

    # Style 2: Dictation Style
    "Please generate an op note for a {age} year old {sex_long} patient referred by {ref_phys}. We performed a robotic assisted bronchoscopy with Ion and EBUS. We targeted a nodule in the {lesion_lobe}, specifically the {lesion_seg}. Radial EBUS confirmed it was {nodule_size}. We took {tbna_count} TBNA samples and {tbbx_count} biopsies. We also sampled {ln_station} via EBUS. Everything went well.",

    # Style 3: Sloppy / Quick Input
    "{age} {sex_short} R91.1 nodule. Robot bronch used. Target {lesion_lobe} {lesion_id}, size {nodule_size}. did brushing, bal, tbna ({tbna_count}), tbbx ({tbbx_count}). Also did EBUS on {ln_station} ({ln_desc}). Placed gold fiducial. Dr. {attending}.",

    # Style 4: Billing/Coding Focus
    "Procedure codes: 31645, 31623, 31624, 31628, 31629, 31626, 31627, 31652. Patient {age} {sex_short}. Site: {lesion_lobe} {lesion_seg}. Modalities: Ion, rEBUS, Cone Beam CT. LN Sampled: {ln_station}. Specimen collected for path/micro.",

    # Style 5: Structured Request
    "PATIENT: {age} / {sex_short}\nREFERRING: {ref_phys}\nPROCEDURE: Ion Robotic Bronchoscopy + EBUS\nTARGET: {lesion_lobe} {lesion_seg} ({lesion_id})\nNODULE: {nodule_size}, {nodule_orientation}\nSAMPLES: TBNA ({tbna_count}), TBBX ({tbbx_count}), BAL ({bal_instilled}/{bal_return})\nEBUS TARGET: {ln_station}\nFIDUCIAL: Yes"
]

# ==========================================
# 4. GENERATOR LOGIC
# ==========================================
def generate_dataset():
    dataset = []
    
    for _ in range(NUM_SAMPLES):
        # A. Randomly select variables
        date = random.choice(data_pool["dates"])
        ref_phys = random.choice(data_pool["ref_phys"])
        age = random.choice(data_pool["age"])
        gender_tup = random.choice(data_pool["gender_tuple"])
        sex_long = gender_tup[0]
        sex_short = gender_tup[1]
        
        attending = random.choice(data_pool["attending"])
        fellow = random.choice(data_pool["fellow"])
        
        # Lesion details
        lesion_data = random.choice(data_pool["lesion_location"])
        lesion_lobe = lesion_data[0]
        lesion_seg = lesion_data[1]
        lesion_id = lesion_data[2]
        
        nodule_size = random.choice(data_pool["nodule_size"])
        nodule_orientation = random.choice(data_pool["nodule_orientation"])
        nodule_margin = random.choice(data_pool["nodule_margin"])
        
        tbna_count = random.choice(data_pool["tbna_count"])
        tbbx_count = random.choice(data_pool["tbbx_count"])
        
        bal_data = random.choice(data_pool["bal_vols"])
        bal_instilled = bal_data[0]
        bal_return = bal_data[1]
        
        # Lymph Node Scenario
        ln_data = random.choice(data_pool["ln_scenario"])
        ln_station = ln_data[0]
        ln_desc = ln_data[1]
        ln_size_status = ln_data[2]
        
        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, sex_short=sex_short, sex_long=sex_long,
            ref_phys=ref_phys, attending=attending,
            lesion_lobe=lesion_lobe, lesion_seg=lesion_seg, lesion_id=lesion_id,
            nodule_size=nodule_size, nodule_orientation=nodule_orientation,
            tbna_count=tbna_count, tbbx_count=tbbx_count,
            bal_instilled=bal_instilled, bal_return=bal_return,
            ln_station=ln_station, ln_desc=ln_desc
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            date=date,
            ref_phys=ref_phys,
            age=age, sex_long=sex_long,
            attending=attending, fellow=fellow,
            lesion_lobe=lesion_lobe, lesion_seg=lesion_seg, lesion_id=lesion_id,
            nodule_size=nodule_size, nodule_orientation=nodule_orientation, nodule_margin=nodule_margin,
            tbna_count=tbna_count, tbbx_count=tbbx_count,
            bal_instilled=bal_instilled, bal_return=bal_return,
            ln_station=ln_station, ln_desc=ln_desc, ln_size_status=ln_size_status
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