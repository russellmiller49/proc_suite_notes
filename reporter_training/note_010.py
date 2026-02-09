import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_010" 
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
    "ages": ["24", "29", "33", "38", "42", "49", "55", "61", "35"],
    "gender_tuple": [("female", "F", "She", "Her"), ("male", "M", "He", "His")],
    "doctors": ["Dr. Ingraham", "Dr. Bowers", "Dr. Chen", "Dr. Smith", "Dr. Miller", "Dr. Jones"],
    "indications": [
        "hemoptysis", 
        "massive hemoptysis", 
        "recurrent hemoptysis", 
        "post-obstructive pneumonia with hemoptysis"
    ],
    "medications": [
        "Versed 8 mg; Fentanyl 100 mcg",
        "Versed 6 mg; Fentanyl 75 mcg",
        "Versed 10 mg; Fentanyl 150 mcg",
        "Propofol 100 mg; Fentanyl 50 mcg"
    ],
    "old_blocker": ["7Fr Arndt blocker", "9Fr Arndt blocker", "Cohen blocker"],
    "new_blocker": ["5Fr Uniblocker", "7Fr Uniblocker", "9Fr Uniblocker"],
    "cryo_probe": ["1.1 mm", "1.9 mm", "2.4 mm"],
    
    # Anatomical consistency logic: 
    # If the clot is in the Left Lung, the "Normal" lung is the Right, and vice versa.
    "anatomy_scenarios": [
        {
            "side": "Left",
            "affected_lung": "Left Lung",
            "normal_lung": "Right Lung",
            "normal_finding": "Cavity was noted in the RB2 subsegment and entered.", # Incidental finding on normal side
            "affected_lobe_abbr": "LUL",
            "affected_landmark": "lingula/LUL",
            "blocker_location_initial": "middle of the left mainstem (LMS)",
            "blocker_location_final": "Left Carina (LC2)",
            "cleaning_list": "Left Mainstem, Carina, RUL Carina (RC1), RML Carina (RC2), LUL Lingula Carina (Lc1), and Left Carina (LC2)",
            "blood_check_loc": "LB1/2 or LB3",
            "main_bronchus": "Left Mainstem"
        },
        {
            "side": "Right",
            "affected_lung": "Right Lung",
            "normal_lung": "Left Lung",
            "normal_finding": "Minor mucosal thickening noted in LB1/2.", # Incidental finding on normal side
            "affected_lobe_abbr": "RUL",
            "affected_landmark": "RUL/Apical Segment",
            "blocker_location_initial": "middle of the right mainstem (RMS)",
            "blocker_location_final": "Right Carina (RC1)",
            "cleaning_list": "Right Mainstem, Carina, LUL Carina (Lc1), LLL Carina (LC2), RUL Carina (RC1), and RML Carina (RC2)",
            "blood_check_loc": "RB1, RB2 or RB3",
            "main_bronchus": "Right Mainstem"
        }
    ]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
# Using the structure of note_010.txt
note_template = """NOTE_ID:  {note_id} SOURCE_FILE: {note_id}.txt

INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT 

DATE OF PROCEDURE: [Date] 

INDICATION FOR OPERATION  [REDACTED] is a {age}-year-old {gender_long} who presents with {indication}.
The nature, purpose, risks, benefits, and alternatives to bronchoscopy were discussed with the patient in detail.
The patient wished to proceed and informed consent was obtained. 

CONSENT  Obtained before the procedure.
Indications, potential complications, and alternatives were discussed with the patient or surrogate.
The patient or surrogate read and signed the provided consent form or provided consent over the phone.
The consent was witnessed by an assisting medical professional. 

PREOPERATIVE DIAGNOSIS 
J98.09 Other diseases of bronchus, not elsewhere classified

POSTOPERATIVE DIAGNOSIS 
J98.09 Other diseases of bronchus, not elsewhere classified

PROCEDURE 
Therapeutic aspiration (subsequent episodes) (CPT 31646) 
Destruction of tumor or relief of stenosis by any method other than excision (e.g., laser therapy, cryotherapy) (CPT 31641) 

ANESTHESIA  Moderate sedation (CPT 99152).
Medications: {meds}.

Time: Start 1450; Stop 1510 (Total 20 minutes).
Assessment: The patient was monitored continuously one-to-one throughout the entire procedure by the attending physician while anesthesia was administered.
MONITORING Pulse oximetry, heart rate, telemetry, and blood pressure were continuously monitored by an independent trained observer throughout the procedure.
INSTRUMENTATION  Flexible Hybrid (Pediatric) Bronchoscope; Cryoprobe system; Uniblocker. 

ESTIMATED BLOOD LOSS None 

COMPLICATIONS None 

PROCEDURE IN DETAIL After the successful induction of anesthesia, a timeout was performed confirming patient identity, planned procedures, and laterality.
Patient Position: Supine 

Initial Airway Inspection: 

Tracheostomy: The tracheostomy tube was in good position.
Pharynx/Larynx/Vocal Cords: Not assessed due to bronchoscopy introduction through tracheostomy tube.

Trachea: Distal 1/3 normal.

Main Carina: Sharp.
{normal_lung}: Normal anatomic branching to segmental level. Thin rusty secretions were noted.
{normal_finding}

{affected_lung}: Normal anatomic branching to segmental level mostly.
However, an endobronchial balloon was noted at the {affected_landmark} with organized clot obscuring evaluation of distal airways.
A {old_blocker} was noted in the {blocker_location_initial}; the balloon was deflated.

Mucosa: Normal.
Secretions: Minimal, thin, and clear (aside from specific areas noted).
Therapeutic Aspiration Successful therapeutic aspiration was performed to clean out the Trachea (Distal 1/3), {cleaning_list} from mucus, blood, and blood clots.

Endobronchial Blocker Placement A {new_blocker} balloon occlusion was performed at the {blocker_location_final} and secured in place with the Uniblocker ventilator adaptor.
Placement: At the tape level at dark blue securement device.
Inflation: Confirmed that 3 cc of air was required to inflate the balloon to fully occlude the {affected_lobe_abbr}.
The endobronchial blocker balloon was intermittently inflated in the {affected_lobe_abbr} to assist with clot removal.

Cryo-Extraction of Mucus Casts/Secretions A {cryo_probe} cryoprobe was applied to adherent organized clot at the {affected_landmark}.
Technique: 5–10 second freeze cycles. 

Result: Excellent clot removal. The airway was cleared with improved ventilation.

Hemostasis and Conclusion After the organized clot was removed from the {affected_lobe_abbr} orifice, the blocker balloon was deflated.
No blood was noted coming from {blood_check_loc}. The blocker was left deflated.
The patient tolerated the procedure well without immediate complications. 

SPECIMENS  None

IMPRESSION / PLAN 
[REDACTED] is a {age}-year-old {gender_long} who presented for bronchoscopy for evaluation of {indication}.
Cryotherapy (cryoprobe) successfully used to evacuate the {affected_lobe_abbr} airways of organized clot.
{new_blocker} was placed and left deflated at the {affected_lobe_abbr}.
The patient tolerated the procedure well and there were no immediate complications. 

PRN bronchoscopy as needed.
Decannulation as appropriate.
"""

