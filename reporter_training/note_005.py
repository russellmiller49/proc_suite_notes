import json
import random
import os
import datetime

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_005"
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
    "age": [str(x) for x in range(35, 90)],
    "gender_tuple": [("Female", "F", "She", "Her"), ("Male", "M", "He", "His")],
    "doctor": ["Ingraham", "Bowers", "Chen", "Smith", "Miller", "Jones", "Doe", "Patel", "Rodriguez"],
    "dates": ["January 10", "February 14", "March 03", "April 12", "May 20", "June 05", "July 22", "August 15", "September 09", "October 30"],
    
    # Logic: (Side, Hemithorax, Intercostal Space, Bronchus, Segment 1 Name, Segment 1 Code, Segment 2 Name, Segment 2 Code)
    "side_tuple": [
        ("Left", "Left hemithorax", "Left 6th", "Left Mainstem", "Superior Segment of the Lingula", "LB4", "Anteromedial Segment of the LLL", "Lb7/8"),
        ("Right", "Right hemithorax", "Right 6th", "Right Mainstem", "Lateral Segment of the RML", "RB4", "Posterior Basal Segment of the RLL", "Rb10")
    ],
    
    "diagnosis_code": ["R91.8", "J90", "J91.8"],
    "diagnosis_text": [
        "Other nonspecific abnormal finding of lung field",
        "Pleural effusion, not elsewhere classified",
        "Pleural effusion in other conditions classified elsewhere"
    ],
    
    "fluid_volume": [str(x) for x in range(400, 2200, 50)],
    "fluid_color": ["serous", "serosanguinous", "straw-colored", "yellow", "cloudy"],
    "lidocaine_vol": ["5", "6", "7", "8", "10"],
    
    "bal_instilled": [60, 100, 120],
    # Returned volume calculated dynamically in logic to be less than instilled
}

# ==========================================
# 3. TEMPLATES
# ==========================================

# The template uses placeholders that correspond to variables generated in the loop
note_template = """INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: {date_str} PATIENT: [REDACTED] AGE/SEX: {age}-year-old {gender_long} INDICATION FOR OPERATION: Patient presents with pleural effusion and lung infiltrates.
CONSENT Obtained before the procedure. Its indications and potential complications and alternatives were discussed with the patient or surrogate.
The patient or surrogate read and signed the provided consent form or provided consent over the phone.
The consent was witnessed by an assisting medical professional. 

PREOPERATIVE DIAGNOSIS

{dx_code} {dx_text}.
POSTOPERATIVE DIAGNOSIS

{dx_code} {dx_text}.

PROCEDURE

32555 Thoracentesis with imaging guidance

31645 Therapeutic aspiration, initial episode

31624 Diagnostic bronchoscopy with bronchoalveolar lavage (BAL)

Note: This procedure required greater than 50% of time and effort that was usually needed for a similar procedure (BAL performed in multiple areas).
ANESTHESIA General Anesthesia

MONITORING Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.
INSTRUMENTATION Flexible Therapeutic Bronchoscope; Thoracentesis Kit.

ESTIMATED BLOOD LOSS None

COMPLICATIONS None

PROCEDURE IN DETAIL

After the successful induction of anesthesia, a timeout was performed (confirming the patient's name, procedure type, and procedure location).
Thoracic Ultrasound and Thoracentesis Focused thoracic ultrasound was performed. Findings for the {hemi} included:

Effusion: Large volume, anechoic echogenicity.
Loculations: None.

Lung: Lung sliding was present pre- and post-procedure; consolidation/atelectasis was present.


Diaphragm: Normal motion.
Based on ultrasound evaluation, thoracentesis was determined to be feasible. The insertion site was prepped and draped in sterile fashion.
Local anesthesia was achieved with {lido_vol} ml of Lidocaine 1%.
Entry was made at the {ics_site} Intercostal Space along the Mid-scapular line.


Fluid Removed: {fluid_vol} ml of {fluid_char} fluid.
Drainage: Performed via drainage bag.

Specimens: Samples sent for pH, LDH, Glucose, Total Protein, Cholesterol, Cell Count, Triglycerides, Gram Stain/Culture, AFB, Fungal Culture, and Cytology.
Flexible Bronchoscopy The bronchoscope was introduced, and a survey was performed.
Therapeutic Aspiration: Successful therapeutic aspiration was performed to clean out the {bronchus} from mucus.
Bronchoalveolar Lavage (BAL) - {seg1_short}: BAL was performed in the {seg1_long} ({seg1_code}) with saline instilled and returned.
Instilled {bal1_in} cc of NS, suction returned with {bal1_out} cc of NS.
Bronchoalveolar Lavage (BAL) - {seg2_short}: BAL was performed at the {seg2_long} ({seg2_code}).
Instilled {bal2_in} cc of NS, suction returned with {bal2_out} cc of NS.
Specimens: Samples from lavage were sent for Cell Count, Microbiology (Cultures/Viral/Fungal), and Cytology. 

The patient tolerated the procedure well.
There were no immediate complications. At the conclusion of the operation, the patient was extubated in the operating room and transported to the recovery room in stable condition.
SPECIMENS

{side} pleural fluid (Chemistry, Microbiology, Cytology)

BAL - {seg1_short} ({seg1_long})

BAL - {seg2_short} ({seg2_long})

IMPRESSION / PLAN

{age}-year-old {gender_short_lower} who presents for bronchoscopy for lavage and thoracentesis.
Successful drainage of {fluid_vol} ml {fluid_char} pleural fluid from the {hemi_lower}.
Successful clearance of mucus from {bronchus} and BAL of {seg1_short}/{seg2_short}.

Follow-up BAL and pleural fluid analysis (PFA) results.
Follow-up Chest X-ray (ordered)."""

