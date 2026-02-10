import json
import random
import os
import datetime

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_074" 
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
    "age": ["34", "37", "41", "45", "52", "58", "63", "67", "72", "75"],
    "gender_tuple": [("female", "F", "She", "Her"), ("male", "M", "He", "His")],
    "doctor": ["Dr. Ingraham", "Dr. Bowers", "Dr. Chen", "Dr. Smith", "Dr. Miller", "Dr. Jones", "Dr. Al-Fayed", "Dr. Weiss"],
    "fellow": ["Dr. Stevens", "Dr. Gupta", "Dr. Lee", "Dr. Hernandez"],
    "date_offset": range(1, 300), # Days to subtract for random dates
    
    # Clinical Variables - Obstruction
    "indication": [
        "tumor obstruction", "malignant airway stenosis", "recurrent granulation tissue", 
        "extrinsic compression with endobronchial invasion", "carcinoid tumor obstruction"
    ],
    "obstruction_site": [
        "Left Mainstem", "Right Mainstem", "Trachea", "Bronchus Intermedius", "Right Lower Lobe", "Left Lower Lobe"
    ],
    "obstruction_pct": ["80", "85", "90", "95", "99", "100"],
    
    # Clinical Variables - Treatment Modalities
    "modality_1": [
        ("Electrocautery: Knife (PreciSect)", "electrocautery knife"),
        ("Electrocautery: Snare", "hot snare"),
        ("APC (Argon Plasma Coagulation)", "APC"),
        ("Laser: Nd:YAG", "laser ablation")
    ],
    "modality_2": [
        ("Microwave: Mini probe (90°C)", "microwave ablation"),
        ("Cryotherapy: Spray", "cryospray"),
        ("Cryotherapy: Probe", "cryoprobe"),
        ("Mechanical Debridement", "mechanical debulking")
    ],
    
    # Stent Details
    "stent_info": [
        ("Bonastent", "10x20"), ("Bonastent", "12x40"), 
        ("AERO", "14x40"), ("Ultraflex", "12x20"), 
        ("Silicone Y-Stent", "14x12x12")
    ],
    "stent_loc_target": [
        ("LLL basal subsegment", "LC2"),
        ("RLL basal subsegment", "RC1"),
        ("LMS mid-distal", "LC1"),
        ("RMS distal", "RC2")
    ],
    "jailed_segment": ["LB6", "RB6", "LB10", "RB10", "LB4", "RML"],
    
    # BAL Details
    "bal_location": [
        "Superior Segment of Lingula (LB4) and Inferior Segment of Lingula (LB5)",
        "Right Middle Lobe (RML)",
        "Right Lower Lobe (RLL)",
        "Left Upper Lobe (LUL)",
        "Left Lower Lobe (LLL)"
    ],
    "fluid_return": [("20", "10"), ("30", "15"), ("50", "20"), ("20", "5"), ("40", "25")]
}

# ==========================================
# 3. TEMPLATES
# ==========================================

# The template mimics the structure of source note_074 exactly
note_template = """NOTE_ID: {note_id}
DATE OF PROCEDURE: {date_str} CC Referred Physician: {referring_doc}

INDICATION FOR OPERATION {patient_name} is a {age}-year-old {gender_long} who presents with {indication}.
The nature, purpose, risks, benefits, and alternatives to Bronchoscopy were discussed with the patient in detail.
CONSENT Obtained before the procedure. Indications, potential complications, and alternatives were discussed with the patient or surrogate.
Consent was signed and witnessed by an assisting medical professional.
PREOPERATIVE DIAGNOSIS

J98.09 Other diseases of bronchus, not elsewhere classified 

POSTOPERATIVE DIAGNOSIS

J98.09 Other diseases of bronchus, not elsewhere classified 

PROCEDURE

31645 Therapeutic aspiration initial episode 

31624 Dx bronchoscope/lavage (BAL) 

31636 Dilate and bronchial stent initial bronchus 

31641 Destruction of tumor OR relief of stenosis by any method other than excision (eg. laser therapy, cryotherapy) 

Rigid Bronchoscopy 

ATTENDING {attending}

ASSISTANT {fellow}

SUPPORT STAFF RN: [Name] RT: [Name]

ANESTHESIA General Anesthesia 

MONITORING Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.
INSTRUMENTATION Rigid Bronchoscope; Flexible Therapeutic Bronchoscope.

ESTIMATED BLOOD LOSS None 

COMPLICATIONS None 

PROCEDURE IN DETAIL After the successful induction of anesthesia, a timeout was performed (confirming the patient's name, procedure type, and procedure location).
Patient Position: [Supine] 

Initial Airway Inspection Findings: Rigid Black ventilating scope was used to intubate the patient.
Successful therapeutic aspiration was performed to clean out the Right Mainstem, Bronchus Intermedius, and Left Mainstem from mucus.
Endobronchial Tumor Destruction Endobronchial obstruction at the {obs_site} ({obs_pct}% obstruction) was treated with the following modalities:


{mod_1_formal} for 10 seconds; removed.


{mod_2_formal} for 2 min and 1.5 min; ablated.
Prior to treatment, affected airway was noted to be 0% patent. After treatment, the airway was 100% patent.
Therapeutic Aspiration Successful therapeutic aspiration was performed to clean out the {stent_loc_desc} subsegments from mucus.
Airway Stent Placement The following stent ({stent_brand} {stent_size}) was placed in the {stent_loc_desc} to the {stent_target}.
The stent was placed jailing {jailed_seg} (origin of the tumor).
Bronchoalveolar Lavage (BAL) Bronchial alveolar lavage was performed at the {bal_loc}.
Instilled {instilled} cc of NS, suction returned with {returned} cc of NS. Samples sent for Microbiology (Cultures/Viral/Fungal).
The patient tolerated the procedure well. There were no immediate complications.
At the conclusion of the operation, the patient was extubated in the operating room and transported to the recovery room in stable condition.
SPECIMENS

Tumor from {obs_site_short} 

BAL 

IMPRESSION / PLAN

{patient_name} is a {age}-year-old {gender_long} who presents for bronchoscopy for endobronchial obstruction.
Follow-up in clinic.

Follow-up in 4-6 weeks post-procedure for stent check.

Start stent hydration protocol.
"""

