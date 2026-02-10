import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_013"
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
    "age": ["22", "29", "33", "38", "45", "51", "64", "72"],
    "gender_tuple": [("female", "F"), ("male", "M")],
    "start_time": ["1439", "0915", "1030", "1300", "0845", "1120"],
    "stop_time_delta": [45, 60, 83, 90, 110],  # Minutes to add to start time
    "diagnosis_main": ["Aspergilloma", "Invasive Aspergillosis", "Fungal Ball", "Mycetoma"],
    "secretion_type": ["bloody", "mucopurulent", "thick tan", "purulent", "serosanguinous"],
    "antifungal_drug": ["Amphotericin", "Voriconazole", "Amphotericin B Liposomal"],
    "antifungal_dose": ["30mg", "40mg", "50mg", "100mg"],
    "volume": ["10cc", "20cc", "40cc"],
    
    # LOGIC MAPPING: Lobe -> Segments -> Uniblocker Position
    # Structure: (Lobe Name, Segment 1, Segment 2, Uniblocker Position)
    "anatomy_map": [
        ("Left Upper Lobe (LUL)", "apico-posterior (LB1/2)", "anterior (LB3)", "Left Mainstem Bronchus (LMSB)"),
        ("Right Upper Lobe (RUL)", "apical (RB1)", "posterior (RB2)", "Right Mainstem Bronchus (RMSB)"),
        ("Right Lower Lobe (RLL)", "superior (RB6)", "posterior basal (RB10)", "Right Mainstem Bronchus (RMSB)"),
        ("Left Lower Lobe (LLL)", "superior (LB6)", "posterior basal (LB10)", "Left Mainstem Bronchus (LMSB)")
    ]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
note_template = """NOTE_ID: {note_id}
SOURCE_FILE: {note_id}.txt

INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: [Date]
INDICATION FOR OPERATION
[REDACTED] is a {age}-year-old {gender_long} who presents with respiratory failure and {diagnosis}.

The nature, purpose, risks, benefits, and alternatives to Bronchoscopy were discussed with the patient in detail.

CONSENT
Obtained before the procedure. Indications, potential complications, and alternatives were discussed with the patient or surrogate.
The patient or surrogate read and signed the provided consent form or provided consent over the phone.
The consent was witnessed by an assisting medical professional.

PREOPERATIVE DIAGNOSIS
J96.90 Respiratory Failure
{diagnosis}

POSTOPERATIVE DIAGNOSIS
J96.90 Respiratory Failure
{diagnosis}

PROCEDURE
Therapeutic aspiration initial episode (CPT 31645)
Therapeutic injection(s) [eg, chemotherapy denervation agent or corticosteroid] (CPT 31573)

ANESTHESIA
Moderate Sedation: Initial 15 minutes (99152);
each additional 15 minutes (99153). Total Time: {total_minutes} minutes (Start: {start_time}; Stop: {stop_time}).

Medications:
Etomidate {etomidate_dose} mg
Rocuronium {roc_dose} mg
Dexmedetomidine gtt 1 mcg/kg/hr
Propofol gtt 40 mcg/kg/min
Fentanyl gtt 150 mcg/hr

MONITORING
Pulse oximetry, heart rate, telemetry, and blood pressure were continuously monitored by an independent trained observer throughout the procedure.
The patient was monitored continuously one-to-one throughout the entire procedure by the attending physician while anesthesia was administered.

INSTRUMENTATION
Disposable Bronchoscope.

ESTIMATED BLOOD LOSS
None.

COMPLICATIONS
None.

PROCEDURE IN DETAIL
After the successful induction of anesthesia, a timeout was performed confirming the patient's name, procedure type, and procedure location.

Patient Position: Supine

Initial Airway Inspection
The bronchoscope was introduced through the tracheostomy tube.

Tracheostomy: Tube is in good position.
Upper Airway: Pharynx, Larynx, and Vocal Cords were not assessed due to introduction through tracheostomy tube.
Trachea: Distal 1/3 normal.
Carina: Sharp.
Proximal Airways: Right and Left lung proximal airways showed normal anatomic branching to the segmental level.
Mucosa: Normal.
Secretions: Moderate {secretion_type} secretions.

Additional Findings: Uniblocker in place (deflated) at the {uniblocker_loc}.

Therapeutic Aspiration
Successful therapeutic aspiration was performed to clean out mucus, blood, and blood clots from the following segments:
Trachea (Distal 1/3)
Right Mainstem, Bronchus Intermedius, RUL Carina (RC1), RML Carina (RC2)
Left Mainstem, Left Carina (LC2), LUL Lingula Carina (Lc1)

Therapeutic Injection
{drug} {dose} in {volume} sterile water was instilled into the {target_lobe} as follows:
{half_vol} into the {seg1} subsegment
{half_vol} into the {seg2} subsegment

Completion
The patient tolerated the procedure well.
There were no immediate complications. At the conclusion of the operation, the patient was in stable condition.

SPECIMENS
None.

IMPRESSION / PLAN
{age}-year-old {gender_long} presented for bronchoscopy for instillation of {drug}.
{target_lobe_short} {drug} instillation successfully performed.
Patient tolerated the procedure well; no immediate complications.
Continued care per primary team.
Repeat instillation of {drug} planned.
"""

