import json
import random
import os
import datetime

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_031"
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
    "gender_tuple": [("female", "F", "She", "Her"), ("male", "M", "He", "His")],
    "doctor": ["Ingraham", "Bowers", "Chen", "Smith", "Miller", "Jones", "Doe", "Gupta", "Rossi"],
    "indication": [
        ("Respiratory Failure", "J96.90"),
        ("Acute Respiratory Failure", "J96.00"),
        ("Chronic Respiratory Failure", "J96.10"),
        ("Prolonged Mechanical Ventilation", "Z99.11"),
        ("Failure to Wean", "J96.90")
    ],
    "tube_type": [
        "Shiley 8.0 cuffed", 
        "Shiley 6.0 cuffed", 
        "Shiley 7.0 cuffed", 
        "Portex 8.0mm cuffed", 
        "Portex 7.0mm cuffed"
    ],
    # Maps Short Name -> (Detailed Anatomy Description, List of segments for aspiration)
    "bal_config": [
        ("Lingula", "Superior Segment of Lingula (LB4) and Inferior Segment of Lingula (LB5)", "LUL Lingula Carina"),
        ("RML", "Right Middle Lobe Medial (RB5) and Lateral (RB4) segments", "RML Carina"),
        ("RUL", "Right Upper Lobe Apical (RB1) segment", "RUL Carina"),
        ("LUL", "Left Upper Lobe Apicoposterior segment (LB1/2)", "LUL Carina")
    ],
    "secretions": [
        "Minimal, thin, and clear",
        "Scant, clear",
        "Moderate, thick, and white",
        "Moderate, yellow, and mucoid",
        "Minimal, blood-tinged"
    ],
    "sedation_time": ["90", "105", "114", "120", "135", "150"],
    "meds_combo": [
        "Etomidate 30mg, Rocuronium 80mg, Propofol gtt 50 mcg/kg/min, Fentanyl gtt 150 mcg/hr",
        "Versed 5mg, Fentanyl 100mcg, Propofol gtt 40 mcg/kg/min",
        "Propofol gtt 60 mcg/kg/min, Fentanyl gtt 200 mcg/hr, Rocuronium 50mg",
        "Etomidate 20mg, Succinylcholine 100mg, Propofol gtt 50 mcg/kg/min"
    ],
    "suture_days": ["5", "7", "10"],
    "trach_change_days": ["7", "10", "14"]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
