import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_281"
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
    "age": ["45", "52", "58", "61", "64", "69", "73", "77", "82"],
    "gender_tuple": [("female", "F"), ("male", "M")],
    "doctor": ["Ingraham", "Bowers", "Chen", "Smith", "Miller", "Jones", "Doe", "Patel", "Weiss"],
    "indication": [
        "lymphadenopathy", 
        "mediastinal adenopathy", 
        "enlarged mediastinal lymph nodes", 
        "hilar adenopathy",
        "abnormal CT chest findings"
    ],
    "diagnosis_code": ["R59.0 Localized enlarged lymph nodes", "R59.1 Generalized enlarged lymph nodes"],
    
    # BAL Locations
    "bal_location": [
        "Lateral Segment of RML (RB4)",
        "Medial Segment of RML (RB5)",
        "Apical Segment of RUL (RB1)",
        "Superior Segment of LLL (LB6)",
        "Anterior Segment of LUL (LB3)"
    ],
    
    # Lymph Node Stations (for sampling)
    "stations": ["4R", "4L", "7", "11L", "11R", "10R", "10L"],
    
    # Node Descriptions mapping to Station names
    "station_desc": {
        "4R": "4R (lower paratracheal)",
        "4L": "4L (lower paratracheal)",
        "7": "7 (subcarinal)",
        "11L": "11L (interlobar)",
        "11R": "11R (interlobar)",
        "10R": "10R (hilar)",
        "10L": "10L (hilar)"
    },

    # Elastography Patterns (Logic: Type -> Description -> Implication)
    "elastography_types": [
        {
            "type": "Type 1",
            "desc": "predominantly soft (green/yellow)",
            "implication": "suggesting a reactive or benign process. Despite the benign appearance, TBNA was performed to confirm the absence of malignancy"
        },
        {
            "type": "Type 2",
            "desc": "mixed soft and stiff regions",
            "implication": "Given this heterogeneous and indeterminate appearance, TBNA was directed at representative areas to ensure comprehensive sampling"
        },
        {
            "type": "Type 3",
            "desc": "predominantly stiff (blue)",
            "implication": "suggesting a pathologic or malignant process. TBNA was directed at the stiffest areas to maximize diagnostic yield"
        }
    ],
    
    # CT sizes
    "ct_sizes": ["< 10 mm", "=> 10 mm", "measured 12x14 mm", "measured 8x9 mm"],
    
    # BAL Fluid returns
    "bal_return": [
        ("40 cc", "17 cc"),
        ("50 cc", "25 cc"),
        ("60 cc", "30 cc"),
        ("30 cc", "12 cc")
    ]
}

# ==========================================
# 3. TEMPLATES
# ==========================================

# Helper function to generate a specific node site paragraph
def get_node_paragraph(site_num, station_key, ct_size, elasto_data):
    return f"""Site {site_num}: The {data_pool['station_desc'][station_key]} node was {ct_size} on CT and Metabolic activity unknown or PET-CT scan unavailable. The lymph node was photographed. The site was sampled. 5 endobronchial ultrasound guided transbronchial biopsies were performed with samples obtained. Endobronchial ultrasound (EBUS) elastography was performed to assess lymph node stiffness and tissue characteristics. The target lymph node demonstrated a {elasto_data['type']} elastographic pattern, {elasto_data['desc']}, {elasto_data['implication']}."""

