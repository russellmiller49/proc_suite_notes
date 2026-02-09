import json
import random
import os
import datetime

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_004"
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
    "age": ["62", "65", "68", "71", "74", "79", "82", "55"],
    "gender_tuple": [("female", "F", "She"), ("male", "M", "He")],
    "doctor": ["Ingraham", "Bowers", "Chen", "Smith", "Miller", "Patel", "Weiss"],
    
    # Clinical Indications
    "indication_dx": [
        ("R91.8 Other nonspecific abnormal finding of lung field", "abnormal CT chest"),
        ("J18.9 Pneumonia, unspecified organism", "persistent infiltrates on CXR"),
        ("R04.2 Hemoptysis", "episode of hemoptysis"),
        ("D70.9 Neutropenia, unspecified", "neutropenic fever")
    ],

    # Sedation details
    "versed_mg": ["1", "2", "3", "4"],
    "fentanyl_mcg": ["50", "75", "100", "125"],
    
    # Bronchoscopy Findings
    "airway_finding": [
        "The RML was fishmouthed. The mucosa appeared normal.",
        "Mild erythema was noted throughout the tracheobronchial tree.",
        "Copious thick white secretions were noted bilaterally.",
        "The airways appeared structurally normal with pale mucosa.",
        "Compression of the RML bronchus was noted from extrinsic mass effect."
    ],
    
    # Anatomy for BAL/Aspiration (Segment Name, Segment Code)
    "segments": [
        ("Posterior Segment of RUL", "RB2"),
        ("Apical Segment of RUL", "RB1"),
        ("Apical-Posterior Segment of LUL", "LB1/2"),
        ("Superior Segment of RLL", "RB6"),
        ("Lateral Basal Segment of LLL", "LB9"),
        ("Lingula", "LB4/5")
    ],
    
    # Modifiers
    "fluids": ["NS", "Saline"],
    "instilled_vol": [60, 80, 100, 120],
    "return_ratio": [0.2, 0.3, 0.4] # To calculate return volume dynamically
}

# ==========================================
# 3. TEMPLATES
# ==========================================

note_template = """NOTE_ID:  {note_id} SOURCE_FILE: {note_id}.txt INDICATION FOR OPERATION:  [REDACTED]is a {age} year old-year-old {gender_long} who presents with {indication_text}.  The nature, purpose, risks, benefits and alternatives to Bronchoscopy were discussed with the patient in detail.  Patient indicated a wish to proceed with surgery and informed consent was signed.
 
CONSENT : Obtained before the procedure. Its indications and potential complications and alternatives were discussed with the patient or surrogate. The patient or surrogate read and signed the provided consent form / provided consent over the phone. The consent was witnessed by an assisting medical professional.
 
PREOPERATIVE DIAGNOSIS: {dx_code}.
 
POSTOPERATIVE DIAGNOSIS:  {dx_code}.
 
PROCEDURE:  
31645 Therapeutic aspiration initial episode
31624 Dx bronchoscope/lavage (BAL)     
32555 - pt with pleural fluid on CT and unclear source of fevers
 
50 Bilateral Procedures (Procedure done on both sides of the body) and 73 Like 53, but the procedure was not started
 
IP [REDACTED] CODE MOD DETAILS: 
Unusual Procedure:
This patient required a bilateral procedure today when this procedure would typically be unilateral. Apply to: 31624 Dx bronchoscope/lavage (BAL)    . BAL performed in the {seg1_name} and {seg2_name} due to neutropenic fever and concern for infectious etiology or two synchronous processes
 
 
ANESTHESIA: 
99152 Moderate sedation: initial 15 minutes
 
Procedure performed under moderate sedation.  
 
The following medications were provided:
Versed             {versed} mg
Fentanyl          {fentanyl} mcg
 
Physician/patient face-to-face anesthesia start time:   {start_time}
 
Physician/patient face-to-face anesthesia stop time:   {stop_time}
 
Total moderate sedation time was {duration} minutes.  
 
Patient was monitored continuously one-to-one throughout the entire procedure by the attending physician while anesthesia was administered 
 
MONITORING : Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.
 
INSTRUMENT : 
Disposable Bronchoscope
 
ESTIMATED BLOOD LOSS:   None
 
COMPLICATIONS:    None
 
PROCEDURE IN DETAIL:
 
A timeout was performed (confirming the patient's name, procedure type, and procedure location).   
 
PATIENT POSITION: supine
 
Initial Airway Inspection Findings:
 
The bronchoscope was introduced into the mouth and advanced to the level of the vocal cords. A total of 6 mL of lidocaine was applied to the vocal cords. The bronchoscope was advanced to through the vocal cords into the trachea. The airways were examined to the subsegmental level bilaterally. 
 
{airway_finding}
 
Successful therapeutic aspiration was performed to clean out the {seg2_code} and {seg1_code} from mucus plug. 
 
Bronchial alveolar lavage was performed at {seg1_name} ({seg1_code}).  Instilled {vol1} cc of {fluid}, suction returned with {ret1} cc of {fluid}.  Samples sent for Cell Count, Microbiology (Cultures/Viral/Fungal), and Cytology.
 
Bronchial alveolar lavage was performed at {seg2_name} ({seg2_code}).  Instilled {vol2} cc of {fluid}, suction returned with {ret2} cc of {fluid}.  Samples sent for Cell Count, Microbiology (Cultures/Viral/Fungal), and Cytology.
 
 
The patient tolerated the procedure well.  There were no immediate complications.  The bronchoscope was removed
 
SPECIMEN(S): 
BAL {seg1_code}
BAL {seg2_code}
 
IMPRESSION/PLAN: [REDACTED]is a {age} year old-year-old {gender_long} who presents for bronchoscopy for {indication_text} and to obtain specimens for cultures to help identify source of fever in neutropenic patient. 
 [ ] f/u culture"""

