import json
import random
import os
import datetime

# ==========================================
# 1. CONFIGURATION
# ==========================================
# [cite_start]EXTRACTED FROM NOTE [cite: 1]
NOTE_ID = "note_065"
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
    "age": [str(x) for x in range(45, 92)],
    "gender_tuple": [("female", "F"), ("male", "M")],
    "ref_physician": [
        "Dr. Smith", "Dr. Johnson", "Dr. Williams", "Dr. Brown", 
        "Dr. Jones", "Dr. Garcia", "Dr. Miller", "Dr. Davis"
    ],
    "indication": [
        "lung mass", "mediastinal lymphadenopathy", "lung nodule", 
        "hilar mass", "abnormal CT chest findings", "PET-avid lymph nodes"
    ],
    "preop_dx_code": ["R91.8", "R91.1", "C34.90", "D02.20"],
    "preop_dx_text": [
        "Other nonspecific abnormal finding of lung field", 
        "Solitary pulmonary nodule", 
        "Malignant neoplasm of unspecified part of bronchus or lung",
        "Carcinoma in situ of bronchus and lung"
    ],
    "mucus_locations": [
        "Right Mainstem, Bronchus Intermedius, and Left Mainstem",
        "Left Lower Lobe and Right Lower Lobe",
        "Bilateral mainstems",
        "Right Upper Lobe and Bronchus Intermedius"
    ],
    # Tuples: (Station Name, Anatomic Location Description)
    "node_stations": [
        ("Station 4R", "lower paratracheal"),
        ("Station 4L", "lower paratracheal"),
        ("Station 7", "subcarinal"),
        ("Station 11Rs", "superior hilar"),
        ("Station 11L", "interlobar"),
        ("Station 10R", "hilar"),
    ],
    # Tuples: (Result Text, Adequacy Statement, Short Summary for Prompt)
    "rose_outcomes": [
        ("suggestive of blood and bronchial cells", "not adequate", "Inadequate"),
        ("suggestive of Positive for malignancy", "adequate", "Positive"),
        ("suggestive of Adenocarcinoma", "adequate", "Adeno"),
        ("suggestive of Small Cell Carcinoma", "adequate", "Small Cell"),
        ("suggestive of Granulomatous Inflammation", "adequate", "Granulomas"),
        ("suggestive of Anthracotic Pigment / Negative for Malignancy", "adequate", "Negative"),
        ("suggestive of Lymphocytes / Negative for Malignancy", "adequate", "Negative")
    ]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
# [cite_start]Based on [cite: 1, 4, 13, 22]
note_template = """INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: {date_str} CC Referred Physician: {ref_physician}

INDICATION FOR OPERATION [REDACTED] is a {age}-year-old {gender_long} who presents with a {indication}.

CONSENT Obtained before the procedure.

The nature, purpose, risks, benefits and alternatives to Bronchoscopy were discussed with the patient in detail.
The patient wished to proceed and informed consent was obtained.

PREOPERATIVE DIAGNOSIS

{dx_code} {dx_text}.

POSTOPERATIVE DIAGNOSIS

{dx_code} {dx_text}.

Positive for malignancy on ROSE ({pos_station}).

PROCEDURE

Therapeutic aspiration (initial episode).
Endobronchial Ultrasound (EBUS) lymph node sampling ({num_nodes} nodes).

Transbronchial needle aspiration (TBNA).

Rapid On-Site Evaluation (ROSE).

ANESTHESIA General Anesthesia.

MONITORING Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.

INSTRUMENTATION Linear EBUS; Disposable Bronchoscope; 25-gauge and 22-gauge TBNA needles.

ESTIMATED BLOOD LOSS None.

COMPLICATIONS None.

PROCEDURE IN DETAIL After the successful induction of anesthesia, a timeout was performed (confirming the patient's name, procedure type, and procedure location).

Initial Airway Inspection & Therapeutic Aspiration Successful therapeutic aspiration was performed to clean out the {mucus_loc} from mucus.

EBUS Staging Indications: Diagnostic. All lymph node stations were assessed.
Only those 5 mm or greater in short axis were sampled.
Lymph node sizing was performed by EBUS and sampling by transbronchial needle aspiration was performed using 25-gauge Needle and 22-gauge Needle.

Lymph Nodes Evaluated:


{node_1_name} ({node_1_loc}): The lymph node was ≥ 10 mm on CT (Metabolic activity unknown).
The lymph node was photographed and sampled. {node_1_passes} endobronchial ultrasound guided transbronchial biopsies were performed.
ROSE Results: Preliminary ROSE Cytology was reported as {node_1_adequacy} and {node_1_result}.
Final results are pending.


{node_2_name} ({node_2_loc}): The lymph node was ≥ 10 mm on CT (Metabolic activity unknown).
The lymph node was photographed and sampled. {node_2_passes} endobronchial ultrasound guided transbronchial biopsies were performed.
ROSE Results: Preliminary ROSE Cytology was reported as {node_2_adequacy} and {node_2_result}.
Final results are pending.

Conclusion The patient tolerated the procedure well. There were no immediate complications.
At the conclusion of the operation, the patient was extubated in the operating room and transported to the recovery room in stable condition.

SPECIMEN(S)

TBNA and TBNB station {node_1_short}.

TBNA and TBNB station {node_2_short}.

IMPRESSION/PLAN

{age}-year-old {gender_long} presenting for bronchoscopy for {indication}.

Therapeutic aspiration performed for mucus clearance.

EBUS-TBNA performed:


{node_1_name}: ROSE {node_1_summary}.


{node_2_name}: ROSE {node_2_summary}.

Follow-up pathology results."""

