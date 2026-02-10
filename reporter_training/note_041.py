import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_041"
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
    "age": ["45", "52", "58", "64", "68", "71", "77", "83", "89", "92"],
    "gender_tuple": [("female", "F", "She"), ("male", "M", "He")],
    "doctor": ["Ingraham", "Bowers", "Chen", "Smith", "Miller", "Jones", "Doe", "Patel", "Weiss"],
    "indication": ["recurrent effusion", "symptomatic pleural effusion", "large pleural effusion", "recurrent malignant effusion"],
    "side_tuple": [("right", "Right"), ("left", "Left")],
    "ics": ["6th", "7th", "8th", "9th"],
    "axillary_line": ["mid-axillary line", "posterior-axillary line"],
    "catheter_size": ["8Fr", "10Fr", "12Fr", "14Fr"],
    "fluid_volume": [str(x) for x in range(400, 1800, 25)],
    "fluid_appearance": ["serous", "serosanguinous", "straw-colored", "cloudy yellow"],
    "lidocaine_vol": ["5", "10", "15", "20"],
    "suction_pressure": ["-20", "-15", "-10", "-25"]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
# CONVERT USER'S NOTE INTO f-string TEMPLATE
note_template = """NOTE_ID: {note_id}
SOURCE_FILE: {note_id}.txt

INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: [Date]

INDICATION FOR OPERATION
The patient is a {age}-year-old {gender_long} who presents with {indication}.

CONSENT
The nature, purpose, risks, benefits, and alternatives to the procedure were discussed with the patient in detail. The patient wished to proceed and informed consent was obtained.

PREOPERATIVE DIAGNOSIS
{indication_title}

POSTOPERATIVE DIAGNOSIS
{indication_title}

PROCEDURE
Ultrasound, chest (includes mediastinum), real time with image documentation (CPT 76604)
Insert catheter pleura with imaging (chest tube) (CPT 32557)

ATTENDING
{doctor}

ANESTHESIA
Local ONLY: Lidocaine 1% ({lidocaine_vol} ml)

ESTIMATED BLOOD LOSS
Minimal

COMPLICATIONS
None

PROCEDURE IN DETAIL
Chest Ultrasound
Bedside ultrasound was performed on the {side} hemithorax.
Pleural Effusion: Large volume, anechoic echogenicity.
Loculations: None.
Diaphragmatic Motion: Normal.
Lung: Sliding was present before and after the procedure. Lung consolidation/atelectasis was present.
Pleura: Normal.
Images were saved and uploaded to the media tab.

Catheter Placement
The insertion site at the {side} {ics} intercostal space, {axillary_line}, was prepped and draped in a sterile fashion.
Local anesthesia was administered.
A {catheter_size} pigtail catheter was inserted using the Seldinger technique.
Entry into the pleural space was confirmed with the easy removal of minimal {fluid_appearance_short} appearing pleural fluid.
A guidewire was inserted using the introducer needle pointed in the apical posterior direction, and the introducer needle was removed.
A dilator was inserted over the wire with a twisting motion to form a tract for catheter insertion.
The dilator was removed and the pigtail catheter (with trochar) was advanced over the guidewire.
The catheter was inserted until all catheter holes were well within the chest.
The guidewire and trochar were removed.

Drainage and Securement
The tube was attached to a Pleurovac collection drain apparatus.
Fluid Removed: {fluid_volume} ml of {fluid_appearance} fluid.
Suction: Applied at {suction_pressure} cmH2O.
Securement: The catheter was sutured in place and covered.

SPECIMENS
None

IMPRESSION / PLAN
The patient tolerated the procedure well with no immediate complications.
Post-procedure chest x-ray ordered.
Continue chest tube to {suction_pressure} cmH2O suction.
Maintain strict I/O.
Daily chest x-ray while chest tube is in place.
Nursing chest tube flushing protocol.
Continued care per primary team; disposition to ICU.
"""

# CREATE 5 DISTINCT PROMPT STYLES
prompt_styles = [
    # Style 1: Telegraphic / Brief
    "Generate IP procedure note. {age}yo {gender_short}. {indication}. Dr. {doctor}. US guided pigtail {catheter_size} placed {side} {ics} ICS. {fluid_volume}ml {fluid_appearance} drained.",
    
    # Style 2: Dictation Style
    "Please draft an operative report for Dr. {doctor}. Patient is a {age} year old {gender_long} with {indication}. We did a bedside ultrasound and placed a {catheter_size} chest tube on the {side} side at the {ics} intercostal space. Drained {fluid_volume} ccs of {fluid_appearance} fluid. Suction at {suction_pressure}.",
    
    # Style 3: Sloppy / Rapid
    "{age} {gender_short}, {indication}. placed {catheter_size} pigtail {side} side. {axillary_line}. {fluid_volume}ml out. {doctor} attending. no complications.",
    
    # Style 4: Billing / CPT Focus
    "CPT 32557, 76604. Dx: {indication_title}. Attending: {doctor}. Patient: {age}/{gender_short}. Procedure: {side} sided chest tube, {catheter_size}, {ics} ICS. Output: {fluid_volume}ml.",
    
    # Style 5: Structured Request
    "PROCEDURE: Chest Tube Placement\nPATIENT: {age} {gender_short}\nINDICATION: {indication}\nSIDE: {side}\nCATHETER: {catheter_size}\nFLUID: {fluid_volume}ml {fluid_appearance}\nDOCTOR: {doctor}"
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
        side_tup = random.choice(data_pool["side_tuple"])
        ics = random.choice(data_pool["ics"])
        ax_line = random.choice(data_pool["axillary_line"])
        cat_size = random.choice(data_pool["catheter_size"])
        vol = random.choice(data_pool["fluid_volume"])
        app = random.choice(data_pool["fluid_appearance"])
        lido = random.choice(data_pool["lidocaine_vol"])
        suction = random.choice(data_pool["suction_pressure"])
        
        # Derived formatting
        # Indication title needs to be Title Case for Diagnosis section
        indication_title = indication.title()
        # Short appearance for the "minimal serous appearing" line
        # If it's "cloudy yellow", we just say "cloudy" or "serous" for the entry confirmation
        app_short = app.split()[0] 

        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_tup[1], 
            gender_long=gender_tup[0],
            doctor=doctor, 
            indication=indication,
            indication_title=indication_title,
            side=side_tup[0],
            ics=ics,
            axillary_line=ax_line,
            catheter_size=cat_size,
            fluid_volume=vol,
            fluid_appearance=app,
            suction_pressure=suction
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            age=age, 
            gender_long=gender_tup[0], 
            indication=indication,
            indication_title=indication_title,
            doctor=doctor,
            lidocaine_vol=lido,
            side=side_tup[0], # "right" or "left" lowercase for mid-sentence
            ics=ics,
            axillary_line=ax_line,
            catheter_size=cat_size,
            fluid_appearance_short=app_short,
            fluid_volume=vol,
            fluid_appearance=app,
            suction_pressure=suction
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