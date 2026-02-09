import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_011"
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
    "age": ["22", "29", "33", "38", "45", "51", "59", "64", "72"],
    "gender_tuple": [("female", "F"), ("male", "M")],
    "indication_dx": [
        "J98.09 Other diseases of bronchus",
        "R04.2 Hemoptysis",
        "J98.09 Bronchial disease NOS",
        "R04.89 Hemorrhage from respiratory passages"
    ],
    "old_blocker_type": ["7Fr Arndt blocker", "5Fr Uniblocker", "9Fr Arndt blocker", "EZ-Blocker"],
    "new_blocker_type": ["5Fr Uniblocker", "7Fr Arndt blocker", "9Fr Cohen blocker"],
    "cryo_probe_size": ["1.7mm", "1.9mm", "2.4mm"],
    "inflation_vol": ["3cc", "4cc", "2.5cc", "5cc", "3.5cc"],
    "lavage_return": ["10 cc", "15 cc", "20 cc", "25 cc", "12 cc"],
    "plan_intervention": [
        "IR-guided Bronchial Artery Embolization (BAE)",
        "CT Angiogram Chest",
        "Thoracic Surgery consultation",
        "Observation in ICU"
    ]
}

# ==========================================
# 3. TEMPLATES
# ==========================================

# We define the template logic inside the generation loop to handle 
# complex left/right anatomical consistency.
note_template_base = """NOTE_ID:  {note_id} SOURCE_FILE: {note_id}.txt

INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

INDICATION FOR OPERATION [REDACTED] is a {age}-year-old {gender_long} who presents with hemoptysis.
The nature, purpose, risks, benefits, and alternatives to bronchoscopy were discussed with the patient in detail.
The patient indicated a wish to proceed with surgery and informed consent was signed.

CONSENT Obtained before the procedure.
Indications, potential complications, and alternatives were discussed with the patient or surrogate.
The patient or surrogate read and signed the provided consent form or provided consent over the phone.
The consent was witnessed by an assisting medical professional.

PREOPERATIVE DIAGNOSIS

{diagnosis}

POSTOPERATIVE DIAGNOSIS

{diagnosis}

PROCEDURE

31646: Therapeutic aspiration subsequent episodes 

31641: Destruction of tumor OR relief of stenosis by any method other than excision (e.g., laser therapy, cryotherapy) 

Modifier 22 Details: Unusual Procedure.
This patient required cryotherapy for removal of organized clot throughout the {side_adj} airways.
This resulted in >100% increased work due to time, technical difficulty of procedure, and physical and mental effort required.

31634: Balloon occlusion or placement of occlusive substance 

31624: Bronchoalveolar lavage (BAL) 

31635: Foreign body removal 

ANESTHESIA General Anesthesia 

MONITORING Pulse oximetry, heart rate, telemetry, and blood pressure were continuously monitored by an independent trained observer that was present throughout the entire procedure.
INSTRUMENTATION Flexible Diagnostic Bronchoscope 

ESTIMATED BLOOD LOSS None 

COMPLICATIONS None 

PROCEDURE IN DETAIL After the successful induction of anesthesia, a timeout was performed confirming the patient's name, procedure type, and procedure location.
Patient Position: Supine.

Initial Airway Inspection The tracheostomy tube was in good position.
Pharynx/Larynx/Vocal Cords: Not assessed due to bronchoscopy introduction through tracheostomy tube.

Trachea: Distal 1/3 normal.

Main Carina: Sharp.

{contralateral_lung_section}

{ipsilateral_lung_section}

Mucosa: Normal.

Secretions: Minimal, thin, and clear.

Therapeutic Aspiration Successful therapeutic aspiration was performed to clean out the Trachea (Distal 1/3), Right Mainstem, Bronchus Intermedius, Left Mainstem, Carina, {segments_list} from mucus, blood, and blood clots.

Foreign Body Removal (Blocker Retrieval) The existing blocker (foreign body) was removed under direct visualization without any additional bleeding.

Cryotherapy / Clot Extraction Endobronchial clot at the {target_carina_1} and {target_carina_2} was treated.
A {cryo_size} cryoprobe was used to evacuate the {target_lobe} airways of organized clot.
Modality: Cryoprobe ({cryo_size}) 
Duration: 5-10 second freezes 
Results: Excellent clot removal 

Endobronchial Blocker Placement A new {new_blocker} was positioned at the {target_carina_2} and secured in place with the ventilator adaptor.
The device was placed at the tape level at the dark blue securement device.
Inflation: Confirmed that {vol} of air was required to inflate the balloon to fully occlude the {target_lobe}.
Check: When the blocker balloon was deflated, additional fresh blood was noted coming from {bleeding_segment}.
The blocker was reinflated with {vol} of air with cessation of bleeding.
The endobronchial blocker balloon was left inflated in the {target_lobe}.

Bronchoalveolar Lavage (BAL) BAL was performed in the {bal_segment}.
Instilled: 60 cc of Normal Saline.
Returned: {return_vol} of Normal Saline.
Analysis: Samples sent for Microbiology (Cultures/Viral/Fungal).

The patient tolerated the procedure well.
There were no immediate complications.

SPECIMENS

BAL (Microbiology/Viral/Fungal) 

IMPRESSION / PLAN

[REDACTED] is a {age}-year-old {gender_long} who presented for bronchoscopy for evaluation of hemoptysis.
Cryotherapy (cryoprobe) was used to evacuate the {target_lobe} airways of organized clot.
A {new_blocker} was placed and left inflated at the {target_lobe}.

Plan:

Obtain post-procedure CXR.
Keep blocker up until {plan_next}.
Repeat bronchoscopy [REDACTED] for bleeding evaluation and blocker take down.
"""

