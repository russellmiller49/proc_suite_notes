import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_029"
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
    "age": ["22", "30", "39", "45", "52", "61", "68", "74", "85", "91"],
    "gender_tuple": [("female", "F", "She"), ("male", "M", "He")],
    "side_tuple": [("Left", "LEFT"), ("Right", "RIGHT")],
    "indication": ["Pleural Effusion", "Recurrent Pleural Effusion", "Hydropneumothorax", "Suspected Empyema"],
    "catheter_size": ["8Fr", "10Fr", "12Fr", "14Fr"],
    "intercostal_space": ["4th", "5th", "6th"],
    "effusion_desc": [
        "Large volume; Anechoic echogenicity with thin loculations",
        "Moderate volume; Simple anechoic fluid",
        "Large volume; Complex septated fluid",
        "Moderate volume; Free flowing anechoic fluid"
    ],
    "fluid_vol": ["150", "300", "550", "800", "1100", "1400"],
    "fluid_color": ["serous", "sanguineous", "straw-colored", "turbid", "serosanguineous"],
    "anesthesia_vol": ["10", "15", "20", "25"],
    "complication": ["None.", "None.", "None.", "Patient reported mild pain, managed with local anesthetic."]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
# The template mirrors note_029.txt structure exactly, replacing dynamic data with variables.
note_template = """INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: [Date] INDICATION FOR OPERATION [REDACTED] is a {age}-year-old {gender_long} who presents with a {indication_lower}.
The nature, purpose, risks, benefits, and alternatives to Chest Ultrasound and Chest tube placement were discussed with the patient in detail.
The patient indicated a wish to proceed with the procedure and informed consent was signed.

CONSENT Obtained before the procedure.
Its indications, potential complications, and alternatives were discussed with the patient or surrogate.
The patient or surrogate read and signed the provided consent form or provided consent over the phone.
The consent was witnessed by an assisting medical professional.

PREOPERATIVE DIAGNOSIS

{indication}

POSTOPERATIVE DIAGNOSIS

{indication}

PROCEDURE

76604: Ultrasound, chest (includes mediastinum), real-time with image documentation.
32557: Insert catheter pleura with imaging (chest tube).

MONITORING Pulse oximetry, heart rate, telemetry, and blood pressure were continuously monitored by an independent trained observer throughout the procedure.
ANESTHESIA Local anesthesia was achieved with {lidocaine_vol} mL of Lidocaine 1%.

COMPLICATIONS {complication}

PROCEDURE IN DETAIL

Patient Position: Supine.
Focused Thoracic Ultrasound (Pleura & Lung) Focused thoracic ultrasound was performed and the image was saved and printed.
Findings were as follows:

Hemithorax: {side_normal}.

Pleural Effusion: {effusion_desc}.

Diaphragmatic Motion: Normal.
Lung: Lung sliding was present before the procedure.

Pleura: Normal.
Pigtail Catheter Placement The insertion site at the {side_normal} {ics} Intercostal Space (Mid-axillary line) was prepped and draped in sterile fashion.
A {cath_size} pigtail catheter was inserted using the Seldinger technique.
Entry into the pleural space was confirmed with the easy removal of minimal {fluid_char} appearing pleural fluid and air bubbles.
A guidewire was inserted using the introducer needle pointed in the apical posterior direction. The introducer needle was then removed.
A dilator was then inserted over the wire with a twisting motion in order to form a tract for catheter insertion.
The dilator was removed and the pigtail catheter (with trochar) was advanced over the guidewire.
The catheter was inserted into the chest until all catheter holes were well within the chest.
The guidewire and trochar were then removed. The tube was then attached to the collection drain apparatus (Pleurovac) and secured in place with suture and covered.
Procedure Findings

Fluid Removed: {fluid_vol} mL of {fluid_char} fluid.

Suction: No (Water seal).
SPECIMENS The following specimens were sent for analysis:

pH, LDH, Glucose, Total Protein, Cholesterol.

Cell Count.

Gram Stain/Culture, AFB, Fungal Culture.
Cytology.

IMPRESSION / PLAN [REDACTED] is a {age}-year-old {gender_long} who presents for Chest Ultrasound and Chest tube placement on the {side_caps}.
The patient tolerated the procedure well. There were no immediate complications.

Follow-up post-procedure Chest X-ray (ordered).

Follow-up pleural fluid studies.
Keep chest tube to water seal.

Small bore chest tube flushing q8h as per orders.
Daily Chest X-ray while chest tube is in place.

DISPOSITION Nursing Unit.
"""

