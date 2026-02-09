import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_009" 
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
    "age": ["19", "24", "29", "33", "41", "48", "55", "62"],
    "gender_tuple": [("female", "F", "She"), ("male", "M", "He")],
    "indication": [
        "airway stenosis", "tracheal stenosis", "subglottic stenosis", 
        "dyspnea with history of stent placement", "migrated airway stent"
    ],
    "stent_type": [
        "BonaStent", "Aero Stent", "Ultraflex Stent", "Dumon Stent"
    ],
    "stent_size": [
        "14x60", "12x40", "16x50", "18x60", "14x40"
    ],
    "stent_location": [
        "distal trachea", "mid-trachea", "proximal trachea", "left mainstem bronchus"
    ],
    "bal_site_tuple": [
        ("Lateral Segment of RML (RB4) and Medial Segment of RML (RB5)", "RML"),
        ("Superior Segment of LLL (LB6)", "LLL"),
        ("Anterior Segment of RUL (RB3)", "RUL"),
        ("Lingula (LB4/LB5)", "Lingula")
    ],
    "lavage_amounts": [
        ("20", "10"), ("30", "15"), ("50", "25"), ("40", "20")
    ],
    "obstruction_material": [
        "hair", "suture material", "fibrinous debris", "thick inspissated mucus"
    ],
    "apc_location": [
        "Subglottic level", "Distal Tracheal level", "Bronchial anastomosis"
    ],
    "apc_settings": [
        "Pulse 20 effect 2, flow 0.3", 
        "Pulse 30 effect 2, flow 0.5", 
        "Pulse 40 effect 3, flow 0.8",
        "Forced Coag effect 2, flow 0.3"
    ],
    "patency_pre": ["40", "50", "60", "70"],
    "patency_post": ["85", "90", "95", "100"],
    "date_offset": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
note_template = """INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT


DATE OF PROCEDURE: [Date]  INDICATION FOR OPERATION [REDACTED] is a {age}-year-old {gender_long} who presents with {indication}.
The nature, purpose, risks, benefits, and alternatives to Bronchoscopy were discussed with the patient in detail.
The patient wished to proceed and informed consent was obtained. 

CONSENT Obtained before the procedure.
Indications, potential complications, and alternatives were discussed with the patient or surrogate.
Consent was signed and witnessed by an assisting medical professional.
PREOPERATIVE DIAGNOSIS

J98.09 Other diseases of bronchus, not elsewhere classified 

POSTOPERATIVE DIAGNOSIS

J98.09 Other diseases of bronchus, not elsewhere classified 

PROCEDURE

Therapeutic aspiration (31645)

Bronchoalveolar lavage (BAL) (31624)

Endobronchial Biopsy(s) (31625)

Bronchoscopy with excision (31640)

Destruction of tumor/stenosis by method other than excision (APC) (31641)

Foreign body removal (31635)

Modifier 22: Substantially greater work than normal.
This patient required significant airway management and endobronchial {obstruction_material} removal.
This resulted in >40% increased work due to increased intensity, technical difficulty of procedure, and physical/mental effort required.
ANESTHESIA General Anesthesia 

MONITORING Pulse oximetry, heart rate, telemetry, and blood pressure were continuously monitored by an independent trained observer throughout the procedure.
INSTRUMENTATION Flexible Therapeutic Bronchoscope 

ESTIMATED BLOOD LOSS None 

COMPLICATIONS None 

PROCEDURE IN DETAIL After induction of anesthesia, a timeout was performed confirming patient identity, planned procedures, and laterality.
Initial Airway Inspection The airway was noted to be stable but with significant airway pressure.
A stent was noted to be migrated {stent_location_adv}. 

Therapeutic Aspiration Successful therapeutic aspiration was performed to clean out the Trachea (Proximal 1/3), Trachea (Middle 1/3), Trachea (Distal 1/3), Right Mainstem, Bronchus Intermedius, and Left Mainstem from mucus.
Bronchoalveolar Lavage BAL was performed in the {bal_site_long} with saline instilled and returned.
Instilled {bal_in} cc of NS, suction returned with {bal_out} cc of NS.
Samples were sent for Cell Count and Microbiology (Cultures/Viral/Fungal).

Foreign Body Removal A foreign body (stent) was visualized in the {stent_location}.
The {stent_type} ({stent_size}) was removed with forceps.

Excision of Lesion / Obstruction Endobronchial obstruction was noted and excised with mechanical debridement.
A significant amount of {obstruction_material} was noted causing endobronchial obstruction at the level of the graft, leading to mucus trapping;
these were mechanically removed with forceps.

Endobronchial Tumor Destruction (APC) Endobronchial obstruction at the {apc_location} was treated with APC.
Significant granulation tissue was noted and ablated to reduce obstruction using the following settings: 1.5mm probe, {apc_settings}, for a duration of 2-3 seconds.
Prior to treatment, affected airway was noted to be {patency_pre}% patent. After treatment, the airway was {patency_post}% patent.
The patient tolerated the procedure well. There were no immediate complications.
At the conclusion of the operation, the patient was extubated in the operating room and transported to the recovery room in stable condition.
SPECIMENS

{stent_type} {stent_size} 

BAL {bal_site_short} 

IMPRESSION / PLAN

[REDACTED] is a {age}-year-old {gender_long} who presents for bronchoscopy for {indication}.
Critical airway watch for overnight. 

Consider CPAP overnight if patient goes into respiratory failure. 

Follow-up in AM with CXR.
"""

