import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_073" 
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
    "age": ["19", "24", "29", "33", "41", "52", "67", "74"],
    # Tuple: (Long, Short, Pronoun_Subj, Pronoun_Poss)
    "gender_tuple": [("female", "F", "she", "her"), ("male", "M", "he", "his")],
    "indication": [
        "tracheal stenosis",
        "subglottic stenosis",
        "airway obstruction due to granulation tissue",
        "symptomatic tracheal granulation"
    ],
    "stent_location": [
        "proximal",
        "mid-tracheal",
        "distal"
    ],
    "granulation_loc": [
        "anterior and posterior aspects",
        "circumferential aspects",
        "right lateral and anterior aspects",
        "posterior wall"
    ],
    "mucus_desc": [
        "Mild thick yellow mucus",
        "Copious white frothy secretions",
        "Moderate purulent mucus",
        "Scant clear secretions",
        "Thick inspissated mucus"
    ],
    "cryo_cycles": [
        "3 cycles",
        "4 cycles",
        "5 cycles",
        "2 cycles"
    ],
    "hemostasis_method": [
        "cold saline",
        "diluted epinephrine",
        "topical epinephrine",
        "saline lavage"
    ],
    "aspiration_list": [
        "Trachea (Distal 1/3), Right Mainstem, Bronchus Intermedius, Left Mainstem, Carina",
        "Trachea, RMS, LMS, RUL, and LUL",
        "proximal and distal airways bilaterally",
        "Trachea, Carina, and bilateral mainstems"
    ]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
# Based on note_073.txt
note_template = """NOTE_ID: {note_id}
SOURCE_FILE: {note_id}.txt

INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT
DATE OF PROCEDURE: [Date]
INDICATION FOR OPERATION
[REDACTED] is a {age}-year-old {gender_long} who presents with {indication}.

The nature, purpose, risks, benefits, and alternatives to bronchoscopy were discussed with the patient in detail.
CONSENT Obtained before the procedure. Indications, potential complications, and alternatives were discussed.
The patient wished to proceed and informed consent was obtained.

PREOPERATIVE DIAGNOSIS
J98.09 Other diseases of bronchus, not elsewhere classified

POSTOPERATIVE DIAGNOSIS
J98.09 Other diseases of bronchus, not elsewhere classified
Tracheal stenosis with granulation tissue

PROCEDURE
Therapeutic aspiration, initial episode (31645)
Diagnostic bronchoscopy with brushing (31623)
Destruction of tumor or relief of stenosis by cryotherapy (31641)

ANESTHESIA General Anesthesia

MONITORING Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.

INSTRUMENTATION Flexible Therapeutic Bronchoscope , 2.4mm Cryoprobe.

ESTIMATED BLOOD LOSS Minimum

COMPLICATIONS None

PROCEDURE IN DETAIL
After the successful induction of anesthesia, a timeout was performed confirming the patient's name, procedure type, and procedure location.

Initial Airway Inspection: The laryngeal mask airway (LMA) was in good position.
The pharynx and larynx were not fully assessed due to bronchoscopy introduction through the LMA.

Vocal Cords: Normal without mass/lesions.
Trachea: A tracheal stent was in place with slight granulation tissue noted at the {granulation_loc} of the {stent_location} stent.
{mucus_desc} was observed within the stent.

Right Lung: Proximal airways showed normal anatomic branching to the segmental level.
No evidence of mass, lesions, bleeding, or other endobronchial pathology.
Left Lung: Proximal airways showed normal anatomic branching to the segmental level.
No evidence of mass, lesions, bleeding, or other endobronchial pathology.

Mucosa: Normal.

Therapeutic Aspiration: Successful therapeutic aspiration was performed to clean out mucus from the {aspiration_list}.

Granulation Tissue Destruction (Cryotherapy): The granulation tissue at the {stent_location} stent was treated with the following modalities:

Anterior: The 2.4mm cryoprobe was used to treat the granulation tissue with 30-second freeze-thaw cycles for a total of {cryo_cycles}.
Excellent tissue destruction was noted.

Posterior: The granulation tissue at the posterior trachea was treated with the 2.4mm cryoprobe; tissue was frozen to the probe and removed en bloc with the bronchoscope.

Additional Sampling and Hemostasis: Mucus and secretions were removed from within the stent using a combination of saline flushes and a cytology brush.
Mild oozing/bleeding was noted and treated successfully with {hemostasis_method}.

Conclusion: At the conclusion of the procedure, areas of granulation tissue treatment and the stent were inspected.
The patient tolerated the procedure well. There were no immediate complications.
The patient was extubated in the operating room and transported to the recovery room in stable condition.

SPECIMENS
Tracheal tumor/granulation tissue removed with cryoprobe

IMPRESSION / PLAN
[REDACTED] is a {age}-year-old {gender_long} who presented for bronchoscopy for evaluation of {indication}.
Granulation tissue at the {granulation_loc} of the {stent_location} tracheal stent was treated with cryoprobe, achieving excellent tissue debulking.
Post-procedure CXR to be obtained.

Pending pathology results.

Patient to follow up in outpatient IP clinic to go over results and next steps.
"""