# Prompt styles to map inputs to the generated note
prompt_styles = [
    # Style 1: Telegraphic / Handoff
    "Pulm procedure note: {age}yo {gender_short}, {side_normal} side {indication_lower}. Placed {cath_size} pigtail, drained {fluid_vol}cc {fluid_char}. {complication_short}",
    
    # Style 2: Dictation
    "Please generate a procedure report for a {age} year old {gender_long}. We did a chest ultrasound and chest tube placement on the {side_normal} side for {indication_lower}. Ultrasound showed {effusion_summary}. We used {lidocaine_vol}cc lido. Placed a {cath_size} catheter at the {ics} space. Got {fluid_vol} ml of {fluid_char} fluid out. Plan is water seal.",
    
    # Style 3: Sloppy / Quick
    "{side_normal} chest tube {age} {gender_short}. {indication_lower}. us guided. {fluid_vol}ml {fluid_char} output. no complications. 32557.",
    
    # Style 4: Billing Focus
    "CPT 32557 and 76604. Diagnosis: {indication}. Site: {side_normal}. Catheter: {cath_size}. Drainage: {fluid_vol}mL.",
    
    # Style 5: Structured Request
    "Patient: {age}y {gender_short}\nProcedure: Pigtail Catheter\nSide: {side_normal}\nUS Findings: {effusion_desc}\nAnesthesia: {lidocaine_vol}mL Lidocaine\nOutput: {fluid_vol}ml {fluid_char}"
]

# ==========================================
# 4. GENERATOR LOGIC
# ==========================================
def generate_dataset():
    dataset = []
    
    for _ in range(NUM_SAMPLES):
        # A. Randomly select variables
        age = random.choice(data_pool["age"])
        gender_tup = random.choice(data_pool["gender_tuple"]) # (long, short, pronoun)
        side_tup = random.choice(data_pool["side_tuple"]) # (Normal, CAPS)
        indication = random.choice(data_pool["indication"])
        cath_size = random.choice(data_pool["catheter_size"])
        ics = random.choice(data_pool["intercostal_space"])
        effusion = random.choice(data_pool["effusion_desc"])
        vol = random.choice(data_pool["fluid_vol"])
        char = random.choice(data_pool["fluid_color"])
        lido = random.choice(data_pool["anesthesia_vol"])
        comp = random.choice(data_pool["complication"])
        
        # Derived variables for prompts
        effusion_summary = "loculated fluid" if "loculations" in effusion else "anechoic fluid"
        comp_short = "No comps" if comp == "None." else "Patient had mild pain"

        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_tup[1], 
            gender_long=gender_tup[0],
            side_normal=side_tup[0],
            indication_lower=indication.lower(),
            indication=indication,
            cath_size=cath_size,
            fluid_vol=vol,
            fluid_char=char,
            complication_short=comp_short,
            effusion_summary=effusion_summary,
            lidocaine_vol=lido,
            ics=ics,
            effusion_desc=effusion
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            age=age,
            gender_long=gender_tup[0],
            indication_lower=indication.lower(),
            indication=indication,
            lidocaine_vol=lido,
            complication=comp,
            side_normal=side_tup[0],
            side_caps=side_tup[1],
            effusion_desc=effusion,
            ics=ics,
            cath_size=cath_size,
            fluid_char=char,
            fluid_vol=vol
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