import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_067"
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
        "April 04, 2024", "May 20, 2024", "June 10, 2024", 
        "August 18, 2024", "October 05, 2024", "November 22, 2024"
    ],
    "age": ["55", "59", "61", "63", "67", "70", "72", "75", "78", "81"],
    "gender_tuple": [("female", "F", "She", "her"), ("male", "M", "He", "his")],
    "ref_physician": [
        "Dr. Sarah Miller", "Dr. James Chen", "Dr. Emily Rost", 
        "Dr. Alan Grant", "Dr. Lisa Wong", "Dr. Robert Smith"
    ],
    "lesion_size": ["1.8", "2.5", "3.0", "3.5", "4.0", "4.2", "5.1"],
    "needle_gauge": ["19G", "21G", "22G"],
    "ventilation_settings": [
        {"mode": "VCV", "rr": "12", "tv": "300", "peep": "12", "fio2": "100%", "flow": "10", "pmean": "15"},
        {"mode": "PCV", "rr": "14", "tv": "350", "peep": "10", "fio2": "90%", "flow": "12", "pmean": "18"},
        {"mode": "VCV", "rr": "10", "tv": "400", "peep": "8", "fio2": "100%", "flow": "10", "pmean": "14"},
        {"mode": "VCV", "rr": "13", "tv": "320", "peep": "14", "fio2": "100%", "flow": "11", "pmean": "16"}
    ],
    "ablation_time_long": ["10:00", "15:00", "20:00", "25:00"],
    "ablation_time_short": ["05:00", "08:00", "10:00", "12:00"],
    "ablation_temp": ["90", "95", "100", "105"],
    "antibiotics": [
        {"iv": "Unasyn", "po": "Moxifloxacin"},
        {"iv": "Zosyn", "po": "Levofloxacin"},
        {"iv": "Rocephin", "po": "Azithromycin"},
        {"iv": "Ampicillin-Sulbactam", "po": "Augmentin"}
    ],
    "samples_count": ["1", "2", "3", "4"],
    "ebus_feature": ["continuous margin", "distinct margin", "lobulated margin"],
    "echotexture": ["heterogenous", "homogeneous"],
    "diagnosis_code": ["R91.1 Solitary Lung Nodule", "R91.8 Other nonspecific abnormal finding of lung field", "D38.1 Neoplasm of uncertain behavior"]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
# Template preserves the specific anatomical segments (RB1/RB2/RB3) consistent with RUL procedures
note_template = """INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: {date} CC Referred Physician: {ref_physician}

INDICATION FOR OPERATION {patient_name_redacted} is a {age}-year-old {gender_long} who presents with a pulmonary nodule.
The nature, purpose, risks, benefits, and alternatives to bronchoscopy were discussed with the patient in detail.
CONSENT Obtained before the procedure. Indications, potential complications, and alternatives were discussed.
PREOPERATIVE DIAGNOSIS

{dx_code}

POSTOPERATIVE DIAGNOSIS

{dx_code}

PROCEDURE

Robotic navigational bronchoscopy (Ion) 

Radial EBUS localization 

Cone-beam CT guidance (Cios Spin) with 3D rendering and interpretation 

Therapeutic aspiration (airway clearance) 

TBNA of RUL mass ({needle_gauge} needle) 

Transbronchial microwave ablation of RUL mass 

ANESTHESIA General Anesthesia 

MONITORING Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.
INSTRUMENTATION Flexible Therapeutic Bronchoscope, Flexible Hybrid (Pediatric) Bronchoscope, Radial EBUS, Ion Robotic Bronchoscope.
ESTIMATED BLOOD LOSS Minimum 

COMPLICATIONS None 

PROCEDURE IN DETAIL After the successful induction of anesthesia, a timeout was performed confirming the patient's name, procedure type, and procedure location.
Initial Airway Inspection & Therapeutic Aspiration Successful therapeutic aspiration was performed to clean out the Trachea (Middle 1/3), Trachea (Distal 1/3), Right Mainstem, and Bronchus Intermedius from mucus.
Robotic Navigational Bronchoscopy (Ion) — RUL Mass A CT Chest scan was placed on a separate planning station to generate a 3D rendering of the pathway to the target.
The navigational plan was reviewed, verified, and loaded into the robotic bronchoscopy platform.

Ventilation Parameters: Mode: {vent_mode} |
RR: {vent_rr} | TV: {vent_tv} | PEEP: {vent_peep} | FiO2: {vent_fio2} | Flow Rate: {vent_flow} |
Pmean: {vent_pmean}.

Navigation and Localization Robotic navigation was performed with the Ion platform using partial registration.
Targeting: The Ion robotic catheter was used to engage the Anterior Segment of the RUL (RB3).
The target lesion is about {size} cm in diameter.


Alignment: Under navigational guidance, the catheter was advanced to 1.0 cm away from the planned target.
The needle was advanced into the lesion.


Imaging & Adjustment: Cone Beam CT (Cios Spin) was performed with 3D reconstructions on an independent workstation.
The images were interpreted, and the Ion robotic system was adjusted to the newly acquired nodule location.
Target Sampling (RUL Mass)


TBNA: Transbronchial needle aspiration was performed with a {needle_gauge} needle through the extended working channel.
Total {sample_count} sample was collected and sent for cytology.


rEBUS Confirmation: Radial EBUS confirmed the nodule location was Concentric after initial puncture.
Features noted: {ebus_feat}, {echo_text} echotexture.

Transbronchial Microwave Ablation Once a tunnel had been created into the lesion with TBNA, transbronchial microwave ablation was performed.
Ablation 1: Medium Antenna at {temp}°C for {time_long} min.


Ablation 2 (RB2): RB2 was engaged, and the microwave catheter was placed in the lateral superior aspect of the lung mass.
CBCT confirmed location.

Settings: Medium Antenna at {temp}°C for {time_short} min.
Ablation 3 (RB1): RB1 was engaged, and the microwave catheter was placed in the superior medial aspect of the lung mass.
CBCT confirmed location.

Settings: Medium Antenna at {temp}°C for {time_short} min.
Final Confirmation Cone Beam CT (Cios Spin) was performed again for evaluation. 3D reconstructions confirmed tool-in-lesion.
The patient tolerated the procedure well with no immediate complications.
At the conclusion of the operation, the patient was extubated in the operating room and transported to the recovery room in stable condition.
SPECIMEN(S)

RUL mass TBNA (cyto) 

IMPRESSION/PLAN {patient_name_redacted} is a {age}-year-old {gender_long} who presents for bronchoscopy for lung nodules.
RLL nodule and RUL mass underwent TBNA and MWA.

Follow-up CXR.

Admit to medicine for observation.

Monitor for post-ablation pain.
Start empiric antibiotics (IV {abx_iv} as inpatient, PO {abx_po} as an outpatient).
"""