# Prompt styles to simulate different doctor inputs
prompt_styles = [
    # Style 1: Telegraphic / Short
    "Rigid bronch for {age}yo {gender_short}. {obs_site} tumor ({obs_pct}%) treated with {mod_1_casual} and {mod_2_casual}. Placed {stent_brand} stent. BAL {bal_short}. No comps.",
    
    # Style 2: Dictation / Narrative
    "Please generate a rigid bronchoscopy report. Patient is a {age} year old {gender_long} with {indication}. We found a {obs_pct}% obstruction in the {obs_site}. Used {mod_1_casual} and {mod_2_casual} to open it. Placed a {stent_brand} {stent_size} stent in the {stent_loc_desc}. Also did a BAL of the {bal_short}.",
    
    # Style 3: Sloppy / Quick Note
    "{age} {gender_short}, {indication}. {obs_site} completely blocked. Debulked w/ {mod_1_casual} + {mod_2_casual}. {stent_brand} stent placed. BAL done. Pt stable.",
    
    # Style 4: Billing & Coding Focus
    "Post-op diagnosis J98.09. Procedures: Rigid bronch, destruction of tumor ({mod_1_casual}), stent placement ({stent_brand}), BAL. Site: {obs_site} ({obs_pct}%). Patient {age} {gender_short}.",
    
    # Style 5: Structured Request
    "Patient: {age} {gender_short}\nDiagnosis: {indication}\nFinding: {obs_site} tumor, {obs_pct}%\nIntervention: {mod_1_casual}, {mod_2_casual}, {stent_brand} stent ({stent_loc_desc})\nBAL: {bal_short}"
]

# ==========================================
# 4. GENERATOR LOGIC
# ==========================================
def generate_dataset():
    dataset = []
    
    for i in range(NUM_SAMPLES):
        # A. Randomly select variables
        age = random.choice(data_pool["age"])
        gender_tup = random.choice(data_pool["gender_tuple"]) # (long, short, He/She, His/Her)
        gender_long = gender_tup[0]
        gender_short = gender_tup[1]
        
        attending = random.choice(data_pool["doctor"])
        fellow = random.choice(data_pool["fellow"])
        referring = random.choice(["Self", "Referred"] + data_pool["doctor"])
        
        # Date logic
        today = datetime.date.today()
        date_obj = today - datetime.timedelta(days=random.choice(data_pool["date_offset"]))
        date_str = date_obj.strftime("%m/%d/%Y")
        
        # Clinical Details
        indication = random.choice(data_pool["indication"])
        obs_site = random.choice(data_pool["obstruction_site"])
        # Create a short version of obs_site for the SPECIMENS section
        obs_site_short = "".join([word[0] for word in obs_site.split()]).upper() # e.g., Left Mainstem -> LM
        
        obs_pct = random.choice(data_pool["obstruction_pct"])
        
        mod1 = random.choice(data_pool["modality_1"])
        mod2 = random.choice(data_pool["modality_2"])
        
        stent = random.choice(data_pool["stent_info"])
        stent_loc = random.choice(data_pool["stent_loc_target"])
        jailed = random.choice(data_pool["jailed_segment"])
        
        bal_loc = random.choice(data_pool["bal_location"])
        # Short BAL for prompt
        bal_short = bal_loc.split('(')[0].strip() if '(' in bal_loc else bal_loc
        
        fluid = random.choice(data_pool["fluid_return"])
        
        patient_name = "[REDACTED]"

        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_short, 
            gender_long=gender_long,
            indication=indication,
            obs_site=obs_site,
            obs_pct=obs_pct,
            mod_1_casual=mod1[1],
            mod_2_casual=mod2[1],
            stent_brand=stent[0],
            stent_size=stent[1],
            stent_loc_desc=stent_loc[0],
            bal_short=bal_short
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            date_str=date_str,
            referring_doc=referring,
            patient_name=patient_name,
            age=age,
            gender_long=gender_long,
            indication=indication,
            attending=attending,
            fellow=fellow,
            obs_site=obs_site,
            obs_pct=obs_pct,
            mod_1_formal=mod1[0],
            mod_2_formal=mod2[0],
            stent_loc_desc=stent_loc[0],
            stent_target=stent_loc[1],
            stent_brand=stent[0],
            stent_size=stent[1],
            jailed_seg=jailed,
            bal_loc=bal_loc,
            instilled=fluid[0],
            returned=fluid[1],
            obs_site_short=obs_site_short
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