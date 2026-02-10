import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_044" 
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
    "age": ["55", "62", "67", "71", "74", "83", "88"],
    "gender_tuple": [("female", "F"), ("male", "M")],
    "doctor": ["Dr. Smith", "Dr. Rao", "Dr. Gonzalez", "Dr. Chen", "Dr. Al-Fayed", "Dr. Miller"],
    "indication": [
        "Complicated Effusion", 
        "Loculated Pleural Effusion", 
        "Empyema", 
        "Parapneumonic Effusion"
    ],
    "side": ["Left", "Right"],
    "us_volume": ["Large", "Moderate", "Moderate-to-Large"],
    "us_echo": ["Anechoic", "Complex septated", "Hyperechoic swirl", "Complex non-septated"],
    "loculations": ["Thin", "Thick", "Multiple septations"],
    "ics": ["5th", "6th", "7th", "8th"],
    "line": ["Post-axillary line", "Mid-axillary line", "Scapular line"],
    "catheter_size": ["8Fr", "10Fr", "12Fr", "14Fr"],
    "fluid_vol": ["80", "120", "150", "200", "350", "400"],
    "fluid_app": ["Serous", "Serosanguinous", "Turbid", "Cloudy", "Purulent"],
    "meds": [
        "tPA (5 mg) / DNase (5 mg)", 
        "Alteplase (10 mg) / DNase (5 mg)", 
        "tPA (10 mg) / DNase (5 mg)"
    ]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
# CONVERT USER'S NOTE INTO f-string TEMPLATE
note_template = """INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: [Date] 
INDICATION FOR OPERATION: {age}-year-old {gender_long} who presents with {indication}.
The nature, purpose, risks, benefits, and alternatives to the procedure were discussed with the patient in detail.
The patient wished to proceed and informed consent was obtained.

CONSENT: Obtained before the procedure.
Indications, potential complications, and alternatives were discussed. Consent was signed and witnessed.

PREOPERATIVE DIAGNOSIS
{indication}

POSTOPERATIVE DIAGNOSIS
{indication}

PROCEDURE
76604 Ultrasound, chest (includes mediastinum), real time with image documentation 
32557 Insert catheter pleura with imaging (chest tube) 
32561 Instillation(s), via chest tube/catheter, agent for fibrinolysis (eg, fibrinolytic agent for break up of multiloculated effusion); initial day 

ANESTHESIA: Local ONLY; Lidocaine 1%: 15 ml 
ESTIMATED BLOOD LOSS: Minimal 
COMPLICATIONS: None 

PROCEDURE IN DETAIL

Chest Ultrasound: Focused thoracic ultrasound was performed and the image was saved and uploaded to the patient's medical record.
Hemithorax: {side}
Pleural Effusion: {us_volume} volume; {us_echo} echogenicity 
Loculations: {loculations}
Diaphragmatic Motion: Normal 
Lung: Lung sliding was absent before and post-procedure. Lung consolidation/atelectasis was present.
Pleura: Thick 

Pigtail Catheter Placement: The patient was positioned supine.
The insertion site was prepped and draped in a sterile fashion.
Local anesthesia was achieved with 15 ml of Lidocaine 1%.
The entry site was identified at the {side} {ics} Intercostal Space along the {line}. A {catheter_size} catheter was selected.
A pigtail catheter was inserted using the Seldinger technique. Entry into the pleural space was confirmed with the easy removal of minimal {fluid_app} appearing pleural fluid and air bubbles.
A guidewire was inserted using the introducer needle pointed in the apical posterior direction. The introducer needle was then removed.
A dilator was then inserted over the wire with a twisting motion in order to form a tract for catheter insertion.
The dilator was removed and the pigtail catheter (with trochar) was advanced over the guidewire.
The catheter was inserted into the chest until all catheter holes were well within the chest.
The guidewire and trochar were then removed. The tube was attached to the collection drain apparatus (Pleurovac) and secured in place with suture and covered.
Suction was applied at -20cmH20.

Fluid Analysis
Volume Removed: {fluid_vol} ml 
Appearance: {fluid_app}

Fibrinolytic Therapy: Following chest tube insertion, fibrinolytic therapy was initiated.
Medication: {meds}
Dose: #1 (Initial) 

SPECIMENS: Fluid was sent for the following analysis:
LDH 
Glucose 
Total Protein 
Cholesterol 
Cell Count 
Gram Stain/Culture 
AFB 
Fungal Culture 
Cytology 

IMPRESSION/PLAN
{age}-year-old {gender_long} who presents for Chest Ultrasound, Chest tube placement, and Instillation of agents for fibrinolysis (initial).
The patient tolerated the procedure well. There were no immediate complications.

Post-procedure CXR ordered.
Unclamp chest tube in 1 hour.
Strict I/O.
Daily CXR while chest tube in place.
Nursing chest tube flushing protocol.
Disposition: Nursing Unit."""

