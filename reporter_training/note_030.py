import json
import random
import os
import datetime

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_030"
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
    "age": ["45", "52", "58", "62", "65", "69", "74", "81"],
    "gender_tuple": [("female", "F"), ("male", "M")],
    "diagnosis_code": ["J96.90", "J96.00", "J96.10", "J96.21"],
    "diagnosis_text": [
        "Respiratory Failure", 
        "Acute Respiratory Failure", 
        "Chronic Respiratory Failure", 
        "Acute on Chronic Respiratory Failure"
    ],
    "trach_brand": ["Portex", "Shiley", "Bivona"],
    "trach_size": ["6.0", "7.0", "7.5", "8.0", "8.5", "9.0"],
    "sedation_meds": [
        {"versed": "2 mg", "fentanyl": "50 mcg"},
        {"versed": "3 mg", "fentanyl": "75 mcg"},
        {"versed": "4 mg", "fentanyl": "100 mcg"},
        {"versed": "5 mg", "fentanyl": "125 mcg"}
    ],
    "aspiration_locations": [
        "Right Mainstem, Bronchus Intermedius, and Left Mainstem",
        "Right Lower Lobe and Left Lower Lobe",
        "bilateral mainstems",
        "trachea and main carina",
        "distal airways bilaterally"
    ],
    "stoma_appearance": [
        "widely patent and no granulation tissue was immediately visualized",
        "patent with mild erythema but no granulation tissue",
        "patent with minimal granulation tissue at the 12 o'clock position",
        "healthy and well-healed"
    ],
    "complications": ["None.", "None.", "None.", "None.", "Transient desaturation, resolved with suctioning."]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
note_template = """NOTE_ID: {note_id} SOURCE_FILE: {note_id}.txt

INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

INDICATION FOR OPERATION [REDACTED] is a {age} year old-year-old {gender_long} who presents with tracheostomy change.
The nature, purpose, risks, benefits and alternatives to Bronchoscopy were discussed with the patient in detail.
Patient indicated a wish to proceed with surgery and informed consent was signed.

CONSENT Obtained before the procedure.
Its indications and potential complications and alternatives were discussed with the patient or surrogate.
The patient or surrogate read and signed the provided consent form / provided consent over the phone.
The consent was witnessed by an assisting medical professional.

PREOPERATIVE DIAGNOSIS

{dx_code} {dx_text}

POSTOPERATIVE DIAGNOSIS

{dx_code} {dx_text}

PROCEDURE

31899 Unlisted Procedure (Trach Change with Mature Tract or Procedure NOS)

31645 Therapeutic aspiration initial episode

31899NFJ Tracheostomy Change After Establishment of Fistula Tract;
Without an E/M Service or Other Endoscopy Procedure

31615 Visualization of windpipe (Tracheobronchoscopy through established tracheostomy incision)

ANESTHESIA

Procedure performed under moderate sedation.
Physician/patient face-to-face anesthesia start time: {start_time}.

Physician/patient face-to-face anesthesia stop time: {stop_time}.

Total moderate sedation time was {duration} minutes.
Patient was monitored continuously one-to-one throughout the entire procedure by the attending physician while anesthesia was administered.
Sedation was administered by RN.

Medications provided:

Versed {versed_dose}

Fentanyl {fentanyl_dose}

MONITORING Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.
INSTRUMENTATION Disposable Bronchoscope.

ESTIMATED BLOOD LOSS None.

COMPLICATIONS {complications}

PROCEDURE IN DETAIL After the successful induction of anesthesia, a timeout was performed (confirming the patient's name, procedure type, and procedure location).
Therapeutic Aspiration Successful therapeutic aspiration was performed to clean out the {aspiration_loc} from mucus.
Tracheostomy Tube Change Upper airway was suctioned and cleared. Endotracheal suctioning performed.
The cuff was deflated and the tracheostomy tube was easily removed.
The stoma appeared {stoma_appr}.
The new tracheostomy tube was then placed with obturator in place.
The obturator was removed, inner cannula was placed and the cuff inflated.
Percutaneous tracheostomy was changed from:

{trach_brand} cuffed Trach ISO/ID size {trach_size}mm To

{trach_brand} cuffed Trach ISO/ID size {trach_size}mm without issue.
Tracheobronchoscopy Tracheobronchoscopy was performed with insertion of bronchoscope through the tracheostomy to perform airway clearance and confirm tracheostomy position.
The patient tolerated the procedure well. There were no immediate complications.
IMPRESSION / PLAN

[REDACTED] is a {age} year old-year-old {gender_long} who presents for bronchoscopy for tracheostomy change.
f/u as outpatient for tracheostomy management.
"""