note_template = """NOTE_ID:  {note_id} SOURCE_FILE: {note_id}.txt
DATE OF PROCEDURE: [REDACTED]

CC Referred Physician:  {doctor}, Referred
No address on file

INDICATION FOR OPERATION:  [REDACTED] is a {age} year old {gender_long} who presents with {indication}.  The nature, purpose, risks, benefits and alternatives to Bronchoscopy were discussed with the patient in detail.  Patient indicated a wish to proceed with surgery and informed consent was signed.

CONSENT : Obtained before the procedure. Its indications and potential complications and alternatives were discussed with the patient or surrogate. The patient or surrogate read and signed the provided consent form / provided consent over the phone. The consent was witnessed by an assisting medical professional.

PREOPERATIVE DIAGNOSIS: {diagnosis}

POSTOPERATIVE DIAGNOSIS:  {diagnosis}

PROCEDURE:  
31645 Therapeutic aspiration initial episode
31624 Dx bronchoscope/lavage (BAL)     
31652 EBUS sampling 1 or 2 nodes
31653 EBUS sampling 3 or more nodes  
76981 Ultrasound Elastography, Parenchyma of Organ
76982 Ultrasound Elastography, First Target Lesion
76983 Ultrasound Elastography, Additional Targets 
76983 Ultrasound Elastography, Additional Target 2

22 Substantially greater work than normal (i.e., increased intensity, time, technical difficulty of procedure, and severity of patient's condition, physical and mental effort required)

IP UCSD CODE MOD DETAILS: 
Unusual Procedure:
This patient required elastography of {num_nodes} nodes. This resulted in >50% increased work due to Time, Technical difficulty of procedure, and Physical and mental effort required. Apply to: 76981 Ultrasound Elastography, Parenchyma of Organ
76982 Ultrasound Elastography, First Target Lesion
76983 Ultrasound Elastography, Additional Targets 

ANESTHESIA: 
General Anesthesia

MONITORING : Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.

INSTRUMENT : 
Flexible Therapeutic Bronchoscope
Linear EBUS 

ESTIMATED BLOOD LOSS:   Minimum

COMPLICATIONS:    None

PROCEDURE IN DETAIL:
After the successful induction of anesthesia, a timeout was performed (confirming the patient's name, procedure type, and procedure location).  All procedure related images were saved and archived in Media folder on Onedrive behind UCSD firewall, relevant images are also uploaded to PACS system or in the media section of the patient's chart. 

PATIENT POSITION: . 

Initial Airway Inspection Findings:

The endotracheal tube is in good position.
Pharynx: Not assessed due to bronchoscopy introduction through ETT.
Larynx: Not assessed due to bronchoscopy introduction through ETT.
Vocal Cords: Not assessed due to bronchoscopy introduction through ETT.
Trachea: Distal 1/3 normal.
Main Carina: Sharp
Right Lung Proximal Airways: Normal anatomic branching to segmental level.  No evidence of mass, lesions, bleeding or other endobronchial pathology.
Left Lung Proximal Airways: Normal anatomic branching to segmental level.  No evidence of mass, lesions, bleeding or other endobronchial pathology.
Mucosa: Normal.
Secretions: Minimal, thin, and clear.  

Successful therapeutic aspiration was performed to clean out the Trachea (Distal 1/3), Right Mainstem, Bronchus Intermedius , Left Mainstem, Carina, RUL Carina (RC1), RML Carina (RC2), LUL Lingula Carina (Lc1), and Left Carina (LC2) from mucus. 

EBUS-Findings
Indications: Diagnostic and Staging
Technique:
All lymph node stations were assessed. Only those 5 mm or greater in short axis were sampled.

Lymph node sizing was performed by EBUS and sampling by transbronchial needle aspiration was performed using 22-gauge Needle.

Lymph Nodes/Sites Inspected: {inspected_list}

No immediate complications

Endobronchial ultrasound (EBUS) elastography was performed to assess lymph node stiffness and tissue characteristics. Elastography provided a semi-quantitative classification (Type 1–3), which was used to guide biopsy site selection and sampling strategy. 

Lymph Nodes Evaluated:
{site_1_paragraph}

{site_2_paragraph}

{site_3_paragraph}

Bronchial alveolar lavage was performed at {bal_loc}.  Instilled {instilled} of NS, suction returned with {returned} of NS.  Samples sent for Cell Count, Microbiology (Cultures/Viral/Fungal), and Cytology.

The patient tolerated the procedure well.  There were no immediate complications.  At the conclusion of the operation, the patient was extubated in the operating room and transported to the recovery room in stable condition. 

SPECIMEN(S): 
- {bal_short} BAL (cell count, micro, cyto)
- Station {sampled_stations_str} TBNA (cyto, flow cytometry)

IMPRESSION/PLAN: [REDACTED] is a {age} year old {gender_long} who presents for bronchoscopy for evaluation of {indication}. Patient underwent endobronchial ultrasound with transbronchial needle aspirations on the {sampled_stations_str} lymph node stations. Samples were sent for cytology and flow cytometry. The patient tolerated the procedure well and there were no immediate complications.

--Post procedure CXR
--Follow up TBNA and BAL results
--Continued care per primary team
"""

