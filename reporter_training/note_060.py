import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_060"
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
    "age": ["28", "32", "35", "41", "46", "52", "59"],
    "gender_tuple": [("female", "F"), ("male", "M")],
    "attending": ["Dr. Smith", "Dr. Chen", "Dr. Rodriguez", "Dr. Patel", "Dr. Ingraham"],
    
    "indication_data": [
        {"ind": "lung infiltrates and possible sarcoid", "dx": "R91.8", "dx_desc": "Other nonspecific abnormal finding of lung field"},
        {"ind": "mediastinal adenopathy and pulmonary nodules", "dx": "R59.1", "dx_desc": "Generalized enlarged lymph nodes"},
        {"ind": "persistent cough and hilar adenopathy", "dx": "D86.0", "dx_desc": "Sarcoidosis of lung"},
        {"ind": "abnormal CT showing ground glass opacities", "dx": "J84.9", "dx_desc": "Interstitial pulmonary disease, unspecified"},
    ],

    # Mapped locations for Radial EBUS to ensure anatomical accuracy
    # Format: (Lobe, Segment Name, Segment Code)
    "lesion_locations": [
        ("LLL", "Posterior-Basal Segment of LLL", "LB10"),
        ("RUL", "Apical Segment of RUL", "RB1"),
        ("LUL", "Apico-posterior Segment of LUL", "LB1+2"),
        ("RLL", "Superior Segment of RLL", "RB6"),
    ],

    "bal_locations": [
        "Lateral Segment of RML (RB4) and Medial Segment of RML (RB5)",
        "Lingula Superior (LB4) and Inferior (LB5)",
        "RUL Apical Segment (RB1)",
        "RLL Superior Segment (RB6)",
    ],

    "ebbx_locations": [
        "RUL Carina (RC1), RML Carina (RC2), and LUL Lingula Carina (Lc1)",
        "RUL Carina (RC1) and RLL Carina (RC6)",
        "LUL Carina (LC1/2) and LLL Carina (LC6)",
        "Main Carina and RML Carina (RC2)",
    ],

    # Node Stations for EBUS
    "target_nodes": [
        {"station": "Station 7", "name": "Subcarinal"},
        {"station": "Station 4R", "name": "Right Lower Paratracheal"},
        {"station": "Station 4L", "name": "Left Lower Paratracheal"},
    ],

    "elastography_findings": [
        {"type": "Type 2", "desc": "mixed soft and stiff regions", "interp": "heterogeneous and indeterminate appearance"},
        {"type": "Type 3", "desc": "predominantly stiff (blue)", "interp": "suspicious for malignancy or granuloma"},
    ],
    
    "benign_nodes": [
        "Station 11Rs", "Station 11L", "Station 10R", "Station 4L"
    ]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
note_template = """INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT
DATE OF PROCEDURE: [Date] CC Referred Physician: {ref_md}

INDICATION FOR OPERATION The patient is a {age}-year-old {gender_long} who presents with {indication}.
The nature, purpose, risks, benefits, and alternatives to Bronchoscopy were discussed with the patient in detail.
The patient indicated a wish to proceed with surgery and informed consent was signed.

CONSENT Obtained before the procedure.
Indications, potential complications, and alternatives were discussed with the patient or surrogate.
PREOPERATIVE DIAGNOSIS

{dx_code} {dx_desc}

POSTOPERATIVE DIAGNOSIS

{dx_code} {dx_desc}

PROCEDURE

31899 Unlisted Procedure (Trach Change with Mature Tract or Procedure NOS) 
31645 Therapeutic aspiration initial episode 
31624 Dx bronchoscope/lavage (BAL) 
31625 Endobronchial Biopsy(s) 
31628 TBBX single lobe 
31652 EBUS sampling 1 or 2 nodes 
31654 Radial EBUS for peripheral lesion 
76982 Ultrasound Elastography, First Target Lesion 
76983 Ultrasound Elastography, Additional Targets 

ATTENDING {attending}

ANESTHESIA General Anesthesia 

MONITORING Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.
INSTRUMENTATION Flexible Therapeutic Bronchoscope, Linear EBUS, Radial EBUS.

ESTIMATED BLOOD LOSS None 

COMPLICATIONS None 

PROCEDURE IN DETAIL After the successful induction of anesthesia, a timeout was performed confirming the patient's name, procedure type, and procedure location.
Patient Position: Supine.

Initial Airway Inspection: NBI was used to assess the airway and nodular changes were noted.
Therapeutic Aspiration: Successful therapeutic aspiration was performed to clean out the Right Mainstem, Bronchus Intermedius, and Left Mainstem from mucus.
Bronchoalveolar Lavage (BAL): Bronchial alveolar lavage was performed at the {bal_loc}.
Instilled 60 cc of NS, suction returned with 20 cc of NS.
Samples were sent for Cell Count, Microbiology (Cultures/Viral/Fungal), and Cytology.
Endobronchial Biopsy: Endobronchial biopsy was performed at {ebbx_loc}.
Lesions were successfully removed and samples sent for Pathology.

Radial EBUS & Transbronchial Biopsy: Radial EBUS was performed to confirm that the location of the lesion in the {lesion_lobe} is concentric.
The following features were noted: Continuous margin; no vessels were noted.
Transbronchial biopsy was performed with alligator forceps at the {lesion_segment} ({lesion_code}).
Total 6 samples were collected and sent for Pathology.

EBUS STAGING Indications: Diagnostic

Technique: All lymph node stations were assessed.
Only those 5 mm or greater in short axis were sampled.
Lymph node sizing was performed by EBUS and sampling by transbronchial needle aspiration was performed using 22-gauge Needle, 19-gauge Needle, and Cryoprobe 1.1mm.
Lymph Nodes Inspected: 4R, 4L, 7, 10R, 10L, 11Rs, 11Ri, 11L.
Lymph Nodes Evaluated & Sampled:

{node_station} ({node_name}): The node was ≥ 10 mm on CT.
Endobronchial ultrasound (EBUS) elastography was performed to assess lymph node stiffness and tissue characteristics.
The target lymph node demonstrated a {elas_type} elastographic pattern with {elas_desc}.
Given this {elas_interp}, TBNA was directed at representative areas.
The lymph node was photographed and the site was sampled;
8 endobronchial ultrasound guided transbronchial biopsies were performed with samples obtained.

{benign_node_1}: The lymph node was < 10 mm on CT. Endobronchial ultrasound (EBUS) elastography was performed;
the node demonstrated a Type 1 elastographic pattern, predominantly soft (green/yellow), suggesting a reactive or benign process.
The site was not sampled as it was not clinically indicated.

{benign_node_2}: The lymph node was < 10 mm on CT. Endobronchial ultrasound (EBUS) elastography was performed;
the node demonstrated a Type 1 elastographic pattern, predominantly soft (green/yellow), suggesting a reactive or benign process.
The site was not sampled as it was not clinically indicated.

Conclusion: The patient tolerated the procedure well.
There were no immediate complications. At the conclusion of the operation, the patient was extubated in the operating room and transported to the recovery room in stable condition.
SPECIMENS

EBBX, TBBX
BAL
{node_station} - TBCBX, TBNA 

IMPRESSION/PLAN

{age}-year-old {gender_long} with {indication}.

Follow up in clinic.
"""