prompt_styles = [
    # Style 1: Telegraphic / Brief
    "Generate op report. {age}{gender_short}, {side} effusion. Thoracentesis ({fluid_vol}ml) + Bronch/BAL ({seg1_code}, {seg2_code}). Dx: {dx_code}.",
    
    # Style 2: Dictation / Narrative
    "Write a procedure note for a {age}-year-old {gender_long}. We performed a {side} thoracentesis removing {fluid_vol} ml of {fluid_char} fluid and a diagnostic bronchoscopy with BAL of the {seg1_short} and {seg2_short}. No complications.",
    
    # Style 3: Sloppy / Quick Input
    "{age}yo {gender_short} {side} side tap and wash. drained {fluid_vol} serous. bal {seg1_code} and {seg2_code}. everything went fine.",
    
    # Style 4: Billing / Technical Focus
    "CPT 32555, 31645, 31624. Side: {side}. Vol: {fluid_vol}ml. BAL Locs: {seg1_long}, {seg2_long}. Dx: {dx_code}.",
    
    # Style 5: Structured Request
    "Patient: {age} {gender_short}\nProcedure: Thoracentesis & Bronchoscopy\nSide: {side}\nFluid: {fluid_vol}ml ({fluid_char})\nBAL Targets: {seg1_code}, {seg2_code}"
]

# ==========================================
# 4. GENERATOR LOGIC
# ==========================================
def generate_dataset():
    dataset = []
    
    for _ in range(NUM_SAMPLES):
        # A. Randomly select variables
        age = random.choice(data_pool["age"])
        gender_tup = random.choice(data_pool["gender_tuple"]) # (Long, Short, Subj, Poss)
        date_str = random.choice(data_pool["dates"])
        doctor = random.choice(data_pool["doctor"])
        
        # Side Logic - CRITICAL for anatomical consistency
        side_data = random.choice(data_pool["side_tuple"])
        # Unpack Side Data: (Side, Hemithorax, Intercostal Space, Bronchus, Seg1 Name, Seg1 Code, Seg2 Name, Seg2 Code)
        side = side_data[0]
        hemi = side_data[1]
        ics_site = side_data[2]
        bronchus = side_data[3]
        seg1_long = side_data[4]
        seg1_code = side_data[5]
        seg2_long = side_data[6]
        seg2_code = side_data[7]
        
        # Derived Side variables for display
        # Note: Seg1 short is usually LUL or RML depending on side, Seg2 is usually LLL or RLL
        seg1_short = "LUL" if side == "Left" else "RML"
        seg2_short = "LLL" if side == "Left" else "RLL"
        
        # Clinical variables
        dx_code = random.choice(data_pool["diagnosis_code"])
        dx_text = random.choice(data_pool["diagnosis_text"])
        fluid_vol = random.choice(data_pool["fluid_volume"])
        fluid_char = random.choice(data_pool["fluid_color"])
        lido_vol = random.choice(data_pool["lidocaine_vol"])
        
        # BAL Math
        bal1_in = random.choice(data_pool["bal_instilled"])
        bal1_out = int(bal1_in * random.uniform(0.3, 0.6)) # Return 30-60%
        bal2_in = random.choice(data_pool["bal_instilled"])
        bal2_out = int(bal2_in * random.uniform(0.3, 0.6))

        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_tup[1], 
            gender_long=gender_tup[0].lower(),
            side=side,
            fluid_vol=fluid_vol,
            fluid_char=fluid_char,
            seg1_code=seg1_code,
            seg2_code=seg2_code,
            seg1_short=seg1_short,
            seg2_short=seg2_short,
            seg1_long=seg1_long,
            seg2_long=seg2_long,
            dx_code=dx_code
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            date_str=date_str,
            age=age,
            gender_long=gender_tup[0],
            gender_short_lower=gender_tup[0].lower(),
            dx_code=dx_code,
            dx_text=dx_text,
            hemi=hemi,
            hemi_lower=hemi.lower(),
            lido_vol=lido_vol,
            ics_site=ics_site,
            fluid_vol=fluid_vol,
            fluid_char=fluid_char,
            bronchus=bronchus,
            seg1_short=seg1_short,
            seg1_long=seg1_long,
            seg1_code=seg1_code,
            bal1_in=bal1_in,
            bal1_out=bal1_out,
            seg2_short=seg2_short,
            seg2_long=seg2_long,
            seg2_code=seg2_code,
            bal2_in=bal2_in,
            bal2_out=bal2_out,
            side=side
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