import json
import random
import os
import datetime

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_071"
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
    "age": ["65", "72", "78", "81", "85", "89", "91", "67", "74"],
    "gender_tuple": [("female", "F"), ("male", "M")],
    "indication": [
        "airway stenosis",
        "dyspnea and history of airway obstruction",
        "surveillance of airway stents",
        "worsening shortness of breath",
        "stridor and tracheal stenosis"
    ],
    "diagnosis_code": ["J98.09", "J95.850", "J39.8", "J98.8"],
    "mucus_location": [
        "Right Mainstem, Bronchus Intermedius, and Left Mainstem",
        "distal trachea and both mainstems",
        "Left Lower Lobe and Right Middle Lobe",
        "Right Lower Lobe and carina"
    ],
    "stent_1_size": ["iCAST 7x16", "iCAST 7x22", "iCAST 8x38", "Ultraflex 12x40"],
    "stent_1_loc": ["right lower airway", "left mainstem", "distal trachea", "right mainstem"],
    "stent_2_size": ["iCAST 5x16", "iCAST 6x22", "iCAST 6x16", "None"], # None handles case where only 1 stent exists
    "stent_2_loc": ["right middle lobe airway", "left upper lobe", "right upper lobe", "None"],
    "bal_loc": ["RLL", "LLL", "RML", "LUL", "RUL"],
    "bal_vol_in": ["30", "40", "50", "60"],
    "bal_vol_out": ["10", "15", "20", "25"],
    "biopsy_loc": ["Bronchus Intermedius", "Right Upper Lobe", "Left Lower Lobe", "Carina"],
    "dilation_loc": ["RB2 orifice", "LB1 orifice", "RML orifice", "RUL bronchus"],
    "balloon_size": ["5mm", "6mm", "7mm", "8mm"],
    "balloon_type": ["mustang", "CRE", "Hurricane"],
    "inflation_count": ["2", "3", "4"],
    "inflation_time": ["30", "45", "60"],
    "follow_up_weeks": ["6", "8", "12", "4"]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
# Note: I corrected "year old-year-old" from original to "year-old" for cleanliness, 
# but kept the overall structure identical.

note_template = """NOTE_ID:  {note_id} SOURCE_FILE: {note_id}.txt

INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: {date_str} INDICATION FOR OPERATION [REDACTED] is a {age} year-old {gender_long} who presents with {indication}.

The nature, purpose, risks, benefits and alternatives to Bronchoscopy were discussed with the patient in detail.

PREOPERATIVE DIAGNOSIS

{diagnosis_code} Other diseases of bronchus, not elsewhere classified 

POSTOPERATIVE DIAGNOSIS

{diagnosis_code} Other diseases of bronchus, not elsewhere classified 

PROCEDURE

31645 Therapeutic aspiration initial episode 

31624 Dx bronchoscope/lavage (BAL) 

31625 Endobronchial Biopsy(s) 

31630 Balloon dilation 

ANESTHESIA General Anesthesia 

MONITORING Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.

INSTRUMENT Disposable Bronchoscope 

ESTIMATED BLOOD LOSS None 

COMPLICATIONS None 

PROCEDURE IN DETAIL After the successful induction of anesthesia, a timeout was performed (confirming the patient's name, procedure type, and procedure location).

Initial Airway Inspection Findings: Successful therapeutic aspiration was performed to clean out the {mucus_location} from mucus.

Stents are in good position. The ({stent_1_size}) was noted in the {stent_1_loc}.
{stent_2_sentence}

Bronchoalveolar Lavage: Bronchial alveolar lavage was performed at {bal_loc}.
Instilled {bal_vol_in} cc of NS, suction returned with {bal_vol_out} cc of NS. Samples sent for Microbiology (Cultures/Viral/Fungal).

Endobronchial Biopsy: Endobronchial biopsy was performed at {biopsy_loc}. Two areas were biopsied with NBI guidance.
Samples sent for Microbiology (Cultures/Viral/Fungal) and Pathology.

Balloon Dilation: Balloon dilation was performed at {dilation_loc}.
{balloon_size} {balloon_type} balloon was used to perform dilation to {balloon_size} at the {dilation_loc_short}.
Total {inflation_count} inflations with dilation time of {inflation_time} seconds each.

The patient tolerated the procedure well.
There were no immediate complications. At the conclusion of the operation, the patient was extubated in the operating room and transported to the recovery room in stable condition.

SPECIMEN(S)

EBBX 

BAL {bal_loc} 

IMPRESSION/PLAN

[REDACTED] is a {age} year-old {gender_long} who presents for bronchoscopy for airway narrowing.

f/u in clinic 

f/u in {follow_up_weeks} weeks for bronch evaluation of stent
"""

