import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_098"
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
    "age": ["45", "52", "56", "59", "64", "68", "72", "77", "81"],
    "gender_tuple": [("female", "F", "She", "Her"), ("male", "M", "He", "His")],
    "doctor": ["Ingraham", "Bowers", "Chen", "Smith", "Miller", "Jones", "Doe", "Patel", "Weiss"],
    "indication": ["bronchial stenosis", "tracheal stenosis", "airway obstruction", "anastomotic stricture"],
    
    # Logic pairs: Stent Location vs. Contralateral/Secondary Location
    "location_pairs": [
        {"stent_loc": "RML", "stent_parent": "RMSB", "bal_loc": "LLL", "bal_seg": "Posterior-Basal Segment (LB10)", "contra_side": "Left"},
        {"stent_loc": "RLL", "stent_parent": "RMSB", "bal_loc": "LUL", "bal_seg": "Apical-Posterior Segment (LB1+2)", "contra_side": "Left"},
        {"stent_loc": "LMSB", "stent_parent": "Trachea", "bal_loc": "RLL", "bal_seg": "Superior Segment (RB6)", "contra_side": "Right"},
        {"stent_loc": "LUL", "stent_parent": "LMSB", "bal_loc": "RML", "bal_seg": "Medial Segment (RB5)", "contra_side": "Right"},
    ],
    
    "stent_issue": [
        "migrated distally", 
        "appeared too small for the airway", 
        "was partially obstructed by granulation tissue", 
        "showed signs of fracture"
    ],
    
    "new_stent_device": [
        "8 x 15 mm Aero SEM stent", 
        "10 x 20 mm Ultraflex stent", 
        "12 x 40 mm AERO stent", 
        "9 x 20 mm covered metal stent"
    ],
    
    "secretions": [
        "thick, white mucus", 
        "purulent yellow secretions", 
        "copious mucoid secretions", 
        "blood-tinged secretions"
    ],
    
    "medication": ["bivalirudin", "heparin", "Coumadin", "Eliquis", "Lovenox"]
}

# ==========================================
# 3. TEMPLATES
# ==========================================

note_template = """NOTE_ID:  {note_id} SOURCE_FILE: {note_id}.txt

INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: [Date] CC Referred Physician: {doctor}

INDICATION FOR OPERATION [REDACTED] is a {age}-year-old {gender_long} who presents with {indication}.
The nature, purpose, risks, benefits, and alternatives to Bronchoscopy were discussed with the patient in detail.
CONSENT Obtained before the procedure. Indications, potential complications, and alternatives were discussed.
The patient wished to proceed and informed consent was obtained.

PREOPERATIVE DIAGNOSIS
{indication}

POSTOPERATIVE DIAGNOSIS
{indication}

PROCEDURE
31645 Therapeutic aspiration initial episode
31622 Dx bronchoscope/cell washing
31624 Dx bronchoscope/lavage (BAL)
31625 Endobronchial Biopsy(s)
31630 Balloon dilation
31636 Dilate and bronchial stent initial bronchus
31638 Revision of tracheal/bronchial stent
31640 Bronchoscopy with excision
31635 Foreign body removal
22 Substantially greater work than normal (increased intensity, time, technical difficulty, severity of patient's condition, physical and mental effort).

Justification: Due to small right mainstem diameter, it was difficult to use the therapeutic bronchoscope.
At times, a disposable bronchoscope was introduced via the mouth alongside the therapeutic bronchoscope going through the tracheostomy tube.
This resulted in >40% increased work.

ATTENDING {doctor}

ANESTHESIA General Anesthesia

MONITORING Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.

INSTRUMENTATION Flexible Therapeutic Bronchoscope; Disposable Bronchoscope.

ESTIMATED BLOOD LOSS Minimum

COMPLICATIONS None

PROCEDURE IN DETAIL After the successful induction of anesthesia, a timeout was performed confirming the patient's name, procedure type, and procedure location.

Initial Airway Inspection The bronchoscope was advanced into the existing tracheostomy tube.
A total of 4 mL of 2% lidocaine was instilled onto the main carina.
The airways were examined to the subsegmental level bilaterally.

Primary Inspection: The anastomosis was without dehiscence but showed white-yellow exudate along the anterior portion of the {stent_parent}.
A stent was visualized in the {stent_loc} extending past the ostium; it was in appropriate position, but the distal portion did not appear fully extended.

{contra_side} Lung: The anastomosis was intact with an area of granulation tissue but without significant stenosis.
A white-yellow fibrinous plaque was noted along the airway extending to the ostium.

Secretions: A moderate amount of {secretions} was found in the {bal_loc} and was therapeutically aspirated.

Interventions

1. Bronchoalveolar Lavage (BAL) BAL was performed at the {bal_seg}.
60 cc of NS was instilled, and suction returned 15 cc of NS.
Samples were sent for cell count and microbiology.

2. {stent_loc} Stent Management (Dilation, Removal, Replacement) Balloon dilation of the existing {stent_loc} bronchus stent was performed using a CRE 8-9-10 balloon.
The stent was dilated x2 to 9 mm for 1 minute each dilation. The stent did not increase in diameter; it {stent_issue}.

Removal: A complex approach was required due to airway size.
Using the therapeutic bronchoscope via the tracheostomy stoma and a disposable bronchoscope via the mouth, an attempt was made to reposition the stent.
The stent (foreign body) was grasped with forceps and removed en bloc from the {stent_loc} via the tracheostomy stoma.
Examination showed the stent did not dilate past 7 mm.

Replacement: The bronchoscope was introduced into the mouth and advanced through the vocal cords into the trachea past the partially deflated cuff of the tracheostomy tube.
A jag wire was introduced into the {stent_loc}. Under direct visualization, an {new_stent_device} was deployed into the {stent_loc} bronchus.
The stent was revised with forceps; position was adequate, and distal airways were patent.

3. {contra_side} Side Management The bronchus was dilated to 8 mm with improvement in diameter.
Fibrinous/yellow-white tumor tissue was removed with forceps at the ostium.

Conclusion There was no evidence of active bleeding, and the bronchoscope was removed.
The patient tolerated the procedure well with no immediate complications.
The patient was transitioned to mechanical ventilation and returned to the ICU to recover.

SPECIMENS
BAL - {bal_loc} - cell count and culture
Stent - for culture
Fibrinous tissue - culture and pathology

IMPRESSION / PLAN
[REDACTED] is a {age}-year-old {gender_long} who presented for bronchoscopy for {indication}.
Follow-up culture and pathology results.
Follow-up bronchoscopy in 1 week to evaluate stent.
Restart {medication} at 18:00 today.
"""

