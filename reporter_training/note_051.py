import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_051"
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
    "age": ["22", "27", "34", "41", "55", "63", "72", "81"],
    "gender_tuple": [("female", "F"), ("male", "M")],
    "indication": [
        "lung infiltrates", 
        "persistent atelectasis", 
        "right middle lobe consolidation", 
        "suspected pneumonia", 
        "mucus plugging on CT"
    ],
    "diagnosis_code": ["J98.09", "J18.9", "J98.4", "J84.10"],
    
    # Logic grouping: Anatomical location + Specific Segments + Abbreviation
    "anatomy_group": [
        {
            "region": "Right Middle Lobe", 
            "segments": "Lateral Segment of the RML (RB4) and the Medial Segment of the RML (RB5)", 
            "abbr": "RML",
            "airway_finding_loc": "Right Mainstem, Bronchus Intermedius, and Right Middle Lobe"
        },
        {
            "region": "Right Lower Lobe", 
            "segments": "Superior Segment (RB6) and Posterior Basal Segment (RB10)", 
            "abbr": "RLL",
            "airway_finding_loc": "Right Mainstem, Bronchus Intermedius, and Right Lower Lobe"
        },
        {
            "region": "Left Upper Lobe", 
            "segments": "Apico-posterior Segment (LB1+2) and Anterior Segment (LB3)", 
            "abbr": "LUL",
            "airway_finding_loc": "Left Mainstem and Left Upper Lobe"
        },
        {
            "region": "Lingula", 
            "segments": "Superior Lingular Segment (LB4) and Inferior Lingular Segment (LB5)", 
            "abbr": "Lingula",
            "airway_finding_loc": "Left Mainstem and Lingular Bronchus"
        }
    ],
    
    "finding_type": [
        "Mucus and mucus plugs", 
        "Thick, copious secretions", 
        "Purulent secretions", 
        "Mucoid impaction"
    ],
    
    # Logic grouping: Instilled vs Returned fluids
    "fluid_vols": [
        ("60", "20"), 
        ("100", "40"), 
        ("120", "50"), 
        ("50", "15")
    ],
    
    "specimens": [
        "Microbiology/Viral/Fungal", 
        "Routine Culture and Gram Stain", 
        "Cytology and Microbiology", 
        "AFB, Fungal, and Routine Culture"
    ]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
note_template = """NOTE_ID: {note_id}
SOURCE_FILE: {note_id}.txt

INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: [Date]

INDICATION FOR OPERATION [REDACTED] is a {age}-year-old {gender_long} who presents with {indication}.

CONSENT The nature, purpose, risks, benefits, and alternatives to Bronchoscopy were discussed with the patient in detail.
The patient indicated a wish to proceed with surgery and informed consent was signed.

PREOPERATIVE DIAGNOSIS

{dx_code} Other diseases of bronchus, not elsewhere classified 

POSTOPERATIVE DIAGNOSIS

{dx_code} Other diseases of bronchus, not elsewhere classified 

PROCEDURE

Therapeutic aspiration tracheobronchial tree, initial episode (31645)

Bronchoscopy with bronchoalveolar lavage (BAL) (31624) 

ANESTHESIA General Anesthesia 

ESTIMATED BLOOD LOSS None 

COMPLICATIONS None 

PROCEDURE IN DETAIL After the successful induction of anesthesia, a timeout was performed (confirming the patient's name, procedure type, and procedure location).

Initial Airway Inspection Findings: {finding_type} were identified in the {airway_loc}.

Therapeutic Aspiration Successful therapeutic aspiration was performed to clean out the {airway_loc} from {finding_type_lower}.

Bronchoalveolar Lavage (BAL) Bronchial alveolar lavage was performed at the {segments}.

Instilled {vol_in} cc of NS, suction returned with {vol_out} cc of NS.

Samples sent for {specimens}.

The patient tolerated the procedure well. There were no immediate complications.

At the conclusion of the operation, the patient was extubated in the operating room and transported to the recovery room in stable condition.

SPECIMEN(S)

{abbr} BAL ({specimens}) 

IMPRESSION / PLAN

[REDACTED] is a {age}-year-old {gender_long} who presents for bronchoscopy for {indication}.

Therapeutic aspiration performed for mucus plugging.

{abbr} BAL performed for microbiology.

Follow up in clinic.
"""

prompt_styles = [
    # Style 1: Telegraphic
    "Write an op note for a {age}yo {gender_short}. Indication: {indication}. Found {finding_type_lower} in {abbr}. Did therapeutic aspiration and BAL of {abbr}. Instilled {vol_in}cc/returned {vol_out}cc. Sent for {specimens}.",
    
    # Style 2: Dictation
    "Please generate a bronchoscopy report. The patient is a {age}-year-old {gender_long} with {indication}. Under general anesthesia, we found {finding_type_lower} in the {airway_loc}. We suctioned the airways and performed a BAL of the {segments}. We used {vol_in} cc of saline and got back {vol_out} cc. Specimens sent for {specimens}.",
    
    # Style 3: Sloppy / Quick
    "{age} {gender_short} bronchoscopy. dx {dx_code} {indication}. {finding_type_lower} seen in {abbr}, suctioned out. lavage done {abbr} ({vol_in}in/{vol_out}out). samples to lab for {specimens}.",
    
    # Style 4: Billing Focus
    "Procedure codes 31645 (Therapeutic Aspiration) and 31624 (BAL). Dx {dx_code}. Patient {age} {gender_short}. Findings: {finding_type} in {airway_loc}. Lavage site: {segments}. Specimen: {specimens}.",
    
    # Style 5: Structured
    "Patient: {age} {gender_short}\nIndication: {indication}\nFindings: {finding_type} in {airway_loc}\nProcedure: Aspiration and BAL ({abbr})\nFluids: {vol_in}cc in, {vol_out}cc return\nSpecimens: {specimens}"
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
        indication = random.choice(data_pool["indication"])
        dx_code = random.choice(data_pool["diagnosis_code"])
        
        # Select anatomy group to keep location logic consistent
        anatomy = random.choice(data_pool["anatomy_group"])
        
        finding_type = random.choice(data_pool["finding_type"])
        fluid_tup = random.choice(data_pool["fluid_vols"])
        specimens = random.choice(data_pool["specimens"])
        
        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_tup[1], 
            gender_long=gender_tup[0],
            indication=indication,
            dx_code=dx_code,
            finding_type=finding_type,
            finding_type_lower=finding_type.lower(),
            abbr=anatomy["abbr"],
            segments=anatomy["segments"],
            airway_loc=anatomy["airway_finding_loc"],
            vol_in=fluid_tup[0],
            vol_out=fluid_tup[1],
            specimens=specimens
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            age=age, 
            gender_long=gender_tup[0], 
            indication=indication,
            dx_code=dx_code,
            finding_type=finding_type,
            finding_type_lower=finding_type.lower(),
            airway_loc=anatomy["airway_finding_loc"],
            segments=anatomy["segments"],
            vol_in=fluid_tup[0], 
            vol_out=fluid_tup[1],
            specimens=specimens,
            abbr=anatomy["abbr"]
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