# 5 Prompt Styles
prompt_styles = [
    # Style 1: Telegraphic
    "Gen IP Report. {age}{gender_short}, {diagnosis}. Trach present. Inj {drug} {dose} to {target_lobe_short}. Secretions {secretion_type}. No comps.",
    
    # Style 2: Dictation
    "Please generate an operative note for a {age} year old {gender_long} with {diagnosis}. We accessed via trach. Found {secretion_type} secretions. We performed therapeutic aspiration and then injected {drug} {dose} into the {target_lobe_short}. Patient stable.",
    
    # Style 3: Sloppy / Quick
    "{age}yo {gender_short} bronch. dx {diagnosis}. uniblocker in {uniblocker_loc}. instilled {drug} into {target_lobe_short} ({seg1}, {seg2}). everything went fine.",
    
    # Style 4: Billing Focus
    "Procedure CPT 31645, 31573. Diagnosis J96.90, {diagnosis}. Patient {age} {gender_short}. Intervention: Injection of {drug} into {target_lobe_short}.",
    
    # Style 5: Structured
    "Patient: {age} {gender_short}\nIndication: {diagnosis}\nAirway: Tracheostomy\nProcedure: Injection of {drug} ({dose})\nTarget: {target_lobe}\nFindings: {secretion_type} secretions"
]

# ==========================================
# 4. GENERATOR LOGIC
# ==========================================
def generate_dataset():
    dataset = []
    
    for _ in range(NUM_SAMPLES):
        # A. Randomly select independent variables
        age = random.choice(data_pool["age"])
        gender_tup = random.choice(data_pool["gender_tuple"])
        diagnosis = random.choice(data_pool["diagnosis_main"])
        secretion_type = random.choice(data_pool["secretion_type"])
        drug = random.choice(data_pool["antifungal_drug"])
        dose = random.choice(data_pool["antifungal_dose"])
        volume = random.choice(data_pool["volume"])
        
        # B. Handle Time Math
        start_str = random.choice(data_pool["start_time"])
        duration = random.choice(data_pool["stop_time_delta"])
        
        # Simple math to calculate stop time string (approximate)
        start_h = int(start_str[:2])
        start_m = int(start_str[2:])
        total_m = start_m + duration
        end_h = start_h + (total_m // 60)
        end_m = total_m % 60
        stop_str = f"{end_h:02d}{end_m:02d}"
        
        # C. Handle Logic-Dependent Variables (Anatomy)
        # Select a target lobe, which dictates segments and uniblocker position
        anat_config = random.choice(data_pool["anatomy_map"])
        target_lobe = anat_config[0]
        seg1 = anat_config[1]
        seg2 = anat_config[2]
        uniblocker_loc = anat_config[3]
        
        # Create short forms and derived values
        target_lobe_short = target_lobe.split("(")[1].replace(")", "") # Extracts LUL, RUL, etc.
        
        # Handle volume splitting string (e.g., "20cc" -> "10cc")
        try:
            vol_int = int(''.join(filter(str.isdigit, volume)))
            half_vol = f"{vol_int // 2}cc"
        except:
            half_vol = "half volume"

        # Randomized meds variation
        etomidate_dose = random.choice(["20", "30", "40"])
        roc_dose = random.choice(["50", "60", "100"])

        # D. Generate Prompt
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_tup[1], 
            gender_long=gender_tup[0],
            diagnosis=diagnosis,
            drug=drug,
            dose=dose,
            target_lobe=target_lobe,
            target_lobe_short=target_lobe_short,
            secretion_type=secretion_type,
            uniblocker_loc=uniblocker_loc,
            seg1=seg1,
            seg2=seg2
        )
        
        # E. Generate Completion
        completion = note_template.format(
            note_id=NOTE_ID,
            age=age,
            gender_long=gender_tup[0],
            diagnosis=diagnosis,
            total_minutes=duration,
            start_time=start_str,
            stop_time=stop_str,
            etomidate_dose=etomidate_dose,
            roc_dose=roc_dose,
            secretion_type=secretion_type,
            uniblocker_loc=uniblocker_loc,
            drug=drug,
            dose=dose,
            volume=volume,
            target_lobe=target_lobe,
            target_lobe_short=target_lobe_short,
            half_vol=half_vol,
            seg1=seg1,
            seg2=seg2
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