prompt_styles = [
    # Style 1: Telegraphic
    "Gen op report {note_id}. {age}{gender_short}, {indication_text}. Bilateral BAL ({seg1_code}, {seg2_code}) + asp. Sedation: Versed {versed}/Fent {fentanyl}. Findings: {airway_finding_short}",
    
    # Style 2: Dictation
    "Please write a bronchoscopy note for a {age}-year-old {gender_long} presenting with {indication_text}. We performed therapeutic aspiration and bilateral BALs in the {seg1_code} and {seg2_code}. Sedation used was {versed} mg Versed and {fentanyl} mcg Fentanyl. {airway_finding}",
    
    # Style 3: Sloppy / Quick
    "{age}yo {gender_short} bronch. {indication_text}. codes 31645 31624-50. bal done at {seg1_code} and {seg2_code}. airway {airway_finding_short}. no comps.",
    
    # Style 4: Billing Focus
    "Procedure Codes: 31645, 31624-50, 32555. Dx: {dx_code_short}. Patient {age} {gender_short}. Bilateral BAL performed ({seg1_name}, {seg2_name}). Sedation {duration} mins.",
    
    # Style 5: Structured
    "Patient: {age} {gender_short}\nDx: {indication_text}\nProcedures: Aspiration, Bilateral BAL ({seg1_code}, {seg2_code})\nMeds: Versed {versed}mg, Fentanyl {fentanyl}mcg\nFindings: {airway_finding}"
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
        gender_long = gender_tup[0]
        gender_short = gender_tup[1]
        
        # Clinical variables
        dx_tuple = random.choice(data_pool["indication_dx"])
        dx_code = dx_tuple[0]
        dx_code_short = dx_code.split(" ")[0]
        indication_text = dx_tuple[1]
        
        # Meds
        versed = random.choice(data_pool["versed_mg"])
        fentanyl = random.choice(data_pool["fentanyl_mcg"])
        
        # Time logic
        start_hour = random.randint(8, 16)
        start_min = random.randint(0, 59)
        duration = random.randint(15, 45)
        
        start_time_obj = datetime.datetime(2023, 1, 1, start_hour, start_min)
        end_time_obj = start_time_obj + datetime.timedelta(minutes=duration)
        
        start_time_str = start_time_obj.strftime("%H:%M")
        stop_time_str = end_time_obj.strftime("%H:%M")
        
        # Anatomy / Procedure Logic
        # Ensure we pick 2 DIFFERENT segments for bilateral logic
        selected_segments = random.sample(data_pool["segments"], 2)
        seg1 = selected_segments[0] # (Name, Code)
        seg2 = selected_segments[1]
        
        airway_finding = random.choice(data_pool["airway_finding"])
        # Create a shorter version for telegraphic prompts
        airway_finding_short = airway_finding.split(".")[0]
        
        # Fluids
        fluid = random.choice(data_pool["fluids"])
        vol1 = random.choice(data_pool["instilled_vol"])
        ret1 = int(vol1 * random.choice(data_pool["return_ratio"]))
        
        vol2 = random.choice(data_pool["instilled_vol"])
        ret2 = int(vol2 * random.choice(data_pool["return_ratio"]))
        
        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            note_id=NOTE_ID,
            age=age, 
            gender_short=gender_short, 
            gender_long=gender_long,
            indication_text=indication_text,
            dx_code_short=dx_code_short,
            versed=versed,
            fentanyl=fentanyl,
            duration=duration,
            seg1_code=seg1[1],
            seg2_code=seg2[1],
            seg1_name=seg1[0],
            seg2_name=seg2[0],
            airway_finding=airway_finding,
            airway_finding_short=airway_finding_short
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            age=age, 
            gender_long=gender_long,
            indication_text=indication_text,
            dx_code=dx_code,
            seg1_name=seg1[0],
            seg2_name=seg2[0],
            seg1_code=seg1[1],
            seg2_code=seg2[1],
            versed=versed,
            fentanyl=fentanyl,
            start_time=start_time_str,
            stop_time=stop_time_str,
            duration=duration,
            airway_finding=airway_finding,
            vol1=vol1, ret1=ret1,
            vol2=vol2, ret2=ret2,
            fluid=fluid
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