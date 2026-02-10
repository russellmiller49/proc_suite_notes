import json
import random
import os
import datetime

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_104"
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
    "age": ["44", "52", "56", "59", "63", "67", "71", "75", "82"],
    "gender_tuple": [("female", "F", "She", "her"), ("male", "M", "He", "his")],
    "ref_physician": [
        "Dr. Anderson", "Dr. Patel", "Dr. Gomez", "Dr. Schmidt", 
        "Dr. Lee", "Dr. Okafor", "Dr. Weiss"
    ],
    "indication": [
        "respiratory failure", 
        "worsening dyspnea and hypoxia", 
        "suspected airway obstruction", 
        "mucus plugging and desaturation"
    ],
    "stent_status": [
        "in good position", 
        "slightly migrated distally but functional", 
        "patent but coated in secretions", 
        "in satisfactory position"
    ],
    "tissue_condition": [
        "significant necrosis/granulation tissue", 
        "moderate granulation tissue", 
        "mild tissue overgrowth", 
        "severe circumferential granulation"
    ],
    "balloon_type": [
        "8-9-10 Elation balloon", 
        "10-11-12 Elation balloon", 
        "6-7-8 CRE balloon"
    ],
    "dilation_target": [
        ("8 mm and to 9 mm", "9 mm"),
        ("10 mm and to 11 mm", "11 mm"),
        ("6 mm and to 7 mm", "7 mm")
    ],
    "bal_volumes": [
        ("40", "25"), ("50", "30"), ("60", "35"), ("30", "15"), ("100", "60")
    ],
    "inflation_time": ["30", "45", "60", "90"],
    "date_offset": range(-10, 0) # Days ago
}

# ==========================================
# 3. TEMPLATES
# ==========================================
# Template with placeholders for dynamic data
note_template = """NOTE_ID: {note_id}
SOURCE_FILE: {note_id}.txt

INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: {proc_date}
CC Referred Physician: {ref_physician}

INDICATION FOR OPERATION
The patient is a {age}-year-old {gender_long} who presents with {indication}. The nature, purpose, risks, benefits, and alternatives to Bronchoscopy were discussed with the patient in detail.

CONSENT
Obtained before the procedure. Indications, potential complications, and alternatives were discussed.

PREOPERATIVE DIAGNOSIS
J96.90 Respiratory Failure

POSTOPERATIVE DIAGNOSIS
J96.90 Respiratory Failure

PROCEDURE
31646 Therapeutic aspiration subsequent episodes
31622 Dx bronchoscope/cell washing
31624 Dx bronchoscope/lavage (BAL)
31630 Balloon dilation
50 Bilateral Procedures

ANESTHESIA
General Anesthesia

MONITORING
Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.

INSTRUMENTATION
Flexible Therapeutic Bronchoscope

ESTIMATED BLOOD LOSS
Minimum

COMPLICATIONS
None

PROCEDURE IN DETAIL
After the successful induction of anesthesia, a timeout was performed confirming the patient's name, procedure type, and procedure location.

Initial Airway Inspection
The airway was inspected from above the tracheostomy tube. The vocal cords were normal appearing. The tracheostomy tube was in good position and the balloon was inflated. Secretions were suctioned and lidocaine was applied. The airway was inspected via the tracheostomy.

Right Lung:
The right-sided stent was {stent_status}. There was {tissue_condition} around the suture site and medially along the transplanted lung, covering the orifice of the right middle lobe. The right lower lobe was preserved. The portion of the right upper lobe takeoff visible through the stent appeared intact, though an area around 9 o'clock appeared potentially injured.

Left Lung:
The left lung anastomosis site had similar medial necrosis and granulation tissue. The lingula was patent but obscured with necrosis. The left upper lobe anterior segment had some necrosis, while the left upper lobe proper was preserved. The left lower lobe was preserved.

Interventions

Endobronchial Biopsy (CPT 31625):
Performed at the RML Carina (RC2). The lesion was successfully removed and samples were sent for pathology.

Balloon Dilation (CPT 31630):
Performed at the RML Carina (RC2). An {balloon_type} was used to perform dilation to {dilation_size_text}. Total of 2 inflations were performed with a dilation time of {inflation_time} seconds each.

Bronchoalveolar Lavage (CPT 31624):
Performed at the Lateral Segment of RML (RB4) and Medial Segment of RML (RB5). Instilled {bal_in} cc of NS, suction returned with {bal_out} cc of NS. Samples were sent for Cell Count, Microbiology (Cultures/Viral/Fungal), and Cytology.

Therapeutic Aspiration (CPT 31646):
Successful therapeutic aspiration was performed to clean mucus from the Trachea (Middle 1/3), Trachea (Distal 1/3), Right Mainstem, Bronchus Intermedius, Left Mainstem, Carina, RUL Carina (RC1), RML Carina (RC2), LUL Lingula Carina (Lc1), and Left Carina (LC2).

The patient tolerated the procedure well. There were no immediate complications. At the conclusion of the operation, the patient was extubated in the operating room and transported to the recovery room in stable condition.

SPECIMENS
Right middle lobe BAL
Right middle lobe EBBX

IMPRESSION / PLAN
{age}-year-old {gender_long} who presented for bronchoscopy for {indication} and airway dilation.
Follow-up bronchoscopic lab work.
Follow-up bronchoscopy planned for later this week or early next week.
"""