# 5 Prompt Styles
prompt_styles = [
    # Style 1: Telegraphic
    "Write IP Op Note. {age}{gender_short}, Ref: {ref_physician}. Ind: {indication}. Dx: {dx_code}. Proc: Asp ({mucus_loc}), EBUS TBNA. Nodes: {node_1_short} ({node_1_summary}), {node_2_short} ({node_2_summary}). No comps.",
    
    # Style 2: Dictation
    "Please generate an operative report for a {age} year old {gender_long} referred by {ref_physician} for {indication}. We performed therapeutic aspiration of the {mucus_loc} and EBUS TBNA of two stations. Station {node_1_short} was {node_1_summary} and station {node_2_short} was {node_2_summary}. Use diagnosis {dx_code}.",
    
    # Style 3: Sloppy / Quick
    "{age}yo {gender_short} with {indication}. EBUS done. {node_1_short} showed {node_1_summary}, {node_2_short} showed {node_2_summary}. Cleaned mucus from {mucus_loc}. General anesthesia used. {dx_code}.",
    
    # Style 4: Billing Focus
    "Procedure: Bronchoscopy with EBUS/TBNA. Indication: {indication}. Dx: {dx_code}. Patient: {age} {gender_short}. Samples: {node_1_short} ({node_1_summary}) and {node_2_short} ({node_2_summary}). Aspiration performed for secretions.",
    
    # Style 5: Structured
    "Patient Age: {age}\nGender: {gender_long}\nIndication: {indication}\nDiagnosis: {dx_code}\nProcedures: Therapeutic Aspiration, EBUS-TBNA\nFindings:\n- {node_1_short}: {node_1_summary}\n- {node_2_short}: {node_2_summary}\n- Secretions cleared from: {mucus_loc}"
]

# ==========================================
# 4. GENERATOR LOGIC
# ==========================================
def generate_dataset():
    dataset = []
    
    for _ in range(NUM_SAMPLES):
        # A. Randomly select basic variables
        age = random.choice(data_pool["age"])
        gender_tup = random.choice(data_pool["gender_tuple"])
        ref_physician = random.choice(data_pool["ref_physician"])
        indication = random.choice(data_pool["indication"])
        
        # Diagnosis Logic
        dx_index = random.randint(0, len(data_pool["preop_dx_code"]) - 1)
        dx_code = data_pool["preop_dx_code"][dx_index]
        dx_text = data_pool["preop_dx_text"][dx_index]
        
        mucus_loc = random.choice(data_pool["mucus_locations"])
        
        # B. Complex Logic for Lymph Nodes (Ensure 2 distinct nodes)
        nodes = random.sample(data_pool["node_stations"], 2)
        node_1 = nodes[0]
        node_2 = nodes[1]
        
        # Assign ROSE results to nodes
        rose_1 = random.choice(data_pool["rose_outcomes"])
        rose_2 = random.choice(data_pool["rose_outcomes"])
        
        # Determine "Positive for malignancy on ROSE" variable for header
        # If either is positive, list it. If neither, list "Negative".
        pos_stations = []
        if "Positive" in rose_1[2] or "Adeno" in rose_1[2] or "Small Cell" in rose_1[2]:
            pos_stations.append(node_1[0])
        if "Positive" in rose_2[2] or "Adeno" in rose_2[2] or "Small Cell" in rose_2[2]:
            pos_stations.append(node_2[0])
            
        if pos_stations:
            pos_station_str = ", ".join(pos_stations)
        else:
            pos_station_str = "Negative/Inadequate"

        # Generate a random date
        date_obj = datetime.date.today() - datetime.timedelta(days=random.randint(0, 365))
        date_str = date_obj.strftime("%m/%d/%Y")

        # C. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, gender_short=gender_tup[1], gender_long=gender_tup[0],
            ref_physician=ref_physician, indication=indication,
            dx_code=dx_code, mucus_loc=mucus_loc,
            node_1_short=node_1[0], node_1_summary=rose_1[2],
            node_2_short=node_2[0], node_2_summary=rose_2[2]
        )
        
        # D. Generate Completion (Structured Note)
        # Extract short name from Station string (e.g. "Station 4R" -> "4R") for Specimen section if needed, 
        # though the template uses full station name usually.
        n1_short_clean = node_1[0].replace("Station ", "")
        n2_short_clean = node_2[0].replace("Station ", "")

        completion = note_template.format(
            note_id=NOTE_ID,
            date_str=date_str,
            ref_physician=ref_physician,
            age=age, gender_long=gender_tup[0],
            indication=indication,
            dx_code=dx_code, dx_text=dx_text,
            pos_station=pos_station_str,
            num_nodes="2",
            mucus_loc=mucus_loc,
            # Node 1 Details
            node_1_name=node_1[0],
            node_1_loc=node_1[1],
            node_1_passes=random.choice(["4", "6", "8"]),
            node_1_adequacy=rose_1[1],
            node_1_result=rose_1[0],
            node_1_short=n1_short_clean,
            node_1_summary=rose_1[2],
            # Node 2 Details
            node_2_name=node_2[0],
            node_2_loc=node_2[1],
            node_2_passes=random.choice(["4", "6", "8"]),
            node_2_adequacy=rose_2[1],
            node_2_result=rose_2[0],
            node_2_short=n2_short_clean,
            node_2_summary=rose_2[2]
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