# <--- CREATE 5 DISTINCT PROMPT STYLES HERE --->
prompt_styles = [
    # Style 1: Telegraphic
    "Gen Anesthesia Bronchoscopy. {age} {gender_short} with {indication}. Mod 22 for {obstruction_material} removal (>40% work). Removed {stent_size} {stent_type} from {stent_location}. BAL {bal_site_short}. APC used on granulation.",
    
    # Style 2: Dictation
    "Write an IP op report for a {age} year old {gender_long}. We performed therapeutic aspiration, BAL in the {bal_site_short}, and removed a migrated {stent_type} ({stent_size}). Note significant work removing {obstruction_material}, justify modifier 22. APC was used at {apc_location}. Airway improved from {patency_pre}% to {patency_post}%.",
    
    # Style 3: Sloppy / Quick
    "{age}yo {gender_short} bronch. migrated {stent_type} removal. lots of {obstruction_material} caught in graft (mod 22). APC for gran tissue. BAL {bal_site_short}. {patency_pre}->{patency_post}% patency.",
    
    # Style 4: Billing Focus
    "Codes: 31645, 31624, 31625, 31640, 31641, 31635-22. Patient {age} {gender_short}. Indication: {indication}. Documentation must support Mod 22 ({obstruction_material} removal, >40% effort). Stent removed: {stent_type} {stent_size}.",
    
    # Style 5: Structured
    "Patient: {age} {gender_short}\nIndication: {indication}\nProcedures: BAL, Biopsy, Stent Removal, APC, Excision\nFindings: Migrated {stent_type}, {obstruction_material} obstruction.\nComplications: None\nNotes: Use Mod 22 for extra work removing {obstruction_material}."
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
        indication = random.choice(data_pool["indication"])
        
        stent_type = random.choice(data_pool["stent_type"])
        stent_size = random.choice(data_pool["stent_size"])
        stent_loc = random.choice(data_pool["stent_location"])
        
        # Adverbial change for findings section (e.g., "distal trachea" -> "distally" logic, or just use location)
        # For simplicity in this regex-free generator, we will reuse the location or map simple variations if needed.
        # Here we just use the location string directly or a slight variation.
        if "distal" in stent_loc:
            stent_loc_adv = "distally"
        elif "proximal" in stent_loc:
            stent_loc_adv = "proximally"
        else:
            stent_loc_adv = f"to the {stent_loc}"

        bal_tup = random.choice(data_pool["bal_site_tuple"])
        bal_vols = random.choice(data_pool["lavage_amounts"])
        
        obstruction = random.choice(data_pool["obstruction_material"])
        apc_loc = random.choice(data_pool["apc_location"])
        apc_set = random.choice(data_pool["apc_settings"])
        
        pat_pre = random.choice(data_pool["patency_pre"])
        pat_post = random.choice(data_pool["patency_post"])

        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_tup[1], 
            gender_long=gender_tup[0],
            indication=indication,
            obstruction_material=obstruction,
            stent_size=stent_size,
            stent_type=stent_type,
            stent_location=stent_loc,
            bal_site_short=bal_tup[1],
            apc_location=apc_loc,
            patency_pre=pat_pre,
            patency_post=pat_post
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            age=age,
            gender_long=gender_tup[0],
            indication=indication,
            obstruction_material=obstruction,
            stent_location_adv=stent_loc_adv,
            bal_site_long=bal_tup[0],
            bal_in=bal_vols[0],
            bal_out=bal_vols[1],
            stent_location=stent_loc,
            stent_type=stent_type,
            stent_size=stent_size,
            apc_location=apc_loc,
            apc_settings=apc_set,
            patency_pre=pat_pre,
            patency_post=pat_post,
            bal_site_short=bal_tup[1]
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