# The full note template with dynamic placeholders
note_template = """INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: {date_str}

INDICATION FOR OPERATION: Patient is a {age}-year-old {gender_long} who presents with {indication_name}.
The nature, purpose, risks, benefits, and alternatives to Bronchoscopy were discussed with the patient in detail.
Patient indicated a wish to proceed with surgery and informed consent was signed.

CONSENT: Obtained before the procedure.
Its indications and potential complications and alternatives were discussed with the patient or surrogate.
The patient or surrogate read and signed the provided consent form or provided consent over the phone.
The consent was witnessed by an assisting medical professional.

PREOPERATIVE DIAGNOSIS: {dx_code} {indication_name}

POSTOPERATIVE DIAGNOSIS: {dx_code} {indication_name}

PROCEDURE:
31645 Therapeutic aspiration initial episode
31624 Dx bronchoscope/lavage (BAL)
31600 Incision of windpipe (perc trach)
76536 Ultrasound of Neck

ANESTHESIA: Moderate Sedation: 99152 (initial 15 minutes), 99153 (each additional 15 minutes).
Medications: {meds}. Time: Physician/patient face-to-face anesthesia start time: {start_time}; stop time: {stop_time}. Total moderate sedation time was {sedation_duration} minutes.
Staff: Patient was monitored continuously one-to-one throughout the entire procedure by the attending physician while anesthesia was administered.
Sedation was administered by ICU RN.

MONITORING: Pulse oximetry, heart rate, telemetry, and blood pressure were continuously monitored by an independent trained observer throughout the procedure.
INSTRUMENTATION: Flexible Diagnostic Bronchoscope.

ESTIMATED BLOOD LOSS: Minimum
COMPLICATIONS: None

PROCEDURE IN DETAIL: After the successful induction of anesthesia, a timeout was performed (confirming the patient's name, procedure type, and procedure location).
Patient Position: Supine

Initial Airway Inspection: The endotracheal tube is in good position.
Pharynx, larynx, and vocal cords were not assessed due to bronchoscopy introduction through ETT.

Trachea: Distal 1/3 normal.
Main Carina: Sharp.

Right Lung: Proximal airways showed normal anatomic branching to segmental level.
No evidence of mass, lesions, bleeding or other endobronchial pathology.
Left Lung: Proximal airways showed normal anatomic branching to segmental level.
No evidence of mass, lesions, bleeding or other endobronchial pathology.

Secretions: {secretions}. Mucosa was normal.
Therapeutic Aspiration: Successful therapeutic aspiration was performed to clean out the Trachea (Distal 1/3), Right Mainstem, Bronchus Intermedius, Left Mainstem, Carina, {bal_short_loc} (target), and proximal airways from mucus.
Bronchoalveolar Lavage (BAL): BAL was performed in the {bal_long_desc}.
Instilled 60 cc of NS, suction returned with 15 cc of NS.
Samples sent for Cell Count, Microbiology (Cultures/Viral/Fungal), and Cytology.

Neck Ultrasound: Neck Ultrasound was performed to evaluate for any abnormal vessel, mass, or structures at the site of percutaneous tracheostomy.
There were no significant vessels/mass noted overlying the tracheostomy site on examination from the laryngeal prominence to the sternal notch.

Percutaneous Tracheostomy: The bronchoscope was retracted into the ETT tube and the ET tube retracted into the subglottic space under direct visualization.
The inferior border of the cricoid along with the proximal tracheal rings were visualized.
Next, the anterior neck was prepped and draped in the usual sterile fashion.
Lidocaine 1% 3ml was injected into the anterior neck. A 1 cm incision was made horizontally with a #10 blade down through the subcutaneous tissue, just inferior to the cricoid cartilage.
A suture (3-0 prolene) was placed around the incision site to create a Rummel tourniquet.
The introducer needle was then passed between the 1st and 2nd tracheal rings and into the trachea under direct visualization.
Next, a J-wire was passed through the catheter, also visualized with the bronchoscope.
The site was then dilated using the 14Fr introducing dilator passed over the wire.
The 14 Fr dilator was then removed from the guide wire and an 8 Fr guiding catheter placed over the guide wire until the safety ridge on the guiding catheter was at skin level.
The tissue dilator was placed over the guiding catheter until the positioning mark was visualized via the bronchoscope.
The tissue dilator was then removed leaving the guiding catheter and guide wire assembly in place, all under direct visualization bronchoscopically.
Finally, a {tube_type} tracheostomy tube with appropriate dilator was introduced over the guiding catheter into the trachea under direct visualization.
The dilator, guiding catheter, and J-wire were then removed and the tracheostomy tube left in place.
This was confirmed to be in good position bronchoscopically. The Endotracheal tube was then removed and the ventilator connected to the tracheostomy tube.
Surgicel was placed preemptively around the tracheostomy site to reduce bleeding.
A Lyofoam drain sponge was placed under the tracheostomy tube prior to suturing into place.
The patient tolerated the procedure well. There were no complications. The staff physician was present throughout the entire procedure.
At the conclusion of the operation, the patient was in stable condition.

SPECIMENS:
{bal_short_loc} BAL (cell count, micro, cyto)

IMPRESSION / PLAN:
Patient is a {age}-year-old {gender_long} who presents for bronchoscopy and tracheostomy tube placement.
{tube_type} tracheostomy tube and Rummel tourniquet placed.

Patient tolerated the procedure well and there were no immediate complications.
Post procedure CXR.

Anticipate suture removal in {suture_days} days.
Anticipate trach change in {trach_days} days.
"""