# CREATE 5 DISTINCT PROMPT STYLES
prompt_styles = [
    # Style 1: Telegraphic / Brief
    "Generate IP procedure note. {age}yo {gender_short}. Dx: {indication}. US showed {us_volume} {us_echo} effusion on {side}. Placed {catheter_size} pigtail at {ics} ICS. {fluid_vol}ml {fluid_app} fluid drained. Started {meds}.",
    
    # Style 2: Dictation / Narrative
    "Please write an operative report for a {age}-year-old {gender_long} patient, referred by {doctor}. Patient has a {indication} on the {side} side. Ultrasound confirmed {us_volume}, {us_echo} fluid with {loculations} loculations. We inserted a {catheter_size} chest tube at the {ics} intercostal space, {line}. We drained {fluid_vol} ml of {fluid_app} fluid and instilled {meds}.",
    
    # Style 3: Sloppy / Quick Input
    "{age} {gender_short} {side} complicated effusion. US guided {catheter_size} tube placement. {ics} space. drained {fluid_vol}cc {fluid_app}. given {meds}. no complications.",
    
    # Style 4: Billing / CPT Focus
    "Procedure codes 76604, 32557, 32561. Patient {age} {gender_short}. Indication: {indication}. Site: {side} {ics} ICS. Findings: {us_volume} {us_echo} effusion. Output: {fluid_vol}ml {fluid_app}. Plan: Fibrinolytics ({meds}).",
    
    # Style 5: Structured Request
    "PATIENT: {age}/{gender_short}\nDOCTOR: {doctor}\nDIAGNOSIS: {indication}\nSIDE: {side}\nUS FINDINGS: {us_volume}, {us_echo}, {loculations}\nPROCEDURE: US-guided pigtail catheter ({catheter_size})\nFLUID: {fluid_vol}ml, {fluid_app}\nMEDS: {meds}"
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
        side = random.choice(data_pool["side"])
        us_volume = random.choice(data_pool["us_volume"])
        us_echo = random.choice(data_pool["us_echo"])
        loculations = random.choice(data_pool["loculations"])
        ics = random.choice(data_pool["ics"])
        line = random.choice(data_pool["line"])
        catheter_size = random.choice(data_pool["catheter_size"])
        fluid_vol = random.choice(data_pool["fluid_vol"])
        fluid_app = random.choice(data_pool["fluid_app"])
        meds = random.choice(data_pool["meds"])
        
        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_tup[1], 
            gender_long=gender_tup[0],
            doctor=doctor,
            indication=indication,
            side=side,
            us_volume=us_volume,
            us_echo=us_echo,
            loculations=loculations,
            ics=ics,
            line=line,
            catheter_size=catheter_size,
            fluid_vol=fluid_vol,
            fluid_app=fluid_app,
            meds=meds
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            age=age, 
            gender_long=gender_tup[0],
            indication=indication,
            side=side,
            us_volume=us_volume,
            us_echo=us_echo,
            loculations=loculations,
            ics=ics,
            line=line,
            catheter_size=catheter_size,
            fluid_vol=fluid_vol,
            fluid_app=fluid_app,
            meds=meds
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