# <--- CREATE 5 DISTINCT PROMPT STYLES HERE --->
prompt_styles = [
    # Style 1: Telegraphic
    "Operative Report: {age}{gender_short}, {indication}. Procedure: Cryo extract clot {affected_lobe_abbr}, exchange {old_blocker} for {new_blocker}. No complications.",
    
    # Style 2: Dictation
    "Please generate a procedure note for a {age} year old {gender_long} patient. Indication is {indication}. We performed therapeutic aspiration and cryotherapy. A {old_blocker} was found in the {affected_lung} and replaced with a {new_blocker} at the {affected_lobe_abbr}. {meds} used for sedation.",
    
    # Style 3: Sloppy / Quick
    "{age}yo {gender_short} with hemoptysis. bronchoscopy via trach. found {old_blocker} in {affected_lung}, removed clot with {cryo_probe} cryo. placed {new_blocker} in {affected_lobe_abbr}. tolerated well.",
    
    # Style 4: Billing Focus
    "Procedures: CPT 31646, 31641. DX J98.09. Patient {age} {gender_short}. Findings: Organized clot in {affected_lobe_abbr}, exchange of bronchial blocker. Cryotherapy utilized.",
    
    # Style 5: Structured
    "Patient: {age} {gender_short}\nDiagnosis: {indication}\nKey Findings: {old_blocker} replaced with {new_blocker} in {affected_lobe_abbr}. Clot removed via Cryo.\nSedation: {meds}"
]

# ==========================================
# 4. GENERATOR LOGIC
# ==========================================
def generate_dataset():
    dataset = []
    
    for _ in range(NUM_SAMPLES):
        # A. Randomly select variables
        age = random.choice(data_pool["ages"])
        gender_tup = random.choice(data_pool["gender_tuple"]) # (long, short, He/She, His/Her)
        doctor = random.choice(data_pool["doctors"])
        indication = random.choice(data_pool["indications"])
        meds = random.choice(data_pool["medications"])
        old_blocker = random.choice(data_pool["old_blocker"])
        new_blocker = random.choice(data_pool["new_blocker"])
        cryo_probe = random.choice(data_pool["cryo_probe"])
        
        # Select Anatomy Scenario (Left vs Right Logic)
        anatomy = random.choice(data_pool["anatomy_scenarios"])
        
        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_tup[1], 
            gender_long=gender_tup[0],
            indication=indication,
            affected_lobe_abbr=anatomy["affected_lobe_abbr"],
            affected_lung=anatomy["affected_lung"],
            old_blocker=old_blocker,
            new_blocker=new_blocker,
            meds=meds,
            cryo_probe=cryo_probe
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            age=age, 
            gender_long=gender_tup[0],
            indication=indication,
            meds=meds,
            
            # Anatomy Variables from the Scenario Dictionary
            normal_lung=anatomy["normal_lung"],
            normal_finding=anatomy["normal_finding"],
            affected_lung=anatomy["affected_lung"],
            affected_landmark=anatomy["affected_landmark"],
            affected_lobe_abbr=anatomy["affected_lobe_abbr"],
            blocker_location_initial=anatomy["blocker_location_initial"],
            blocker_location_final=anatomy["blocker_location_final"],
            cleaning_list=anatomy["cleaning_list"],
            blood_check_loc=anatomy["blood_check_loc"],
            
            # Instrument Variables
            old_blocker=old_blocker,
            new_blocker=new_blocker,
            cryo_probe=cryo_probe
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