# 5 Distinct Prompt Styles
prompt_styles = [
    # Style 1: Telegraphic
    "Operative note IP. {age}{gender_short}, {indication}. Stent is {stent_location}. Found granulation {granulation_loc} and {mucus_desc}. Did cryo ({cryo_cycles}) and aspiration. Hemostasis w/ {hemostasis_method}.",
    
    # Style 2: Dictation
    "Generate a bronchoscopy report for a {age}-year-old {gender_long} with {indication}. There was a stent in the {stent_location} trachea. We saw {mucus_desc}. Granulation tissue was at the {granulation_loc}. We used cryotherapy for {cryo_cycles} and aspirated the {aspiration_list}.",
    
    # Style 3: Sloppy / Quick
    "{age}yo {gender_short} {indication}. stent {stent_location} w/ granulation {granulation_loc}. used cryo {cryo_cycles}. stopped bleeding w {hemostasis_method}. no complications.",
    
    # Style 4: Billing Focus
    "Procedures 31645, 31623, 31641. Dx J98.09. {age}M/F. {indication}. Findings: {stent_location} stent, {granulation_loc} granulation, {mucus_desc}. Intervention: Cryo destruction ({cryo_cycles}).",
    
    # Style 5: Structured
    "Patient: {age} {gender_short}\nIndication: {indication}\nFindings: {stent_location} stent with {granulation_loc} granulation; {mucus_desc}.\nAction: Therapeutic aspiration ({aspiration_list}); Cryotherapy ({cryo_cycles}); Hemostasis ({hemostasis_method})."
]

# ==========================================
# 4. GENERATOR LOGIC
# ==========================================
def generate_dataset():
    dataset = []
    
    for _ in range(NUM_SAMPLES):
        # A. Randomly select variables
        age = random.choice(data_pool["age"])
        gender_tup = random.choice(data_pool["gender_tuple"]) # (long, short, subj, poss)
        indication = random.choice(data_pool["indication"])
        stent_location = random.choice(data_pool["stent_location"])
        granulation_loc = random.choice(data_pool["granulation_loc"])
        mucus_desc = random.choice(data_pool["mucus_desc"])
        cryo_cycles = random.choice(data_pool["cryo_cycles"])
        hemostasis_method = random.choice(data_pool["hemostasis_method"])
        aspiration_list = random.choice(data_pool["aspiration_list"])
        
        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_tup[1], 
            gender_long=gender_tup[0],
            indication=indication,
            stent_location=stent_location,
            granulation_loc=granulation_loc,
            mucus_desc=mucus_desc,
            cryo_cycles=cryo_cycles,
            hemostasis_method=hemostasis_method,
            aspiration_list=aspiration_list
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            age=age, 
            gender_long=gender_tup[0],
            gender_pronoun=gender_tup[2],
            gender_poss=gender_tup[3],
            indication=indication,
            stent_location=stent_location,
            granulation_loc=granulation_loc,
            mucus_desc=mucus_desc,
            cryo_cycles=cryo_cycles,
            hemostasis_method=hemostasis_method,
            aspiration_list=aspiration_list
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