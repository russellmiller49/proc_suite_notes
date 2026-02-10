import json
import random
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_088"
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
    "age": ["45", "52", "57", "61", "64", "68", "73", "79", "82"],
    "gender_tuple": [("female", "F"), ("male", "M")],
    "ref_physician": ["Dr. Smith", "Dr. Jones", "Dr. Chen", "Dr. Patel", "Dr. Williams", "Dr. Harken"],
    "attending": ["Dr. Ingraham", "Dr. Bowers", "Dr. Lee", "Dr. Gomez"],
    "fellow": ["Dr. Miller", "Dr. Davis", "Dr. Wilson", "Dr. Taylor"],
    "rn_name": ["Sarah", "Mike", "Jessica", "David", "Emily"],
    "rt_name": ["Tom", "Lisa", "John", "Karen", "Chris"],
    
    # Clinical Variations
    "location_data": [
        {"site": "RML", "cleaning_target": "RML Carina (RC2)"},
        {"site": "RUL", "cleaning_target": "RUL Carina (RC1)"},
        {"site": "LUL", "cleaning_target": "LUL Carina (LC1)"},
        {"site": "LLL", "cleaning_target": "LLL Carina (LC2)"},
        {"site": "RLL", "cleaning_target": "RLL Carina (RC3)"},
        {"site": "Bronchus Intermedius", "cleaning_target": "Bronchus Intermedius"},
    ],
    "pre_patent": ["10", "15", "20", "25", "30", "35"],
    "post_patent": ["90", "95", "100"],
    "secretion_type": [
        "white thicker mucus",
        "thick purulent secretions",
        "moderate bloody secretions",
        "tenacious tan mucus",
        "copious clear secretions"
    ],
    "balloon_size_1": ["5", "6"],
    "balloon_size_2": ["7", "8"],
    "follow_up": ["2 weeks", "4 weeks", "1 month", "3 weeks"]
}

# ==========================================
# 3. TEMPLATES
# ==========================================
note_template = """INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: [Date] CC Referred Physician: {ref_physician}

INDICATION FOR OPERATION [REDACTED] is a {age}-year-old {gender_long} who presents with bronchial stenosis.

The nature, purpose, risks, benefits and alternatives to Bronchoscopy were discussed with the patient in detail.

CONSENT Obtained before the procedure.

Indications, potential complications, and alternatives were discussed with the patient or surrogate.

The patient wished to proceed and informed consent was obtained.

PREOPERATIVE DIAGNOSIS

J98.09 Other diseases of bronchus, not elsewhere classified 

POSTOPERATIVE DIAGNOSIS

J98.09 Other diseases of bronchus, not elsewhere classified 

PROCEDURE

Flexible Bronchoscopy

31645 Therapeutic aspiration initial episode 

31630 Balloon dilation 

31641 Destruction of tumor OR relief of stenosis by any method other than excision (eg. laser therapy, cryotherapy) 

ATTENDING {attending}

ASSISTANT {fellow}

SUPPORT STAFF RN: {rn_name} RT: {rt_name}

ANESTHESIA General Anesthesia 

MONITORING Pulse oximetry, heart rate, telemetry, and BP were continuously monitored by an independent trained observer that was present throughout the entire procedure.

INSTRUMENTATION Flexible Therapeutic Bronchoscope; Flexible Hybrid (Pediatric) Bronchoscope; Electrocautery (Needle Knife); Cryoprobe (1.7mm); Elation Balloon (6/7/8).

ESTIMATED BLOOD LOSS Minimum 

COMPLICATIONS None 

PROCEDURE IN DETAIL After the successful induction of anesthesia, a timeout was performed (confirming the patient's name, procedure type, and procedure location).

Patient Position: [Position] Initial Airway Inspection: The laryngeal mask airway is in good position. The vocal cords appear normal.

The subglottic space is normal. The trachea is of normal caliber. The carina is sharp.

The tracheobronchial tree was examined to at least the first subsegmental level.

Airway Findings:

Airway exam notable for stenosis of the {site} ({pre_patent}% patent).

Moderate clear secretions bilaterally, {secretion_type} eminating from {site}.

Therapeutic Aspiration Successful therapeutic aspiration was performed to clean out the Trachea (Distal 1/3), Right Mainstem, Bronchus Intermedius, Left Mainstem, and {cleaning_target} from mucus and mucus plug.

Endobronchial Stenosis Destruction Endobronchial obstruction at {site} was treated with the following modalities:


Electrocautery: Needle Knife (EndoCut I, Effect 3, 3d/2i) used for radial cuts.

Cryotherapy: 1.7mm cryoprobe used for ablation (30sec freeze-thaw cycles).

Balloon Dilation Balloon dilation was performed at {site}.

Dilation 1: 6/7/8 Elation balloon was used to perform dilation to {balloon_1} mm at the {site}.

Total 2 inflations with dilation time of 60 seconds each.

Dilation 2: 6/7/8 Elation balloon was used to perform dilation to {balloon_2} mm at the {site}.

Total 2 inflations with dilation time of 60 seconds each.

Results Prior to treatment, affected airway was noted to be {pre_patent}% patent. After treatment, the airway was {post_patent}% patent.

The patient tolerated the procedure well. There were no immediate complications.

At the conclusion of the operation, the patient was extubated in the operating room and transported to the recovery room in stable condition.

SPECIMEN(S) None 

IMPRESSION / PLAN

[REDACTED] is a {age}-year-old {gender_long} who presents for bronchoscopy for bronchial stenosis.

{site} airway moderately stenosed again; treated with repeat dilation and touch cryotherapy.

Plan for bronchoscopy with dilation in {follow_up}.
"""