# ==========================================
# 4. GENERATOR LOGIC
# ==========================================

prompt_styles = [
    # Style 1: Telegraphic / Handoff
    "Pt {age}{gender_short}, severe hemoptysis. Old blocker rmvd from {side} mainstem. {cryo_size} cryo used for clots in {target_lobe}. New {new_blocker} placed. Plan: {plan_next}.",
    
    # Style 2: Dictation
    "Please generate an IP op report for a {age} year old {gender_long}. Preop dx {diagnosis}. Procedure included removal of old blocker, cryotherapy for organized clot in the {side} lung, and placement of a new {new_blocker}. BAL was done in {bal_segment}.",
    
    # Style 3: Sloppy / Quick Input
    "{age}yo {gender_short} hemoptysis case. Swapped out old {old_blocker} for {new_blocker} in {target_lobe}. Extensive cryo needed ({cryo_size}). Bleeding controlled with {vol} inflation.",
    
    # Style 4: Billing Focus
    "Codes: 31646, 31641-22, 31634, 31624, 31635. Dx: {diagnosis}. Pt {age} {gender_short}. Complex cryo debridement of {target_lobe} clot required. Blocker exchange performed.",
    
    # Style 5: Structured Request
    "PATIENT: {age}/{gender_short}\nINDICATION: Hemoptysis\nACTION: Remove {old_blocker}, Cryo debridement ({side} side), Place {new_blocker}\nFINDINGS: Clot in {target_lobe}, Cavity in {contra_lobe}."
]