prompt_styles = [
    # Style 1: Telegraphic
    "Pt {age}{gender_short}, {indication}. Performed BAL {bal_short}, EBBX {ebbx_short}. Radial EBUS {lesion_lobe} lesion, bx {lesion_code}. EBUS staged {node_station} ({elas_type}), others benign.",
    
    # Style 2: Dictation
    "Please generate an IP op note for a {age} year old {gender_long} with {indication}. We did a BAL at the {bal_short} and EBBX at {ebbx_short}. Used radial EBUS for a {lesion_lobe} lesion, taking biopsies. Staged mediastinum, sampled {node_station} which was {elas_type}, skipped the smaller nodes.",
    
    # Style 3: Sloppy / Quick
    "{age}yo {gender_short} {indication}. Full IP workup. BAL {bal_short}, EBBX. Radial EBUS to {lesion_lobe} ({lesion_code}) - concentric. EBUS TBNA {node_station} - elastography showed {elas_desc}. No comps.",
    
    # Style 4: Billing Focus
    "Procedures: 31624 (BAL {bal_short}), 31625 (EBBX), 31654 (Radial EBUS {lesion_lobe}), 31652 (EBUS TBNA {node_station}). Dx: {dx_code}. Elastography performed on {node_station} and benign nodes.",
    
    # Style 5: Structured
    "Patient: {age} {gender_short}\nIndication: {indication}\nProcedures: BAL, EBBX, Radial EBUS ({lesion_lobe}), Linear EBUS ({node_station})\nFindings: {node_station} {elas_type}, {lesion_lobe} lesion concentric."
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
        attending = random.choice(data_pool["attending"])
        ref_md = random.choice(["Dr. Jones", "Self", "Dr. Adams", "Dr. Lee"])
        
        # Clinical Scenario
        ind_data = random.choice(data_pool["indication_data"])
        
        # Anatomical Targets
        lesion_info = random.choice(data_pool["lesion_locations"]) # (Lobe, Seg Name, Seg Code)
        bal_loc = random.choice(data_pool["bal_locations"])
        ebbx_loc = random.choice(data_pool["ebbx_locations"])
        
        # Node Staging
        target_node = random.choice(data_pool["target_nodes"])
        elastography = random.choice(data_pool["elastography_findings"])
        
        # Select 2 distinct benign nodes
        benign_sample = random.sample(data_pool["benign_nodes"], 2)
        
        # Shorteners for prompts
        bal_short = bal_loc.split('(')[0].strip()
        ebbx_short = "multiple carinas"
        
        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, gender_short=gender_tup[1], gender_long=gender_tup[0],
            indication=ind_data["ind"],
            dx_code=ind_data["dx"],
            bal_short=bal_short,
            ebbx_short=ebbx_short,
            lesion_lobe=lesion_info[0],
            lesion_code=lesion_info[2],
            node_station=target_node["station"],
            elas_type=elastography["type"],
            elas_desc=elastography["desc"]
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            age=age, gender_long=gender_tup[0],
            indication=ind_data["ind"],
            dx_code=ind_data["dx"],
            dx_desc=ind_data["dx_desc"],
            attending=attending,
            ref_md=ref_md,
            bal_loc=bal_loc,
            ebbx_loc=ebbx_loc,
            lesion_lobe=lesion_info[0],
            lesion_segment=lesion_info[1],
            lesion_code=lesion_info[2],
            node_station=target_node["station"],
            node_name=target_node["name"],
            elas_type=elastography["type"],
            elas_desc=elastography["desc"],
            elas_interp=elastography["interp"],
            benign_node_1=benign_sample[0],
            benign_node_2=benign_sample[1]
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