prompt_styles = [
    # Style 1: Telegraphic
    "Trach change for {age}yo {gender_short}. Dx {dx_code}. Used {trach_brand} {trach_size}. Suctioned {aspiration_loc_short}. Sedation {duration} min.",
    
    # Style 2: Dictation
    "Generate an operative report for a {age}-year-old {gender_long} with {dx_text}. We performed a trach change, replacing a size {trach_size} {trach_brand} tube. We also suctioned the {aspiration_loc_short}. Stoma was {stoma_status}.",
    
    # Style 3: Sloppy / Quick
    "{age} {gender_short} trach chg. {trach_brand} {trach_size} to same. {versed_dose} versed, {fentanyl_dose} fent. asp {aspiration_loc_short}. no comps.",
    
    # Style 4: Billing Focus
    "Procedures: 31899, 31645, 31615. Pt age {age} {gender_short}. Diagnosis {dx_code}. Sedation time {duration} mins. Meds: Versed {versed_dose}/Fentanyl {fentanyl_dose}. Change size {trach_size}.",
    
    # Style 5: Structured
    "Patient: {age} {gender_short}\nIndication: Trach Change\nDiagnosis: {dx_text}\nTube: {trach_brand} {trach_size}mm\nFindings: Suctioned {aspiration_loc_short}, Stoma {stoma_status}."
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
        dx_code = random.choice(data_pool["diagnosis_code"])
        dx_text = random.choice(data_pool["diagnosis_text"])
        trach_brand = random.choice(data_pool["trach_brand"])
        trach_size = random.choice(data_pool["trach_size"])
        meds = random.choice(data_pool["sedation_meds"])
        aspiration_loc = random.choice(data_pool["aspiration_locations"])
        stoma_appr = random.choice(data_pool["stoma_appearance"])
        complications = random.choice(data_pool["complications"])
        
        # Time Logic
        start_hour = random.randint(8, 15)
        start_minute = random.randint(0, 59)
        duration = random.choice([15, 20, 25, 30, 35, 40])
        
        start_dt = datetime.datetime(2025, 1, 1, start_hour, start_minute)
        stop_dt = start_dt + datetime.timedelta(minutes=duration)
        
        start_time_str = start_dt.strftime("%H:%M")
        stop_time_str = stop_dt.strftime("%H:%M")
        
        # Helper for short prompts
        aspiration_loc_short = "airways" if len(aspiration_loc) > 30 else aspiration_loc
        stoma_status = "patent" if "patent" in stoma_appr else "healthy"

        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_tup[1], 
            gender_long=gender_tup[0],
            dx_code=dx_code,
            dx_text=dx_text,
            trach_brand=trach_brand,
            trach_size=trach_size,
            aspiration_loc_short=aspiration_loc_short,
            duration=duration,
            versed_dose=meds["versed"],
            fentanyl_dose=meds["fentanyl"],
            stoma_status=stoma_status
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            age=age,
            gender_long=gender_tup[0],
            dx_code=dx_code,
            dx_text=dx_text,
            start_time=start_time_str,
            stop_time=stop_time_str,
            duration=duration,
            versed_dose=meds["versed"],
            fentanyl_dose=meds["fentanyl"],
            complications=complications,
            aspiration_loc=aspiration_loc,
            stoma_appr=stoma_appr,
            trach_brand=trach_brand,
            trach_size=trach_size
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