# Prompt styles mapped to variables
prompt_styles = [
    # Style 1: Telegraphic
    "{age}yo {gender_short} {indication_name}. Perc trach {tube_short} + BAL {bal_short_loc}. {secretions_short} secretions. No comps.",
    
    # Style 2: Dictation
    "Please write an operative report for a {age} year old {gender_long} with {indication_name}. We performed a bronchoscopy with BAL of the {bal_short_loc} and percutaneous tracheostomy using a {tube_type}. Findings: {secretions} secretions.",
    
    # Style 3: Sloppy / Quick
    "perc trach {tube_short}, bal {bal_short_loc}. {age}{gender_short} dx {dx_code}. {secretions_short} secretions found. all clear on US.",
    
    # Style 4: Billing Focus
    "Procedure codes 31645, 31624, 31600. Dx {dx_code}. {tube_type} placed. {bal_short_loc} washed.",
    
    # Style 5: Structured
    "Patient: {age} {gender_short}\nIndication: {indication_name}\nProcedure: Trach ({tube_type}) + BAL ({bal_short_loc})\nFindings: {secretions}"
]

# ==========================================
# 4. GENERATOR LOGIC
# ==========================================
def generate_dataset():
    dataset = []
    
    for _ in range(NUM_SAMPLES):
        # A. Randomly select variables
        age = random.choice(data_pool["age"])
        gender_tup = random.choice(data_pool["gender_tuple"]) # (long, short, he/she, his/her)
        doctor = random.choice(data_pool["doctor"])
        indication_tup = random.choice(data_pool["indication"]) # (name, code)
        tube_type = random.choice(data_pool["tube_type"])
        tube_short = tube_type.split()[0] + " " + tube_type.split()[1] # e.g., Shiley 8.0
        
        bal_config = random.choice(data_pool["bal_config"]) # (Short, Long Desc, Target)
        secretions = random.choice(data_pool["secretions"])
        secretions_short = secretions.split(",")[0]
        
        sedation_duration = random.choice(data_pool["sedation_time"])
        meds = random.choice(data_pool["meds_combo"])
        suture_days = random.choice(data_pool["suture_days"])
        trach_days = random.choice(data_pool["trach_change_days"])
        
        # Date and Time Logic
        date_obj = datetime.date.today() - datetime.timedelta(days=random.randint(0, 365))
        date_str = date_obj.strftime("%B %d, %Y")
        
        start_hour = random.randint(8, 15)
        start_min = random.randint(0, 59)
        start_time_obj = datetime.time(start_hour, start_min)
        # Calculate stop time roughly based on sedation duration (just adding minutes for string purposes)
        # Simplified: just strings for this template, but logic makes it realistic
        stop_hour = start_hour + int(int(sedation_duration) / 60)
        stop_min = (start_min + int(sedation_duration) % 60) % 60
        start_time_str = f"{start_hour:02d}{start_min:02d}"
        stop_time_str = f"{stop_hour:02d}{stop_min:02d}"

        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_tup[1], 
            gender_long=gender_tup[0],
            indication_name=indication_tup[0],
            dx_code=indication_tup[1],
            tube_type=tube_type,
            tube_short=tube_short,
            bal_short_loc=bal_config[0],
            secretions=secretions,
            secretions_short=secretions_short
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            date_str=date_str,
            age=age,
            gender_long=gender_tup[0],
            indication_name=indication_tup[0],
            dx_code=indication_tup[1],
            meds=meds,
            start_time=start_time_str,
            stop_time=stop_time_str,
            sedation_duration=sedation_duration,
            secretions=secretions,
            bal_short_loc=bal_config[0],
            bal_long_desc=bal_config[1],
            tube_type=tube_type,
            suture_days=suture_days,
            trach_days=trach_days
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