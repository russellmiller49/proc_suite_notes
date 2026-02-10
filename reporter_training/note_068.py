import json
import random
import os
import datetime

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_068"
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
    "age": ["55", "62", "65", "68", "71", "74", "79", "82"],
    "gender_tuple": [("female", "F"), ("male", "M")],
    "doctor": ["Dr. Smith", "Dr. Chen", "Dr. Rodriguez", "Dr. Patel", "Dr. Weiss", "Dr. Ingraham"],
    "assistant": ["Dr. Lee", "Dr. Jacobs", "Dr. Al-Fayed", "Dr. Thompson"],
    
    # Variations for Indication/Stent
    "stent_scenario": [
        {"loc": "RML orifice", "status": "good position"},
        {"loc": "LUL orifice", "status": "good position"},
        {"loc": "Trachea", "status": "patent with mild granulation tissue at proximal edge"},
        {"loc": "Right Mainstem", "status": "migrated slightly distally but patent"},
        {"loc": "Left Mainstem", "status": "patent with no obstruction"}
    ],

    # Variations for Obstruction & Treatment
    # Tuple: (Sites affected, Modality, Tool Description, Setting, Patency Pre->Post)
    "treatment_scenario": [
        (
            "Trachea (Distal 1/3), Right Mainstem, and Left Mainstem", 
            "APC", "2.3 mm straight probe", "Pulse effect 4", 
            "90", "100"
        ),
        (
            "Trachea (Mid 1/3) and Left Mainstem", 
            "APC", "2.3 mm straight probe", "Pulse effect 3", 
            "80", "100"
        ),
        (
            "Right Mainstem and Bronchus Intermedius", 
            "Electrocautery", "blunt probe", "Effect 30W", 
            "70", "95"
        ),
        (
            "Left Mainstem (Distal)", 
            "Laser Ablation", "Nd:YAG fiber", "20W Continuous", 
            "50", "90"
        ),
        (
            "Trachea and Carina", 
            "APC", "Side-fire probe", "Pulse effect 5", 
            "85", "100"
        )
    ],

    # Aspiration targets
    "aspiration_targets": [
        "Right Mainstem, Bronchus Intermedius, and Left Mainstem",
        "Left Lower Lobe and Right Lower Lobe",
        "Trachea and bilateral mainstems",
        "RUL and RML segments"
    ],

    # Follow up
    "plan_timing": ["4-6 weeks", "2-3 months", "1 month", "2 weeks"],
    "adjunct_therapy": ["consideration to perform PDT", "consideration for cryotherapy", "referral to radiation oncology", "no further intervention planned"]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
# Note Template
note_template = """INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: {date_str} CC Referred Physician: {ref_doc}

INDICATION FOR OPERATION {gender_long_cap} is a {age}-year-old {gender_long} who presents with a lung mass and for bronchoscopy for stent evaluation.

The nature, purpose, risks, benefits, and alternatives to Bronchoscopy were discussed with the patient in detail.

CONSENT Obtained before the procedure. Indications, potential complications, and alternatives were discussed.

PREOPERATIVE DIAGNOSIS

J98.09 Other diseases of bronchus, not elsewhere classified 

POSTOPERATIVE DIAGNOSIS

J98.09 Other diseases of bronchus, not elsewhere classified 

Endobronchial obstruction ({obstruction_sites}) 

PROCEDURE

Flexible Therapeutic Bronchoscopy 

Therapeutic aspiration (initial episode) 

Destruction of tumor OR relief of stenosis by any method other than excision ({modality}) 

ATTENDING {attending}

ASSISTANT {assistant}

SUPPORT STAFF RN: [Name] RT: [Name]

ANESTHESIA General Anesthesia 

MONITORING Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.

INSTRUMENTATION Flexible Therapeutic Bronchoscope; {modality} system.

ESTIMATED BLOOD LOSS None 

COMPLICATIONS None 

PROCEDURE IN DETAIL After the successful induction of anesthesia, a timeout was performed (confirming the patient's name, procedure type, and procedure location).

Patient Position: Supine 

Initial Airway Inspection Findings:

Stent in {stent_loc} in {stent_status}.

Therapeutic Aspiration Successful therapeutic aspiration was performed to clean out the {aspiration_targets} from mucus.

Endobronchial Obstruction / {modality} Ablation Endobronchial obstruction at the {obstruction_sites} was treated with the following modalities:

Modality: {modality}

Tool: {tool}

Setting: {setting}

Result: Ablated

Prior to treatment, affected airway was noted to be {patency_pre}% patent.

After treatment, the airway was {patency_post}% patent.

Conclusion The patient tolerated the procedure well. There were no immediate complications.

At the conclusion of the operation, the patient was extubated in the operating room and transported to the recovery room in stable condition.

SPECIMEN(S) None 

IMPRESSION / PLAN

{gender_long_cap} is a {age}-year-old {gender_long} who presented for stent evaluation; {stent_loc} stent noted in {stent_status}.

Mucus successfully aspirated from {aspiration_targets_short}.

Obstruction in {obstruction_sites_short} treated with {modality};

patency improved from {patency_pre}% to {patency_post}%.

Repeat bronchoscopy in {plan_timing}.

Follow-up in clinic with {adjunct_therapy}.
"""