prompt_styles = [
    # Style 1: Telegraphic
    "Pt {age} {gender_short}. Ref {doctor}. Indication: {indication}. Found {stent_loc} stent {stent_issue}. Removed FB, replaced with {new_stent_device}. BAL {bal_loc} showed {secretions}. Restart {medication}.",
    
    # Style 2: Dictation
    "Write a full operative report for Dr. {doctor}. The patient is a {age}-year-old {gender_long} with {indication}. We performed a therapeutic bronchoscopy. The {stent_loc} stent had {stent_issue} and required removal and replacement with a {new_stent_device}. We also lavaged the {bal_loc} due to {secretions}. Plan is to restart {medication} tonight.",
    
    # Style 3: Sloppy / Quick
    "{age}yo {gender_short} with {indication}. {stent_loc} stent was bad, {stent_issue}. took it out via trach/mouth combo. put in {new_stent_device}. also saw {secretions} in {bal_loc}, did BAL. no complications. restart {medication}.",
    
    # Style 4: Billing Focus
    "Codes: 31645, 31622, 31636, 31635, 31638. Pt {age} {gender_short}. Dx: {indication}. Complex removal of {stent_loc} stent ({stent_issue}). Replacement with {new_stent_device}. BAL performed at {bal_loc}. Meds: {medication}.",
    
    # Style 5: Structured
    "Patient: {age} {gender_short}\nDoctor: {doctor}\nIndication: {indication}\nKey Findings: {stent_loc} stent {stent_issue}, {secretions} in {bal_loc}.\nInterventions: Removal of stent, placement of {new_stent_device}, BAL.\nPlan: Restart {medication}."
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
        
        # Select Logic Pair for anatomical consistency
        loc_data = random.choice(data_pool["location_pairs"])
        
        stent_issue = random.choice(data_pool["stent_issue"])
        new_stent = random.choice(data_pool["new_stent_device"])
        secretions = random.choice(data_pool["secretions"])
        medication = random.choice(data_pool["medication"])
        
        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_tup[1], 
            gender_long=gender_tup[0],
            doctor=doctor, 
            indication=indication,
            stent_loc=loc_data["stent_loc"],
            stent_issue=stent_issue,
            new_stent_device=new_stent,
            bal_loc=loc_data["bal_loc"],
            secretions=secretions,
            medication=medication
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            age=age, 
            gender_long=gender_tup[0], 
            doctor=doctor,
            indication=indication,
            stent_loc=loc_data["stent_loc"],
            stent_parent=loc_data["stent_parent"],
            stent_issue=stent_issue,
            new_stent_device=new_stent,
            bal_loc=loc_data["bal_loc"],
            bal_seg=loc_data["bal_seg"],
            contra_side=loc_data["contra_side"],
            secretions=secretions,
            medication=medication
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