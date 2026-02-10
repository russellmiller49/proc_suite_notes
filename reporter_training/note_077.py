import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_077" 
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
    "age": ["55", "62", "67", "71", "74", "59", "48", "81"],
    "gender_tuple": [("female", "F"), ("male", "M")],
    "attending": ["Dr. Smith", "Dr. Chen", "Dr. Rodriguez", "Dr. Patel", "Dr. Ingraham"],
    "referring": ["Dr. Jones", "Dr. Williams", "Self-referred", "Dr. Lee"],
    
    # Indication & Diagnosis Logic
    "clinical_scenario": [
        {
            "indication": "lymphadenopathy",
            "pre_dx_code": "R59.0",
            "pre_dx_text": "Localized enlarged lymph nodes",
            "rose_finding": "Granulomas",
            "final_dx_code": "D86.0", # Sarcoidosis implied
            "final_dx_text": "Sarcoidosis (suggested by Granulomas)",
            "node_appearance": "hypermetabolic via PET-CT",
            "bal_color": "clear"
        },
        {
            "indication": "mediastinal adenopathy",
            "pre_dx_code": "R59.9",
            "pre_dx_text": "Enlarged lymph nodes, unspecified",
            "rose_finding": "Malignant cells consistent with Adenocarcinoma",
            "final_dx_code": "C34.90",
            "final_dx_text": "Non-small cell lung cancer",
            "node_appearance": "enlarged and necrotic center",
            "bal_color": "slightly hemorrhagic"
        },
        {
            "indication": "abnormal CT findings",
            "pre_dx_code": "R91.8",
            "pre_dx_text": "Other nonspecific abnormal finding of lung field",
            "rose_finding": "Reactive Lymphocytes",
            "final_dx_code": "R59.0",
            "final_dx_text": "Reactive Lymphadenopathy",
            "node_appearance": "enlarged but distinct borders",
            "bal_color": "cloudy"
        }
    ],

    # Aspiration Scenarios
    "aspiration_scope": [
        "Trachea (Middle 1/3), Trachea (Distal 1/3), Right Mainstem, Bronchus Intermedius, Left Mainstem, Carina",
        "Trachea and bilateral mainstems",
        "Right Mainstem, RUL, and Bronchus Intermedius",
        "Minimal secretions noted, aspiration performed in Distal Trachea only"
    ],

    # BAL Locations
    "bal_location": [
        "Lateral Segment of RML (RB4) and Medial Segment of RML (RB5)",
        "Superior Segment of LUL",
        "Posterior Basal Segment of RLL",
        "Lingula (LB4/LB5)"
    ],

    # EBUS Stations
    "stations_list": [
        ["Station 11L", "Station 7 (Subcarinal)", "Station 11Ri"],
        ["Station 4R", "Station 7 (Subcarinal)", "Station 4L"],
        ["Station 7 (Subcarinal)", "Station 10R", "Station 11R"],
        ["Station 4L", "Station 11L"]
    ]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
note_template = """NOTE_ID:  {note_id} SOURCE_FILE: {note_id}.txt

INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: [Date] CC Referred Physician: {referring}

INDICATION FOR OPERATION {age}-year-old {gender_long} who presents with {indication}. The nature, purpose, risks, benefits, and alternatives to Bronchoscopy were discussed with the patient in detail.

CONSENT Obtained before the procedure. Indications, potential complications, and alternatives were discussed with the patient or surrogate. The patient wished to proceed and informed consent was obtained.

PREOPERATIVE DIAGNOSIS
{pre_dx_code} {pre_dx_text}

POSTOPERATIVE DIAGNOSIS
{pre_dx_code} {pre_dx_text}
{rose_finding} noted on ROSE

PROCEDURE
Therapeutic aspiration (initial episode)
Diagnostic bronchoscopy with Bronchoalveolar lavage (BAL)
EBUS sampling {num_nodes} or more nodes

ATTENDING {attending}
ASSISTANT [Fellow name]
SUPPORT STAFF RN: [Name] RT: [Name]

ANESTHESIA General Anesthesia

MONITORING Pulse oximetry, heart rate, telemetry, and blood pressure were continuously monitored by an independent trained observer throughout the procedure.

INSTRUMENTATION Linear EBUS, Disposable Bronchoscope.

ESTIMATED BLOOD LOSS Minimum
COMPLICATIONS None

PROCEDURE IN DETAIL After the successful induction of anesthesia, a timeout was performed (confirming the patient's name, procedure type, and procedure location).
Patient position: [Supine]

Initial Airway Inspection: Normal appearing airway anatomy and mucosa bilaterally to the segmental level.

Therapeutic Aspiration Successful therapeutic aspiration was performed to clean out the {aspiration_scope} from mucus, blood, and blood clots.

EBUS STAGING The EBUS bronchoscope was introduced. All lymph node stations were assessed.
Technique: Only lymph nodes measuring ≥5 mm in short axis were sampled.
Sampling was performed by transbronchial needle aspiration using a 22-gauge needle.

Lymph Nodes Inspected: 4R, 4L, 7, 11Rs, 11Ri, 11L.

Stations Sampled:

{node_details_block}

Overall ROSE Diagnosis: {rose_finding}.
Final Results: Pending.

Bronchoalveolar Lavage (BAL) Bronchial alveolar lavage was performed at the {bal_loc}.
Instilled {fluid_in} cc of NS, suction returned with {fluid_out} cc of NS.
Samples sent for Cell Count, Microbiology (Cultures/Viral/Fungal), and Cytology.

Completion The patient tolerated the procedure well.
There were no immediate complications. At the conclusion of the operation, the patient was extubated in the operating room and transported to the recovery room in stable condition.

SPECIMENS
EBUS-TBNA: {stations_joined}
{bal_short_loc} Bronchoalveolar lavage

IMPRESSION / PLAN
{age}-year-old {gender_long} who presents for bronchoscopy for {indication}.
EBUS-TBNA performed on stations {stations_joined}; ROSE suggestive of {rose_short} at sampled stations.
BAL performed in {bal_short_loc}.
Follow up bronchoscopic lab work.
"""