prompt_styles = [
    # Style 1: Telegraphic / Summary
    "Bronch/BAL/Bx/Dilation note. {age}yo {gender_short}. Indication: {indication}. Stents checked ({stent_1_loc}). BAL {bal_loc}. Bx {biopsy_loc}. Dilation {dilation_loc} using {balloon_size} balloon.",
    
    # Style 2: Dictation Style
    "Please generate an IP op report for a {age} year old {gender_long} presenting with {indication}. We performed therapeutic aspiration, BAL at the {bal_loc}, biopsies at the {biopsy_loc}, and balloon dilation of the {dilation_loc}. Stents were patent.",
    
    # Style 3: Sloppy / Quick Handoff
    "{age} {gender_short} {indication}. cleaned mucus from {mucus_location}. checked stents. lavaged {bal_loc} and biopsied {biopsy_loc}. dilated {dilation_loc} {inflation_count} times.",
    
    # Style 4: Billing / Coding Focus
    "Procedures: 31645, 31624, 31625, 31630. Diagnosis {diagnosis_code}. Patient {age} {gender_short}. Findings: Stents in place. Dilation performed at {dilation_loc} with {balloon_size} balloon.",
    
    # Style 5: Structured Request
    "PATIENT: {age}/{gender_short}\nINDICATION: {indication}\nPROCEDURE: Airway clearance, Stent check, BAL ({bal_loc}), Biopsy ({biopsy_loc}), Dilation ({dilation_loc})\nPLAN: Follow up {follow_up_weeks} weeks."
]

# ==========================================
# 4. GENERATOR LOGIC
# ==========================================
def generate_dataset():
    dataset = []
    
    # Generate a base date for context
    base_date = datetime.date(2026, 2, 9)
    
    for _ in range(NUM_SAMPLES):
        # A. Randomly select variables
        age = random.choice(data_pool["age"])
        gender_tup = random.choice(data_pool["gender_tuple"])
        indication = random.choice(data_pool["indication"])
        diagnosis_code = random.choice(data_pool["diagnosis_code"])
        mucus_location = random.choice(data_pool["mucus_location"])
        
        stent_1_size = random.choice(data_pool["stent_1_size"])
        stent_1_loc = random.choice(data_pool["stent_1_loc"])
        
        # Logic for second stent (sometimes present, sometimes not)
        stent_2_size = random.choice(data_pool["stent_2_size"])
        stent_2_loc = random.choice(data_pool["stent_2_loc"])
        
        if stent_2_size == "None" or stent_2_loc == "None":
            stent_2_sentence = ""
        else:
            stent_2_sentence = f"({stent_2_size}) was noted in the {stent_2_loc}."
            
        bal_loc = random.choice(data_pool["bal_loc"])
        bal_vol_in = random.choice(data_pool["bal_vol_in"])
        bal_vol_out = random.choice(data_pool["bal_vol_out"])
        
        biopsy_loc = random.choice(data_pool["biopsy_loc"])
        
        dilation_loc = random.choice(data_pool["dilation_loc"])
        # Create a short version of dilation loc for the second mention (e.g., "RB2 orifice" -> "RB2")
        dilation_loc_short = dilation_loc.split(" ")[0]
        
        balloon_size = random.choice(data_pool["balloon_size"])
        balloon_type = random.choice(data_pool["balloon_type"])
        inflation_count = random.choice(data_pool["inflation_count"])
        inflation_time = random.choice(data_pool["inflation_time"])
        follow_up_weeks = random.choice(data_pool["follow_up_weeks"])
        
        # Date generation
        date_offset = random.randint(-30, 30)
        date_str = (base_date + datetime.timedelta(days=date_offset)).strftime("%A, %B %d, %Y")

        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_tup[1], 
            gender_long=gender_tup[0],
            indication=indication,
            diagnosis_code=diagnosis_code,
            mucus_location=mucus_location,
            stent_1_loc=stent_1_loc,
            bal_loc=bal_loc,
            biopsy_loc=biopsy_loc,
            dilation_loc=dilation_loc,
            balloon_size=balloon_size,
            inflation_count=inflation_count,
            follow_up_weeks=follow_up_weeks
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            date_str=date_str,
            age=age,
            gender_long=gender_tup[0],
            indication=indication,
            diagnosis_code=diagnosis_code,
            mucus_location=mucus_location,
            stent_1_size=stent_1_size,
            stent_1_loc=stent_1_loc,
            stent_2_sentence=stent_2_sentence,
            bal_loc=bal_loc,
            bal_vol_in=bal_vol_in,
            bal_vol_out=bal_vol_out,
            biopsy_loc=biopsy_loc,
            dilation_loc=dilation_loc,
            dilation_loc_short=dilation_loc_short,
            balloon_size=balloon_size,
            balloon_type=balloon_type,
            inflation_count=inflation_count,
            inflation_time=inflation_time,
            follow_up_weeks=follow_up_weeks
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