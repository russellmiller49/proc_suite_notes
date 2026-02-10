import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_036"
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
    "age": ["34", "41", "47", "52", "58", "64", "69", "73", "77", "85"],
    "gender_tuple": [
        ("female", "F", "She", "Her"), 
        ("male", "M", "He", "His")
    ],
    "attending": ["Dr. Ingraham", "Dr. Bowers", "Dr. Chen", "Dr. Smith", "Dr. Miller", "Dr. Jones"],
    "assistant": ["Dr. Doe", "Dr. White", "Dr. Black", "PA-C Green", "PA-C Brown"],
    
    # Logic: Side triggers Position. (If Right side, Position is Left Lat Decubitus)
    "side_tuple": [
        ("Right", "Left Lateral Decubitus"), 
        ("Left", "Right Lateral Decubitus")
    ],
    
    "removal_reason": [
        "patient request and partial dislodgement",
        "resolution of pleural effusion",
        "suspected catheter tract infection",
        "catheter malfunction and blockage",
        "completion of therapy",
        "accidental cuff dislodgement"
    ],
    
    "site_appearance": [
        "clean and dry, with no erythema, tenderness, or drainage",
        "clean, dry, with mild erythema at the exit site but no purulence",
        "showing evidence of granulation tissue but no active drainage",
        "well-healed with no signs of infection"
    ],
    
    "cpt_code": ["32552"], # Removal of indwelling tunneled pleural catheter
    
    "plan_action": [
        "Follow up in Interventional Pulmonary Pleural clinic.",
        "Follow up with primary oncologist.",
        "Return to clinic only as needed.",
        "Follow up in 2 weeks for wound check."
    ]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
# Based on note_036.txt
note_template = """INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: [Date] 
INDICATION FOR OPERATION: [Patient Name] is a {age}-year-old {gender_long} who presents with a pleural effusion requiring removal of an indwelling tunneled pleural catheter.

PREOPERATIVE DIAGNOSIS
Pleural Effusion

POSTOPERATIVE DIAGNOSIS
Pleural Effusion
Status post removal of indwelling tunneled pleural catheter

PROCEDURE
Removal of indwelling tunneled pleural catheter with cuff (CPT {cpt})

ATTENDING: {attending}
ASSISTANT: {assistant}

ANESTHESIA: None
ESTIMATED BLOOD LOSS: None
COMPLICATIONS: None

PROCEDURE IN DETAIL

Patient Position: {position}.

Tunneled Pleural Catheter Removal: The existing tunneled pleural catheter on the {side} side was identified.

Site Inspection: The catheter site was noted to be {site_appearance}.

Indication for Removal: {removal_reason}.

Technique: The previous tunneled pleural catheter was dissected free and removed.
No local anesthesia was utilized for the procedure.

Closure: The site was not sutured.

Dressing: A clean dry dressing was applied. The patient was instructed that the dressing should remain in place for a minimum of 72 hours and that it is acceptable to shower with an occlusive dressing.

Adjuncts: No antibiotics were administered.

FINDINGS / OBSERVATIONS
Date of original TPC insertion: [REDACTED].

IMPRESSION / PLAN
{age}-year-old {gender_long} who presents for Tunnel Pleural Catheter Removal.

The patient tolerated the procedure well.
There were no immediate complications.

{plan}

Obtain follow-up chest x-ray (CXR).

DISPOSITION: Nursing Unit."""

# 5 Distinct Prompt Styles
prompt_styles = [
    # Style 1: Telegraphic / Brief
    "Remove TPC {side}, {age}{gender_short}. Reason: {removal_reason}. Site {site_short}. No comps.",
    
    # Style 2: Dictation / Narrative
    "Please generate a procedure note for TPC removal. Patient is a {age} year old {gender_long}. The catheter was on the {side}. Indication was {removal_reason}. The site was {site_short}. Attending was {attending}.",
    
    # Style 3: Sloppy / Quick Input
    "{age}yo {gender_short} TPC pull {side}. {removal_reason}. Site ok. {attending}/{assistant}.",
    
    # Style 4: Billing Focused
    "Procedure: Removal of Tunneled Pleural Catheter ({cpt}). Side: {side}. Dx: Effusion. Indication: {removal_reason}.",
    
    # Style 5: Structured Request
    "PATIENT: {age} / {gender_short}\nPROCEDURE: TPC Removal\nSIDE: {side}\nREASON: {removal_reason}\nATTENDING: {attending}"
]

# ==========================================
# 4. GENERATOR LOGIC
# ==========================================
def generate_dataset():
    dataset = []
    
    for _ in range(NUM_SAMPLES):
        # A. Randomly select variables
        age = random.choice(data_pool["age"])
        
        # Gender Tuple: (long, short, SubjPro, ObjPro)
        gend_tup = random.choice(data_pool["gender_tuple"])
        gender_long = gend_tup[0]
        gender_short = gend_tup[1]
        
        attending = random.choice(data_pool["attending"])
        assistant = random.choice(data_pool["assistant"])
        
        # Side Tuple: (Side, Position) -> Logic Sync
        side_tup = random.choice(data_pool["side_tuple"])
        side = side_tup[0]
        position = side_tup[1]
        
        removal_reason = random.choice(data_pool["removal_reason"])
        site_appearance = random.choice(data_pool["site_appearance"])
        # Create a short version of site appearance for telegraphic prompts
        site_short = "clean" if "clean" in site_appearance else "mild erythema"
        
        cpt = random.choice(data_pool["cpt_code"])
        plan = random.choice(data_pool["plan_action"])
        
        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_short, 
            gender_long=gender_long,
            side=side,
            removal_reason=removal_reason,
            site_short=site_short,
            attending=attending,
            assistant=assistant,
            cpt=cpt
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            age=age,
            gender_long=gender_long,
            cpt=cpt,
            attending=attending,
            assistant=assistant,
            position=position,
            side=side,
            site_appearance=site_appearance,
            removal_reason=removal_reason,
            plan=plan
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