def generate_dataset():
    dataset = []
    
    for _ in range(NUM_SAMPLES):
        # A. Randomly select basic variables
        age = random.choice(data_pool["age"])
        gender_tup = random.choice(data_pool["gender_tuple"])
        diagnosis = random.choice(data_pool["indication_dx"])
        old_blocker = random.choice(data_pool["old_blocker_type"])
        new_blocker = random.choice(data_pool["new_blocker_type"])
        cryo_size = random.choice(data_pool["cryo_probe_size"])
        vol = random.choice(data_pool["inflation_vol"])
        return_vol = random.choice(data_pool["lavage_return"])
        plan_next = random.choice(data_pool["plan_intervention"])
        
        # B. Anatomy Logic (Left vs Right Side Bleed)
        # To maintain medical accuracy, if the bleed is Left, the blocker goes Left.
        is_left_side = random.choice([True, False])
        
        if is_left_side:
            side_adj = "left-sided"
            side_short = "Left"
            
            # Ipsilateral (Bleeding side - Left)
            ipsilateral_lung_section = f"""Left Lung Proximal Airways: An endobronchial balloon was noted at the lingula/LUL with organized clot obscuring evaluation of distal airways.
A {old_blocker} was noted in the middle of the left mainstem (LMS) with the balloon deflated.
Otherwise, normal anatomic branching to segmental level."""
            
            # Contralateral (Non-bleeding - Right)
            contralateral_lung_section = """Right Lung Proximal Airways: Normal anatomic branching to segmental level. Thin rusty secretions were noted.
A cavity was noted in the RB2 subsegment."""
            
            # Specific Targets
            target_carina_1 = "LUL Lingula Carina (Lc1)"
            target_carina_2 = "Left Carina (LC2)"
            target_lobe = "LUL"
            contra_lobe = "RUL" # For prompt generation logic
            bleeding_segment = "LB1/2"
            segments_list = "RUL Carina (RC1), RML Carina (RC2), LUL Lingula Carina (Lc1), and Left Carina (LC2)"
            bal_segment = "Posterior-Basal Segment of LLL (LB10)"
            
        else:
            side_adj = "right-sided"
            side_short = "Right"
            
            # Ipsilateral (Bleeding side - Right)
            ipsilateral_lung_section = f"""Right Lung Proximal Airways: An endobronchial balloon was noted at the RUL with organized clot obscuring evaluation of distal airways.
A {old_blocker} was noted in the middle of the right mainstem (RMS) with the balloon deflated.
Otherwise, normal anatomic branching to segmental level."""

            # Contralateral (Non-bleeding - Left)
            contralateral_lung_section = """Left Lung Proximal Airways: Normal anatomic branching to segmental level. Thin rusty secretions were noted.
A cavity was noted in the LB1+2 subsegment."""
            
            # Specific Targets
            target_carina_1 = "RUL Carina (RC1)"
            target_carina_2 = "Right Carina (RC2)"
            target_lobe = "RUL"
            contra_lobe = "LUL"
            bleeding_segment = "RB1"
            segments_list = "LUL Carina (LC1), Lingula Carina, RUL Carina (RC1), and Right Carina (RC2)"
            bal_segment = "Posterior-Basal Segment of RLL (RB10)"

        # C. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_tup[1], 
            gender_long=gender_tup[0],
            diagnosis=diagnosis,
            side=side_short,
            target_lobe=target_lobe,
            contra_lobe=contra_lobe,
            old_blocker=old_blocker,
            new_blocker=new_blocker,
            cryo_size=cryo_size,
            vol=vol,
            bal_segment=bal_segment,
            plan_next=plan_next
        )
        
        # D. Generate Completion (Structured Note)
        completion = note_template_base.format(
            note_id=NOTE_ID,
            age=age, 
            gender_long=gender_tup[0],
            diagnosis=diagnosis,
            side_adj=side_adj,
            contralateral_lung_section=contralateral_lung_section,
            ipsilateral_lung_section=ipsilateral_lung_section,
            segments_list=segments_list,
            target_carina_1=target_carina_1,
            target_carina_2=target_carina_2,
            target_lobe=target_lobe,
            cryo_size=cryo_size,
            new_blocker=new_blocker,
            vol=vol,
            bleeding_segment=bleeding_segment,
            bal_segment=bal_segment,
            return_vol=return_vol,
            plan_next=plan_next
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