prompt_styles = [
    # Style 1: Telegraphic
    "Operative note: {age}{gender_short}, {size}cm RUL mass. Ion bronc, EBUS, {needle_gauge} TBNA. MWA x3 (RB1/2/3). {abx_iv}/{abx_po}. No complications.",
    
    # Style 2: Dictation
    "Please generate a procedure note for Dr. {ref_physician}'s patient. {age}yo {gender_long}. RUL mass approx {size} cm. We did robotic navigation, EBUS, and microwave ablation. Ablation settings were {temp} degrees. Samples taken with {needle_gauge} needle. Discharged on {abx_po}.",
    
    # Style 3: Sloppy / Quick
    "{age} {gender_short} ion bronchoscopy. RUL lesion {size}cm. 3 ablations done @ {temp}C. cone beam ct used. start {abx_iv} then {abx_po}.",
    
    # Style 4: Billing Focus
    "Procedure: Robotic Bronchoscopy/MWA. Dx: {dx_code}. Patient: {age} {gender_short}. RUL Target {size}cm. Tools: Ion, Cios Spin, {needle_gauge} needle. Plan: Admit, {abx_iv}.",
    
    # Style 5: Structured
    "Patient: {age} {gender_short}\nRef: {ref_physician}\nProcedure: Ion Bronchoscopy + MWA\nFindings: {size} cm RUL mass, {echo_text} on EBUS\nPlan: Admit for obs, {abx_iv}."
]

# ==========================================
# 4. GENERATOR LOGIC
# ==========================================
def generate_dataset():
    dataset = []
    
    for _ in range(NUM_SAMPLES):
        # A. Randomly select variables
        date = random.choice(data_pool["dates"])
        age = random.choice(data_pool["age"])
        gender_tup = random.choice(data_pool["gender_tuple"])
        gender_long = gender_tup[0]
        gender_short = gender_tup[1]
        ref_physician = random.choice(data_pool["ref_physician"])
        size = random.choice(data_pool["lesion_size"])
        needle_gauge = random.choice(data_pool["needle_gauge"])
        
        vent = random.choice(data_pool["ventilation_settings"])
        
        time_long = random.choice(data_pool["ablation_time_long"])
        time_short = random.choice(data_pool["ablation_time_short"])
        temp = random.choice(data_pool["ablation_temp"])
        
        abx = random.choice(data_pool["antibiotics"])
        sample_count = random.choice(data_pool["samples_count"])
        ebus_feat = random.choice(data_pool["ebus_feature"])
        echo_text = random.choice(data_pool["echotexture"])
        dx_code = random.choice(data_pool["diagnosis_code"])
        
        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_short, 
            gender_long=gender_long,
            size=size,
            ref_physician=ref_physician,
            needle_gauge=needle_gauge,
            abx_iv=abx["iv"],
            abx_po=abx["po"],
            temp=temp,
            dx_code=dx_code,
            echo_text=echo_text
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            date=date,
            ref_physician=ref_physician,
            patient_name_redacted="[REDACTED]",
            age=age,
            gender_long=gender_long,
            dx_code=dx_code,
            needle_gauge=needle_gauge,
            vent_mode=vent["mode"],
            vent_rr=vent["rr"],
            vent_tv=vent["tv"],
            vent_peep=vent["peep"],
            vent_fio2=vent["fio2"],
            vent_flow=vent["flow"],
            vent_pmean=vent["pmean"],
            size=size,
            sample_count=sample_count,
            ebus_feat=ebus_feat,
            echo_text=echo_text,
            temp=temp,
            time_long=time_long,
            time_short=time_short,
            abx_iv=abx["iv"],
            abx_po=abx["po"]
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