prompt_styles = [
    # Style 1: Telegraphic
    "EBUS/Elastography note. {age}{gender_short}, Dr. {doctor}. Indication: {indication}. Sampled {sampled_stations_str}. BAL {bal_short}. Mod 22 for extra work.",
    
    # Style 2: Dictation
    "Please generate an operative report for Dr. {doctor}. Patient is a {age}-year-old {gender_long} with {indication}. Performed EBUS with elastography on stations {sampled_stations_str} and BAL at {bal_loc}. Note increased difficulty due to elastography.",
    
    # Style 3: Sloppy / Quick
    "{age}yo {gender_short} ebus elastography. {sampled_stations_str} nodes sampled. {bal_short} bal. dx {diagnosis_short}. dr {doctor} ref.",
    
    # Style 4: Billing Focus
    "Codes 31653, 76981-76983 (Mod 22). {age} {gender_short}. Dx R59.0. EBUS sampling {sampled_stations_str} with elastography mapping.",
    
    # Style 5: Structured
    "Patient: {age} {gender_short}\nReferral: {doctor}\nProcedure: EBUS with Elastography + BAL\nNodes: {sampled_stations_str}\nFindings: Mixed elastography types recorded."
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
        doctor = random.choice(data_pool["doctor"])
        indication = random.choice(data_pool["indication"])
        diagnosis = random.choice(data_pool["diagnosis_code"])
        diagnosis_short = diagnosis.split(" ")[0]
        
        # BAL details
        bal_loc = random.choice(data_pool["bal_location"])
        bal_short = bal_loc.split(" (")[0].replace("Segment of ", "") # e.g., Lateral RML
        instilled, returned = random.choice(data_pool["bal_return"])
        
        # Node Logic: Select 3 distinct nodes for the 3 sites in the template
        selected_nodes = random.sample(data_pool["stations"], 3)
        
        # Generate Inspection List (just the names formatted)
        inspected_list_raw = [data_pool["station_desc"][n] for n in selected_nodes]
        inspected_list = "\n".join(inspected_list_raw)
        
        # Generate Paragraphs for each site
        site_paragraphs = []
        for i, node in enumerate(selected_nodes):
            ct_size = random.choice(data_pool["ct_sizes"])
            elasto_data = random.choice(data_pool["elastography_types"])
            para = get_node_paragraph(i+1, node, ct_size, elasto_data)
            site_paragraphs.append(para)
            
        sampled_stations_str = ", ".join(selected_nodes[:-1]) + ", and " + selected_nodes[-1]
        
        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_tup[1], 
            gender_long=gender_tup[0],
            doctor=doctor, 
            indication=indication,
            diagnosis_short=diagnosis_short,
            sampled_stations_str=sampled_stations_str,
            bal_loc=bal_loc,
            bal_short=bal_short
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            age=age, 
            gender_long=gender_tup[0], 
            doctor=doctor,
            indication=indication,
            diagnosis=diagnosis,
            num_nodes=len(selected_nodes),
            inspected_list=inspected_list,
            site_1_paragraph=site_paragraphs[0],
            site_2_paragraph=site_paragraphs[1],
            site_3_paragraph=site_paragraphs[2],
            bal_loc=bal_loc,
            instilled=instilled,
            returned=returned,
            bal_short=bal_short,
            sampled_stations_str=sampled_stations_str
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