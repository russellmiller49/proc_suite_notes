import json
import random
import os
import datetime

# ==========================================
# 1. CONFIGURATION
# ==========================================
# EXTRACTED FROM NOTE
NOTE_ID = "note_061" 
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
    "age": ["58", "62", "65", "68", "71", "74", "79", "83"],
    "gender_tuple": [("female", "F", "She", "Her"), ("male", "M", "He", "His")],
    "referring_doc": ["Dr. Smith", "Dr. Chen", "Dr. Williams", "Dr. Patel", "Self-referred", "Dr. Johnson"],
    "attending": ["Dr. Ingraham", "Dr. Bowers", "Dr. Miller", "Dr. Weiss"],
    "assistant": ["Dr. Lee", "Dr. Jacobs", "Dr. Fox", "Dr. Gupta"],
    "staff_rn": ["Sarah Jones", "Mike Ross", "Emily Blunt", "David Kim"],
    "staff_rt": ["Tom Cruise", "Jessica Chastain", "Chris Evans", "Anne Hathaway"],
    
    # Diagnosis Variations
    "diagnosis_tuple": [
        ("J98.09", "Other diseases of bronchus, not elsewhere classified"),
        ("J39.8", "Other specified diseases of upper respiratory tract"),
        ("C34.90", "Malignant neoplasm of unspecified part of unspecified bronchus or lung")
    ],

    # Anatomic Targets for Ablation (Logic Syncing)
    "target_location": [
        "Left Mainstem", 
        "Right Mainstem", 
        "Trachea", 
        "Bronchus Intermedius", 
        "Left Upper Lobe"
    ],

    # APC Settings
    "apc_settings": [
        {"probe": "1.5mm Straight probe", "mode": "Pulse 2", "duration": "10 seconds"},
        {"probe": "2.3mm Straight probe", "mode": "Forced 30W", "duration": "5 seconds"},
        {"probe": "1.5mm Side-fire probe", "mode": "Pulse 1", "duration": "15 seconds"},
        {"probe": "2.3mm Straight probe", "mode": "Pulse 2", "duration": "8 seconds"}
    ],

    # Follow-up Plans
    "follow_up": ["4-6 weeks", "6-8 weeks", "2-3 months", "1 month"]
}

# ==========================================
# 3. TEMPLATES
# ==========================================

note_template = """NOTE_ID: {note_id}
SOURCE_FILE: {note_id}.txt

INTERVENTIONAL PULMONOLOGY OPERATIVE REPORT

DATE OF PROCEDURE: {date_str} CC Referred Physician: {ref_doc}

INDICATION FOR OPERATION {gender_tuple[2]} is a {age}-year-old {gender_tuple[0]} who presents for bronchoscopy for stent evaluation.
The nature, purpose, risks, benefits, and alternatives to bronchoscopy were discussed with the patient in detail.
The patient indicated a wish to proceed with surgery and informed consent was signed.

CONSENT Obtained before the procedure.
Indications, potential complications, and alternatives were discussed with the patient or surrogate.
Consent was signed and witnessed by an assisting medical professional.

PREOPERATIVE DIAGNOSIS

{dx_code} {dx_text}

Airway obstruction 

POSTOPERATIVE DIAGNOSIS

{dx_code} {dx_text}

{target_loc} obstruction requiring ablation 

PROCEDURE

Flexible Therapeutic Bronchoscopy 

Therapeutic aspiration of tracheobronchial tree (initial episode) (CPT 31645) 

Destruction of tumor OR relief of stenosis by any method other than excision (APC) (CPT 31641) 

Airway stent evaluation 

ATTENDING {attending}

ASSISTANT {assistant}

SUPPORT STAFF RN: {rn_name} RT: {rt_name}

ANESTHESIA General Anesthesia 

MONITORING Pulse oximetry, heart rate, telemetry, and blood pressure were continuously monitored by an independent trained observer throughout the procedure.
INSTRUMENTATION Flexible Therapeutic Bronchoscope; APC (Argon Plasma Coagulation) system.

ESTIMATED BLOOD LOSS None 

COMPLICATIONS None 

PROCEDURE IN DETAIL

After the successful induction of anesthesia, a timeout was performed confirming the patient's name, procedure type, and procedure location.
Patient Position: Supine.

Initial Airway Inspection and Therapeutic Aspiration Successful therapeutic aspiration was performed to clean out the Right Mainstem, Bronchus Intermedius, and Left Mainstem from mucus and mucus plug.

{target_loc} Intervention (APC Ablation) Endobronchial obstruction at the {target_loc} was identified.
The obstruction was treated with the following modalities:


Modality: APC (Argon Plasma Coagulation) 


Tool: {apc_probe}


Setting/Mode: {apc_mode}


Duration: {apc_duration}

Tissue was successfully ablated.
Conclusion The patient tolerated the procedure well. There were no immediate complications.
At the conclusion of the operation, the patient was extubated in the operating room and transported to the recovery room in stable condition.
SPECIMENS

None 

IMPRESSION / PLAN

{age}-year-old {gender_tuple[1]} presented for stent evaluation.

Significant mucus plugging in Right Mainstem, Bronchus Intermedius, and Left Mainstem was cleared via therapeutic aspiration.
{target_loc} obstruction was successfully ablated using APC.


Plan: Repeat bronchoscopy in {plan_time}.
"""