prompt_styles = [
    # Style 1: Telegraphic / Summary
    "Patient: {age}{gender_short}. Ref: {ref_physician}. Indication: Stenosis {site} ({pre_patent}%). Procedure: Bronch with Needle Knife, Cryo, Balloon ({balloon_1}mm -> {balloon_2}mm). Findings: {secretion_type}. Post-op: {post_patent}% patent. Plan: Repeat in {follow_up}.",
    
    # Style 2: Dictation
    "Write an IP op report for a {age} year old {gender_long} referred by {ref_physician}. The patient has stenosis of the {site}, only {pre_patent} percent open. We performed therapeutic aspiration for {secretion_type}, then used electrocautery needle knife and cryotherapy. We dilated twice, first to {balloon_1}mm then to {balloon_2}mm. The airway is now {post_patent} percent patent. Follow up in {follow_up}.",
    
    # Style 3: Sloppy / Quick Note
    "{age}yo {gender_short} stenosis {site}. dilated {balloon_1}-{balloon_2}mm using elation. used knife + cryo too. secretions: {secretion_type}. result {post_patent}% open. no comps. {attending}/{fellow}.",
    
    # Style 4: Billing / Technical Focus
    "CPT Codes 31645, 31630, 31641. Dx J98.09. {age} {gender_short}. Site: {site} stenosis. Interventions: Electrocautery (Needle Knife), Cryo (1.7mm), Balloon Dilation (Elation, max {balloon_2}mm). Findings: {secretion_type}, {pre_patent}% patent initially. Outcome: {post_patent}% patent.",
    
    # Style 5: Structured Request
    "Create Bronchoscopy Report:\n- Patient: {age} {gender_long}\n- Attending: {attending}\n- Target: {site} ({pre_patent}% patent)\n- Interventions: Aspiration ({secretion_type}), Needle Knife, Cryo, Balloon ({balloon_1}mm, {balloon_2}mm)\n- Outcome: {post_patent}% patent\n- Plan: Repeat {follow_up}"
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
        
        ref_physician = random.choice(data_pool["ref_physician"])
        attending = random.choice(data_pool["attending"])
        fellow = random.choice(data_pool["fellow"])
        rn_name = random.choice(data_pool["rn_name"])
        rt_name = random.choice(data_pool["rt_name"])
        
        # Site Logic
        loc_data = random.choice(data_pool["location_data"])
        site = loc_data["site"]
        cleaning_target = loc_data["cleaning_target"]
        
        pre_patent = random.choice(data_pool["pre_patent"])
        post_patent = random.choice(data_pool["post_patent"])
        secretion_type = random.choice(data_pool["secretion_type"])
        
        balloon_1 = random.choice(data_pool["balloon_size_1"])
        balloon_2 = random.choice(data_pool["balloon_size_2"])
        follow_up = random.choice(data_pool["follow_up"])
        
        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, gender_short=gender_short, gender_long=gender_long,
            ref_physician=ref_physician, attending=attending, fellow=fellow,
            site=site, pre_patent=pre_patent, post_patent=post_patent,
            secretion_type=secretion_type, balloon_1=balloon_1, balloon_2=balloon_2,
            follow_up=follow_up
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            age=age, gender_long=gender_long,
            ref_physician=ref_physician,
            attending=attending,
            fellow=fellow,
            rn_name=rn_name,
            rt_name=rt_name,
            site=site,
            cleaning_target=cleaning_target,
            pre_patent=pre_patent,
            post_patent=post_patent,
            secretion_type=secretion_type,
            balloon_1=balloon_1,
            balloon_2=balloon_2,
            follow_up=follow_up
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