# Prompt Styles
prompt_styles = [
    # Style 1: Telegraphic
    "Operative Report: {age}yo {gender_short}, ref {ref_doc}. Stent check ({stent_loc}). Found obstruction in {obstruction_sites}, treated w/ {modality} ({patency_pre}%->{patency_post}%). Aspirated {aspiration_targets_short}. Plan: repeat {plan_timing}.",
    
    # Style 2: Dictation
    "Please generate a procedure note for a {age} year old {gender_long} patient referred by {ref_doc}. We checked the stent in the {stent_loc} which was {stent_status}. We treated obstruction in the {obstruction_sites} using {modality} which improved patency from {patency_pre} percent to {patency_post} percent. Also suctioned the {aspiration_targets_short}.",
    
    # Style 3: Sloppy / Quick
    "IP bronch note. {age} {gender_short}. Stent eval {stent_loc}. {modality} used for obs in {obstruction_sites}. improved {patency_pre} to {patency_post}. {assistant} assisted. f/u {plan_timing}.",
    
    # Style 4: Billing Focus
    "Dx J98.09. Procedure: Therapeutic Bronchoscopy with {modality} destruction of stenosis. Pt {age}/{gender_short}. Locations treated: {obstruction_sites}. Patency change {patency_pre}-{patency_post}. Stent check: {stent_loc}.",
    
    # Style 5: Structured
    "Patient: {age} {gender_short}\nIndication: Stent evaluation\nFindings: Stent in {stent_loc} ({stent_status})\nIntervention: {modality} ablation of {obstruction_sites}\nOutcome: Patency {patency_pre}% -> {patency_post}%"
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
        gender_long = gender_tup[0]
        gender_short = gender_tup[1]
        
        ref_doc = random.choice(data_pool["doctor"])
        attending = "Dr. " + random.choice(["Martinez", "Kim", "O'Malley", "Gupta"]) # Static list for attending
        assistant = random.choice(data_pool["assistant"])
        
        # Stent Logic
        stent_data = random.choice(data_pool["stent_scenario"])
        
        # Treatment Logic
        # Unpack tuple: (Sites, Modality, Tool, Setting, Pre, Post)
        tx_data = random.choice(data_pool["treatment_scenario"])
        obstruction_sites = tx_data[0]
        modality = tx_data[1]
        tool = tx_data[2]
        setting = tx_data[3]
        patency_pre = tx_data[4]
        patency_post = tx_data[5]
        
        # Shorten sites for Impression section to vary wording slightly
        obstruction_sites_short = obstruction_sites.replace(" and ", ", ").replace("Trachea (Distal 1/3)", "Trachea")
        
        # Aspiration
        asp_target = random.choice(data_pool["aspiration_targets"])
        asp_target_short = asp_target.replace("Right Mainstem", "RMS").replace("Left Mainstem", "LMS").replace("Bronchus Intermedius", "BI")
        
        plan_timing = random.choice(data_pool["plan_timing"])
        adjunct = random.choice(data_pool["adjunct_therapy"])
        
        date_str = (datetime.date.today() - datetime.timedelta(days=random.randint(0, 365))).strftime("%m/%d/%Y")

        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_short=gender_short, 
            gender_long=gender_long,
            ref_doc=ref_doc,
            stent_loc=stent_data["loc"],
            stent_status=stent_data["status"],
            obstruction_sites=obstruction_sites,
            modality=modality,
            patency_pre=patency_pre,
            patency_post=patency_post,
            aspiration_targets_short=asp_target_short,
            plan_timing=plan_timing,
            assistant=assistant
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            date_str=date_str,
            ref_doc=ref_doc,
            gender_long_cap=gender_long.capitalize(),
            age=age,
            gender_long=gender_long,
            obstruction_sites=obstruction_sites,
            modality=modality,
            attending=attending,
            assistant=assistant,
            stent_loc=stent_data["loc"],
            stent_status=stent_data["status"],
            aspiration_targets=asp_target,
            tool=tool,
            setting=setting,
            patency_pre=patency_pre,
            patency_post=patency_post,
            aspiration_targets_short=asp_target_short,
            obstruction_sites_short=obstruction_sites_short,
            plan_timing=plan_timing,
            adjunct_therapy=adjunct
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