# 5 Prompt Styles
prompt_styles = [
    # Style 1: Telegraphic
    "Write an IP bronch report. {age}{gender_tuple[1]}, ref {ref_doc}. Dx {dx_code}. Findings: Mucus plugging and {target_loc} obstruction. Procedure: Aspiration and APC ablation ({apc_mode}). Plan: Repeat {plan_time}.",
    
    # Style 2: Dictation
    "Please generate a bronchoscopy operative note for a {age} year old {gender_tuple[0]} referred by {ref_doc}. The patient has an airway obstruction. We performed therapeutic aspiration and APC ablation on the {target_loc} using a {apc_probe}. The patient tolerated it well.",
    
    # Style 3: Sloppy / Quick
    "{age}yo {gender_tuple[0]} stent eval. {dx_code}. suctioned airways. Used APC on {target_loc} obstruction ({apc_duration}). attending {attending}. no comps. f/u {plan_time}.",
    
    # Style 4: Billing Focus
    "Procedure codes 31645, 31641. Diagnosis {dx_code}. {age} {gender_tuple[1]}. Location of ablation: {target_loc}. Modality: APC ({apc_mode}). Impression: {target_loc} obstruction ablated, mucus cleared.",
    
    # Style 5: Structured
    "Patient: {age} {gender_tuple[1]}\nReferral: {ref_doc}\nPre-op Dx: {dx_code}\nProcedure: Flexible Bronchoscopy, Aspiration, APC\nTarget: {target_loc}\nAPC Settings: {apc_mode}, {apc_probe}\nPlan: Repeat in {plan_time}"
]

# ==========================================
# 4. GENERATOR LOGIC
# ==========================================
def generate_dataset():
    dataset = []
    
    for _ in range(NUM_SAMPLES):
        # A. Randomly select variables
        age = random.choice(data_pool["age"])
        gender_tuple = random.choice(data_pool["gender_tuple"]) # (female, F, She, Her)
        ref_doc = random.choice(data_pool["referring_doc"])
        attending = random.choice(data_pool["attending"])
        assistant = random.choice(data_pool["assistant"])
        rn_name = random.choice(data_pool["staff_rn"])
        rt_name = random.choice(data_pool["staff_rt"])
        
        # Diagnosis
        dx_tuple = random.choice(data_pool["diagnosis_tuple"])
        
        # Procedure Specifics (Logic Syncing)
        target_loc = random.choice(data_pool["target_location"])
        apc_set = random.choice(data_pool["apc_settings"])
        plan_time = random.choice(data_pool["follow_up"])
        
        # Generate a random recent date
        date_obj = datetime.date.today() - datetime.timedelta(days=random.randint(1, 365))
        date_str = date_obj.strftime("%B %d, %Y")

        # B. Generate Prompt (User Input)
        prompt_style = random.choice(prompt_styles)
        prompt = prompt_style.format(
            age=age, 
            gender_tuple=gender_tuple, 
            ref_doc=ref_doc,
            dx_code=dx_tuple[0],
            target_loc=target_loc,
            apc_mode=apc_set["mode"],
            apc_probe=apc_set["probe"],
            apc_duration=apc_set["duration"],
            plan_time=plan_time,
            attending=attending
        )
        
        # C. Generate Completion (Structured Note)
        completion = note_template.format(
            note_id=NOTE_ID,
            date_str=date_str,
            ref_doc=ref_doc,
            age=age, 
            gender_tuple=gender_tuple,
            dx_code=dx_tuple[0],
            dx_text=dx_tuple[1],
            target_loc=target_loc,
            attending=attending,
            assistant=assistant,
            rn_name=rn_name,
            rt_name=rt_name,
            apc_probe=apc_set["probe"],
            apc_mode=apc_set["mode"],
            apc_duration=apc_set["duration"],
            plan_time=plan_time
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