prompt_styles = [
    # Style 1: Telegraphic / Brief
    "Generate EBUS note. Pt {age} {gender_short}. Indication: {indication}. ROSE: {rose_short}. Stations: {stations_joined}. BAL: {bal_short_loc}.",
    
    # Style 2: Dictation style
    "Please dictate a procedure note for Dr. {attending}. Patient is a {age} year old {gender_long} with {indication}. We did EBUS and BAL. Found {rose_short} in stations {stations_joined}. BAL was done in the {bal_short_loc}.",
    
    # Style 3: Sloppy / Physician Quick Note
    "{age}yo {gender_short} adenopathy. EBUS/BAL. Sampled {stations_joined} -> ROSE {rose_short}. BAL {bal_short_loc}. No complications.",
    
    # Style 4: Billing Focus
    "Procedure Codes: EBUS (3+ nodes), BAL, Therapeutic Asp. Pt: {age} {gender_short}. Dx: {pre_dx_code}. Findings: {rose_short}.",
    
    # Style 5: Structured Request
    "Procedure: EBUS + BAL\nPatient: {age} {gender_short}\nIndication: {indication}\nNodes Sampled: {stations_joined}\nROSE Results: {rose_short}\nAttending: {attending}"
]

# ==========================================
# 4. GENERATOR LOGIC
# ==========================================
def generate_node_block(stations, rose_finding, appearance):
    """Generates the detailed EBUS STAGING text block dynamically."""
    block = ""
    for station in stations:
        # Randomize number of passes (3 or 4)
        passes = random.choice(["3", "4"])
        
        # Logic: Make one node 'adequate' and others potentially 'inadequate' or also 'adequate'
        # For simplicity in this script, we apply the main finding to at least one node.
        
        individual_rose = rose_finding if station == stations[1] or station == stations[0] else "Preliminary cytology reported as inadequate or blood only"
        if individual_rose == rose_finding:
            cytology_text = f"Preliminary cytology reported as adequate and suggestive of {rose_finding}"
        else:
            cytology_text = individual_rose

        entry = f"""{station}:
Size/Appearance: ≥10 mm on CT and {appearance}.
Sampling: {passes} EBUS-guided TBNA biopsies obtained.
ROSE: {cytology_text}.
"""
        block += entry + "\n"
    return block.strip()

def generate_dataset():
    dataset = []
    
    for _ in range(NUM_SAMPLES):
        # A. Randomly select variables
        age = random.choice(data_pool["age"])
        gender_tup = random.choice(data_pool["gender_tuple"])
        attending = random.choice(data_pool["attending"])
        referring = random.choice(data_pool["referring"])
        
        # Clinical Scenario Logic
        scenario = random.choice(data_pool["clinical_scenario"])
        indication = scenario["indication"]
        pre_dx_code = scenario["pre_dx_code"]
        pre_dx_text = scenario["pre_dx_text"]
        rose_finding = scenario["rose_finding"]
        node_appearance = scenario["node_appearance"]
        
        # Procedure Details
        aspiration_scope = random.choice(data_pool["aspiration_scope"])
        bal_loc = random.choice(data_pool["bal_location"])
        
        # Fluid Logic (Instilled > Returned)
        fluid_in = random.choice([30, 40, 50, 60, 100])
        fluid_out = random.randint(10, fluid_in - 5)
        
        # Station Logic
        stations_list = random.choice(data_pool["stations_list"])
        stations_joined = ", ".join(stations_list)
        node_details_block = generate_node_block(stations_list, rose_finding, node_appearance)
        
        # Formatting helpers
        if "RML" in bal_loc: bal_short_loc = "RML"
        elif "LUL" in bal_loc: bal_short_loc = "LUL"
        elif "RLL" in bal_loc: bal_short_loc = "RLL"
        else: bal_short_loc = "Target Segment"

        rose_short = "Granulomas" if "Granuloma" in rose_finding else "Malignancy" if "Malignant" in rose_finding else "Reactive"

        # B. Generate Prompt
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_tup[1], 
            gender_long=gender_tup[0],
            attending=attending,
            indication=indication,
            rose_short=rose_short,
            stations_joined=stations_joined,
            bal_short_loc=bal_short_loc,
            pre_dx_code=pre_dx_code
        )
        
        # C. Generate Completion
        completion = note_template.format(
            note_id=NOTE_ID,
            age=age,
            gender_long=gender_tup[0],
            referring=referring,
            indication=indication,
            pre_dx_code=pre_dx_code,
            pre_dx_text=pre_dx_text,
            rose_finding=rose_finding,
            num_nodes=len(stations_list),
            attending=attending,
            aspiration_scope=aspiration_scope,
            node_details_block=node_details_block,
            bal_loc=bal_loc,
            fluid_in=fluid_in,
            fluid_out=fluid_out,
            stations_joined=stations_joined,
            bal_short_loc=bal_short_loc,
            rose_short=rose_short
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