# 5 Distinct Prompt Styles
prompt_styles = [
    # Style 1: Telegraphic / Brief
    "Generate Op Report. {age}{gender_short}, Ref: {ref_physician}. Indication: {indication}. Stents checked: {stent_status} but {tissue_condition}. Interventions: Biopsy RML, Dilation ({balloon_type} to {max_dilation}), BAL ({bal_in}cc), extensive aspiration. No comps.",

    # Style 2: Dictation Style
    "Please write a procedure note for a {age}-year-old {gender_long} referred by {ref_physician}. The patient is in {indication}. Under general anesthesia, we inspected the airway. Right stent was {stent_status}. We found {tissue_condition}. We performed balloon dilation using an {balloon_type} for {inflation_time} seconds, RML biopsy, and BAL with {bal_in} cc saline.",

    # Style 3: Sloppy / Handoff
    "Bronch report for {age}yo {gender_long}. dx j96.90. saw {tissue_condition} at anastomosis. did dilation with {balloon_type} to {max_dilation}. washed rml ({bal_out}cc return). aspirated all airways. pt tolerated well. ref {ref_physician}.",

    # Style 4: Billing & Coding Focus
    "Procedure Codes: 31646, 31622, 31624, 31630. Pt: {age} {gender_short}. Dx: {indication}. Findings: {tissue_condition}. Procedures: Dilation ({balloon_type}, {inflation_time}s), BAL RML, Biopsy RC2. {ref_physician}.",

    # Style 5: Structured Request
    "PATIENT: {age} {gender_short}\nREFERRING: {ref_physician}\nINDICATION: {indication}\nFINDINGS: Right stent {stent_status}, {tissue_condition}.\nINTERVENTIONS:\n- Biopsy RML\n- Dilation ({balloon_type})\n- BAL ({bal_in}cc in / {bal_out}cc out)\n- Aspiration (bilateral)"
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
        gender_long = gender_tup[0]
        gender_short = gender_tup[1]
        
        ref_physician = random.choice(data_pool["ref_physician"])
        indication = random.choice(data_pool["indication"])
        stent_status = random.choice(data_pool["stent_status"])
        tissue_condition = random.choice(data_pool["tissue_condition"])
        
        # Balloon Logic
        balloon_type = random.choice(data_pool["balloon_type"])
        # Match dilation size text to reasonable balloon types or randomize carefully
        # For simplicity in this script, we pick a tuple that loosely matches
        dilation_tup = random.choice(data_pool["dilation_target"])
        dilation_size_text = dilation_tup[0]
        max_dilation = dilation_tup[1]
        inflation_time = random.choice(data_pool["inflation_time"])
        
        # BAL Logic
        bal_tup = random.choice(data_pool["bal_volumes"])
        bal_in = bal_tup[0]
        bal_out = bal_tup[1]
        
        # Date Logic
        days_ago = random.choice(data_pool["date_offset"])
        proc_date = (datetime.date.today() + datetime.timedelta(days=days_ago)).strftime("%m/%d/%Y")
        
        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_short, 
            gender_long=gender_long,
            ref_physician=ref_physician,
            indication=indication,
            stent_status=stent_status,
            tissue_condition=tissue_condition,
            balloon_type=balloon_type,
            max_dilation=max_dilation,
            bal_in=bal_in,
            bal_out=bal_out,
            inflation_time=inflation_time
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            proc_date=proc_date,
            ref_physician=ref_physician,
            age=age,
            gender_long=gender_long,
            indication=indication,
            stent_status=stent_status,
            tissue_condition=tissue_condition,
            balloon_type=balloon_type,
            dilation_size_text=dilation_size_text,
            inflation_time=inflation_time,
            bal_in=bal_in,
            bal_out=bal_out
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