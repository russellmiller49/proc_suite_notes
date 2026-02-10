import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_083" 
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
# Variations specific to Interventional Pulmonology and this specific case anatomy
data_pool = {
    "age": ["58", "62", "65", "68", "71", "74", "79", "82"],
    "gender_tuple": [("female", "F", "She", "Her"), ("male", "M", "He", "His")],
    "stent_brand": ["Microtech", "Aero", "Ultraflex", "Silicone", "Dumont"],
    "stent_issue": [
        "migrated distally", 
        "migrated proximally", 
        "partially migrated", 
        "significant granulation tissue overgrowth", 
        "fractured and migrated"
    ],
    "mucus_desc": [
        "thick yellow-green mucus", 
        "copious white frothy secretions", 
        "tenacious purulent plugging", 
        "blood-tinged mucus plugs", 
        "inspissated secretions"
    ],
    "mucosa_desc": [
        "ragged and irregular", 
        "friable and edematous", 
        "hyperemic with granulation", 
        "inflamed and necrotic"
    ],
    "probe_type": ["1.7mm cryoprobe", "2.4mm cryoprobe", "1.9mm cryoprobe"],
    "bal_location": [
        "Superior Segment of the Lingula (LB4)", 
        "Inferior Segment of the Lingula (LB5)", 
        "Left Upper Lobe (LB3)"
    ],
    "bal_volumes": [
        ("40", "15"), ("50", "20"), ("60", "25"), ("30", "10"), ("100", "40")
    ],
    "plan_rx": [
        "Start antibiotics to treat MSSA; add Prednisone 20 mg",
        "Start Levaquin for Pseudomonas coverage; add Prednisone 40 mg",
        "Start Augmentin; add Solu-Medrol 40 mg IV",
        "Start Doxycycline; add Dexamethasone 4 mg",
        "Start Zosyn; taper Prednisone starting at 30 mg"
    ]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
# The template preserves the complex Left-side anatomy while varying findings and tools.
note_template = """NOTE_ID:  {note_id} SOURCE_FILE: {note_id}.txt

INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

INDICATION FOR OPERATION [REDACTED] is a {age}-year-old {gender_long} who presents with bronchial stenosis.
The patient has a complex airway with significant stenosis of the Left Mainstem Bronchus (LMSB) and complete occlusion of the Left Lower Lobe (LLL) bronchus.
Unusual Procedural Circumstances: This patient required extensive mechanical excision of endobronchial tissue to salvage the airway, as well as stent management given aberrant anatomy.
This resulted in >80% increased work due to the technical difficulty of the procedure and the physical and mental effort required.

PREOPERATIVE DIAGNOSIS
J98.09 Other diseases of bronchus, not elsewhere classified 

POSTOPERATIVE DIAGNOSIS
J98.09 Other diseases of bronchus, not elsewhere classified 
Bronchial stenosis with stent migration and occlusion 

PROCEDURE
31645 Therapeutic aspiration initial episode 
31635 Foreign body removal (Stent removal) 
31641 Destruction of tumor OR relief of stenosis by any method other than excision (e.g., laser therapy, cryotherapy) 
31625 Endobronchial Biopsy(s) 
31654 Radial EBUS 
31624 Bronchoalveolar lavage (BAL) 
22 Substantially greater work than normal 

ANESTHESIA General Anesthesia 

MONITORING Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.

INSTRUMENTATION Disposable Bronchoscope; {probe_type}; Alligator Forceps; Radial EBUS probe; Jag wire.

ESTIMATED BLOOD LOSS Minimum 

COMPLICATIONS None 

PROCEDURE IN DETAIL After the successful induction of anesthesia, a timeout was performed (confirming the patient's name, procedure type, and procedure location).

Patient Position / Airway Inspection An iGel was placed by anesthesia after adequate sedation.
Initial inspection revealed the airway stent was partially occluded with {mucus_desc}.
It appeared that the LMSB stent had {stent_issue} and was covering the LMSB.

Therapeutic Aspiration Successful therapeutic aspiration was performed to clean out the Trachea (Middle 1/3), Trachea (Distal 1/3), Left Mainstem, Carina, LUL Lingula Carina (Lc1), and Left Carina (LC2) from mucus and mucus plugs.

Foreign Body (Stent) Removal Using forceps, the proximal end of the {stent_brand} stent was grasped and removed en bloc with the bronchoscope.
The removal was difficult due to significant inflammation. After removal, the LMSB mucosa appeared {mucosa_desc}, with dynamic collapse noted.

Tumor Destruction and Relief of Stenosis Endobronchial tumor/tissue was noted and required extensive excision and mechanical debridement.
This was performed using alligator forceps and a {probe_type} with 30-second freeze cycles to achieve vascular occlusion, followed by cryotherapy for further debulking of the LUL ostium.

Navigation and Airway Survey The LUL bronchus was approximately 3-4 mm, and the LLL bronchus could not be visualized.
Saline was instilled without visualization of the LLL. The area was firm, and the LLL airway could not be identified despite multiple attempts.
Due to the complex anatomy, a jag wire was placed in the Lingula, and radial EBUS was utilized to identify vasculature and airways to assist in localization.
Despite these measures, the LLL remained unidentifiable.

Bronchoalveolar Lavage (BAL) Bronchoalveolar lavage was performed at the {bal_location}.
{bal_in} cc of NS was instilled, and suction returned {bal_out} cc of NS.
Endobronchial Biopsy Endobronchial biopsies were obtained from the LMSB.

Conclusion The patient tolerated the procedure well.
There were no immediate complications. At the conclusion of the operation, the patient was extubated in the operating room and transported to the recovery room in stable condition.

SPECIMEN(S)
LUL BAL - cell count, culture, and cytology 
LMSB EBBx - pathology 

IMPRESSION / PLAN
{age}-year-old {gender_long} with very odd presentation of cicatrization and benign stenosis of the LMSB without evidence of residual malignancy.
Very challenging anatomy of the airway and stenosis with continued robust inflammatory response.
No additional stents were placed at this time.

Admit overnight.

{plan_rx}.
Obtain CT chest with contrast.

NPO after midnight for potential follow-up bronchoscopy.
"""

# 5 Prompt styles matching the variables
prompt_styles = [
    # Style 1: Telegraphic
    "Operative Report: {age}{gender_short}, LMSB stenosis. Removed {stent_brand} stent ({stent_issue}). Findings: {mucus_desc}, {mucosa_desc} mucosa. EBUS used for navigation. Plan: {plan_rx_short}.",
    
    # Style 2: Dictation
    "Please generate a procedure note for a {age}-year-old {gender_long}. We performed a bronchoscopy for stent removal. The {stent_brand} stent in the LMSB had {stent_issue}. We found {mucus_desc}. Used {probe_type} for debridement. BAL done at {bal_location}.",
    
    # Style 3: Sloppy / Quick
    "{age}yo {gender_short} interventional bronch. lmsb stent removal ({stent_brand}). it {stent_issue}. airway was mess, {mucus_desc}. bal {bal_in}/{bal_out} cc at {bal_location}. admit and {plan_rx_short}.",
    
    # Style 4: Billing Focus
    "Codes 31645, 31635, 31641, 31654. {age} {gender_short}. Dx J98.09. Procedure: Removal of {stent_brand} stent, lysis of adhesions using {probe_type}. Complicated by {stent_issue}.",
    
    # Style 5: Structured
    "Patient: {age} {gender_short}\nIndication: Bronchial stenosis/Stent check\nFindings: {stent_brand} stent {stent_issue}, {mucus_desc}, {mucosa_desc} mucosa\nProcedure: Stent removal, BAL ({bal_location}), EBUS\nPlan: {plan_rx}"
]

# ==========================================
# 4. GENERATOR LOGIC
# ==========================================
def generate_dataset():
    dataset = []
    
    for _ in range(NUM_SAMPLES):
        # A. Randomly select variables
        age = random.choice(data_pool["age"])
        gender_tup = random.choice(data_pool["gender_tuple"]) # (long, short, he/she, his/her)
        stent_brand = random.choice(data_pool["stent_brand"])
        stent_issue = random.choice(data_pool["stent_issue"])
        mucus_desc = random.choice(data_pool["mucus_desc"])
        mucosa_desc = random.choice(data_pool["mucosa_desc"])
        probe_type = random.choice(data_pool["probe_type"])
        bal_location = random.choice(data_pool["bal_location"])
        bal_vols = random.choice(data_pool["bal_volumes"])
        plan_rx = random.choice(data_pool["plan_rx"])
        
        # Derive short plan for telegraphic prompts
        plan_rx_short = plan_rx.split(';')[0].replace("Start ", "")

        # B. Generate Prompt
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_tup[1], 
            gender_long=gender_tup[0],
            stent_brand=stent_brand,
            stent_issue=stent_issue,
            mucus_desc=mucus_desc,
            mucosa_desc=mucosa_desc,
            probe_type=probe_type,
            bal_location=bal_location,
            bal_in=bal_vols[0],
            bal_out=bal_vols[1],
            plan_rx=plan_rx,
            plan_rx_short=plan_rx_short
        )
        
        # C. Generate Completion
        completion = note_template.format(
            note_id=NOTE_ID,
            age=age, 
            gender_long=gender_tup[0],
            stent_brand=stent_brand,
            stent_issue=stent_issue,
            mucus_desc=mucus_desc,
            mucosa_desc=mucosa_desc,
            probe_type=probe_type,
            bal_location=bal_location,
            bal_in=bal_vols[0],
            bal_out=bal_vols[1],
            plan_rx=plan_rx
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